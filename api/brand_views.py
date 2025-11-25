from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import Coalesce
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from brands.models import Brand
from marketplace.models import Product, ReviewSlot
from orders.models import Order
from reviews.models import Review
from payments.models import Transaction
from .serializers import ProductSerializer, ReviewSlotSerializer
from .utils import (
    success_response, error_response, forbidden_response,
    not_found_response, server_error_response
)
from .constants import DEFAULT_CURRENCY
from .services.campaign_service import CampaignService
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brand_products(request):
    """
    Get list of brand's products
    GET /api/brand/products/
    """
    if not request.user.is_brand:
        return forbidden_response('Only users with BRAND role can access this endpoint.')
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return not_found_response('Brand profile not found. Please create a brand profile first.')
    
    products = Product.objects.filter(brand=brand).select_related('brand').order_by('-created_at')
    serializer = ProductSerializer(products, many=True, context={'request': request})
    
        return success_response({
            'count': products.count(),
            'products': serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    """
    Create a new product
    POST /api/brand/products/create/
    """
    if not request.user.is_brand:
        return forbidden_response('Only users with BRAND role can create products.')
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return not_found_response('Brand profile not found. Please create a brand profile first.')
    
    serializer = ProductSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        product = serializer.save(brand=brand)
        return success_response({
            'product': ProductSerializer(product, context={'request': request}).data
        }, message='Product created successfully', status_code=status.HTTP_201_CREATED)
    
    return error_response('Invalid product data', errors=serializer.errors)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_product(request, product_id):
    """
    Update product details
    PATCH /api/brand/products/{id}/
    """
    if not request.user.is_brand:
        return forbidden_response('Only users with BRAND role can update products.')
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return not_found_response('Brand profile not found. Please create a brand profile first.')
    
    try:
        product = Product.objects.get(id=product_id, brand=brand)
    except Product.DoesNotExist:
        return not_found_response('Product not found or does not belong to your brand')
    
    serializer = ProductSerializer(
        product, 
        data=request.data, 
        partial=True, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        logger.info(f"Product {product.id} updated by brand {brand.id}")
        return success_response({
            'product': serializer.data
        }, message='Product updated successfully')
    
    return error_response('Invalid product data', errors=serializer.errors)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_campaign(request):
    """
    Create a review campaign (review slot)
    POST /api/brand/review-slots/
    """
    if not request.user.is_brand:
        return forbidden_response('Only users with BRAND role can create campaigns.')
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return not_found_response('Brand profile not found. Please create a brand profile first.')
    
    # Get product ID
    product_id = request.data.get('product')
    if not product_id:
        return error_response('Product ID is required')
    
    try:
        product = Product.objects.get(id=product_id, brand=brand)
    except Product.DoesNotExist:
        return not_found_response('Product not found or does not belong to your brand')
    
    # Validate campaign data using service layer
    try:
        cashback_amount = Decimal(str(request.data.get('cashback_amount', 0)))
        total_slots = int(request.data.get('total_slots', 1))
        
        is_valid, error_msg, total_cost = CampaignService.validate_campaign_data(
            cashback_amount, total_slots, brand
        )
        
        if not is_valid:
            return error_response(error_msg)
        
    except (ValueError, InvalidOperation, TypeError) as e:
        logger.error(f"Invalid input in create_campaign: {str(e)}")
        return error_response('Invalid input data')
    
    # Create review slot with transaction using service layer
    serializer = ReviewSlotSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            campaign_data = serializer.validated_data
            review_slot = CampaignService.create_campaign(
                product=product,
                brand=brand,
                cashback_amount=cashback_amount,
                total_slots=total_slots,
                **campaign_data
            )
            
            return success_response({
                'campaign': ReviewSlotSerializer(review_slot, context={'request': request}).data,
                'locked_balance': str(brand.locked_balance)
            }, message='Campaign created successfully', status_code=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}", exc_info=True)
            return server_error_response('Failed to create campaign')
    
    return error_response('Invalid campaign data', errors=serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brand_stats(request):
    """
    Get brand dashboard statistics
    GET /api/brand/stats/
    """
    if not request.user.is_brand:
        return forbidden_response('Only users with BRAND role can access this endpoint.')
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return not_found_response('Brand profile not found.')
    
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
    
    # Calculate sentiment breakdown (only for approved reviews)
    approved_reviews_queryset = reviews.filter(status='APPROVED')
    positive_reviews = approved_reviews_queryset.filter(rating__gte=4).count()
    neutral_reviews = approved_reviews_queryset.filter(rating=3).count()
    negative_reviews = approved_reviews_queryset.filter(rating__lte=2).count()
    
    # Calculate average rating
    rating_agg = approved_reviews_queryset.aggregate(
        avg_rating=Avg('rating')
    )
    avg_rating = rating_agg['avg_rating'] if rating_agg['avg_rating'] else 0
    
    # Reviews by rating breakdown
    reviews_by_rating = {}
    for rating in range(1, 6):
        reviews_by_rating[str(rating)] = approved_reviews_queryset.filter(rating=rating).count()
    
    # Calculate total spent (from locked balance + completed campaigns)
    total_spent = brand.locked_balance + Transaction.objects.filter(
        order__product__brand=brand,
        transaction_type='CREDIT',
        status='COMPLETED'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    return success_response({
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
            'sentiment_breakdown': {
                'positive_reviews': positive_reviews,
                'neutral_reviews': neutral_reviews,
                'negative_reviews': negative_reviews,
                'average_rating': round(float(avg_rating), 2) if avg_rating else 0
            },
            'reviews_by_rating': reviews_by_rating
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_funds(request):
    """
    Generate payment order for adding funds (Razorpay integration)
    POST /api/brand/add-funds/
    """
    if not request.user.is_brand:
        return forbidden_response('Only users with BRAND role can add funds.')
    
    amount = request.data.get('amount')
    if not amount or Decimal(str(amount)) <= 0:
        return error_response('Valid amount is required')
    
    try:
        brand = request.user.brand_profile
    except Brand.DoesNotExist:
        return not_found_response('Brand profile not found.')
    
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
    
    return success_response({
        'order_id': order_id,
        'amount': str(amount),
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
    }, message='Payment order created')

