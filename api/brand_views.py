from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from brands.models import Brand
from marketplace.models import Product, ReviewSlot
from orders.models import Order
from reviews.models import Review
from payments.models import Transaction
from .serializers import ProductSerializer, ReviewSlotSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brand_products(request):
    """
    Get list of brand's products
    GET /api/brand/products/
    """
    if not request.user.is_brand:
        return Response({
            'status': 'error',
            'message': 'Only users with BRAND role can access this endpoint.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Brand profile not found. Please create a brand profile first.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    products = Product.objects.filter(brand=brand).order_by('-created_at')
    serializer = ProductSerializer(products, many=True, context={'request': request})
    
    return Response({
        'status': 'success',
        'count': products.count(),
        'products': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    """
    Create a new product
    POST /api/brand/products/
    """
    if not request.user.is_brand:
        return Response({
            'status': 'error',
            'message': 'Only users with BRAND role can create products.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Brand profile not found. Please create a brand profile first.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        product = serializer.save(brand=brand)
        return Response({
            'status': 'success',
            'message': 'Product created successfully',
            'product': ProductSerializer(product, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_campaign(request):
    """
    Create a review campaign (review slot)
    POST /api/brand/review-slots/
    """
    if not request.user.is_brand:
        return Response({
            'status': 'error',
            'message': 'Only users with BRAND role can create campaigns.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Brand profile not found. Please create a brand profile first.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get product ID
    product_id = request.data.get('product')
    if not product_id:
        return Response({
            'status': 'error',
            'message': 'Product ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = Product.objects.get(id=product_id, brand=brand)
    except Product.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Product not found or does not belong to your brand'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Calculate total cost
    cashback_amount = Decimal(str(request.data.get('cashback_amount', 0)))
    total_slots = int(request.data.get('total_slots', 1))
    total_cost = cashback_amount * total_slots
    
    # Check if brand has enough balance
    available_balance = brand.wallet_balance - brand.locked_balance
    if available_balance < total_cost:
        return Response({
            'status': 'error',
            'message': f'Insufficient balance. Required: {total_cost}, Available: {available_balance}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create review slot
    serializer = ReviewSlotSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        review_slot = serializer.save(product=product)
        
        # Lock the balance
        brand.locked_balance += total_cost
        brand.save()
        
        return Response({
            'status': 'success',
            'message': 'Campaign created successfully',
            'campaign': ReviewSlotSerializer(review_slot, context={'request': request}).data,
            'locked_balance': str(brand.locked_balance)
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brand_stats(request):
    """
    Get brand dashboard statistics
    GET /api/brand/stats/
    """
    if not request.user.is_brand:
        return Response({
            'status': 'error',
            'message': 'Only users with BRAND role can access this endpoint.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Brand profile not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get all products for this brand
    products = Product.objects.filter(brand=brand)
    product_ids = products.values_list('id', flat=True)
    
    # Calculate statistics
    total_products = products.count()
    active_products = products.filter(is_active=True).count()
    
    # Get all review slots for brand's products
    review_slots = ReviewSlot.objects.filter(product__brand=brand)
    total_slots = review_slots.aggregate(total=Sum('total_slots'))['total'] or 0
    reserved_slots = review_slots.aggregate(total=Sum('reserved_slots'))['total'] or 0
    available_slots = total_slots - reserved_slots
    
    # Get orders for brand's products
    orders = Order.objects.filter(product__brand=brand)
    total_orders = orders.count()
    approved_orders = orders.filter(status='APPROVED').count()
    pending_orders = orders.filter(status='PENDING').count()
    
    # Get reviews for brand's products
    reviews = Review.objects.filter(product__brand=brand)
    total_reviews = reviews.count()
    approved_reviews = reviews.filter(status='APPROVED').count()
    
    # Calculate total spent (from locked balance + completed campaigns)
    total_spent = brand.locked_balance + Transaction.objects.filter(
        order__product__brand=brand,
        transaction_type='CREDIT',
        status='COMPLETED'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    return Response({
        'status': 'success',
        'stats': {
            'wallet_balance': str(brand.wallet_balance),
            'locked_balance': str(brand.locked_balance),
            'available_balance': str(brand.wallet_balance - brand.locked_balance),
            'currency': brand.currency,
            'total_products': total_products,
            'active_products': active_products,
            'total_slots': total_slots,
            'reserved_slots': reserved_slots,
            'available_slots': available_slots,
            'total_orders': total_orders,
            'approved_orders': approved_orders,
            'pending_orders': pending_orders,
            'total_reviews': total_reviews,
            'approved_reviews': approved_reviews,
            'reviews_acquired': approved_reviews,
            'total_spent': str(total_spent),
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_funds(request):
    """
    Generate payment order for adding funds (Razorpay integration)
    POST /api/brand/add-funds/
    """
    if not request.user.is_brand:
        return Response({
            'status': 'error',
            'message': 'Only users with BRAND role can add funds.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    amount = request.data.get('amount')
    if not amount or Decimal(str(amount)) <= 0:
        return Response({
            'status': 'error',
            'message': 'Valid amount is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Brand profile not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # In production, integrate with Razorpay here
    # For now, return a mock order ID
    import uuid
    order_id = f"order_{uuid.uuid4().hex[:16]}"
    
    # In production, create Razorpay order:
    # razorpay_order = razorpay_client.order.create({
    #     'amount': int(Decimal(str(amount)) * 100),  # Amount in paise
    #     'currency': 'INR',
    #     'notes': {
    #         'brand_user_id': request.user.id
    #     }
    # })
    
    return Response({
        'status': 'success',
        'message': 'Payment order created',
        'order_id': order_id,
        'amount': str(amount),
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
        'note': 'In production, this will integrate with Razorpay. Webhook will update wallet balance.'
    }, status=status.HTTP_200_OK)

