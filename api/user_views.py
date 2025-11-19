from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from marketplace.models import Product, ReviewSlot
from orders.models import Order
from reviews.models import Review
from payments.models import Wallet
from .serializers import (
    ProductSerializer, ReviewSlotSerializer, OrderCreateSerializer, 
    OrderSerializer, ReviewCreateSerializer, ReviewSerializer, WalletSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shop_products(request):
    """
    Get list of products available for reviews
    GET /api/shop/products/
    """
    # Only show active products with available review slots
    products = Product.objects.filter(
        is_active=True
    ).prefetch_related('review_slots').distinct()
    
    # Filter products that have at least one open review slot
    products_with_slots = []
    user = request.user
    
    for product in products:
        if product.review_slots.filter(status='OPEN').exists():
            # Filter out products user has already completed
            completed_orders = Order.objects.filter(
                user=user,
                product=product,
                status='APPROVED'
            )
            # Check if user has submitted a review for any approved order
            has_completed = Review.objects.filter(
                user=user,
                product=product,
                order__in=completed_orders,
                status='APPROVED'
            ).exists()
            
            if not has_completed:
                products_with_slots.append(product)
    
    serializer = ProductSerializer(products_with_slots, many=True, context={'request': request})
    
    return Response({
        'status': 'success',
        'count': len(products_with_slots),
        'products': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_click(request):
    """
    Track when user clicks "Buy Now" (creates draft submission)
    POST /api/user/track/
    """
    if not request.user.is_user:
        return Response({
            'status': 'error',
            'message': 'Only users with USER role can track clicks.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    product_id = request.data.get('product_id')
    review_slot_id = request.data.get('review_slot_id')
    
    if not product_id:
        return Response({
            'status': 'error',
            'message': 'Product ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    review_slot = None
    if review_slot_id:
        try:
            review_slot = ReviewSlot.objects.get(
                id=review_slot_id,
                product=product,
                status='OPEN'
            )
        except ReviewSlot.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Review slot not found or not available'
            }, status=status.HTTP_404_NOT_FOUND)
    
    # Create draft order
    draft_order = Order.objects.create(
        user=request.user,
        product=product,
        review_slot=review_slot,
        order_id=f"DRAFT_{timezone.now().timestamp()}",
        order_date=timezone.now().date(),
        order_amount=product.price,
        currency=product.currency,
        purchase_proof=None,  # Will be uploaded later
        status='PENDING',
        is_draft=True,
        clicked_at=timezone.now()
    )
    
    from .serializers import OrderSerializer
    
    return Response({
        'status': 'success',
        'message': 'Click tracked. Draft order created.',
        'draft_order': OrderSerializer(draft_order, context={'request': request}).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_order(request):
    """
    Submit purchase proof (order)
    POST /api/user/orders/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return Response({
            'status': 'error',
            'message': 'Only users with USER role can submit orders.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = OrderCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Create order with current user
        order = serializer.save(user=request.user, status='PENDING', is_draft=False)
        
        # If review slot is provided, reserve it
        if order.review_slot:
            order.review_slot.reserve_slot()
        
        response_serializer = OrderSerializer(order, context={'request': request})
        
        return Response({
            'status': 'success',
            'message': 'Order submitted successfully. Waiting for approval.',
            'order': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    """
    Get list of user's orders
    GET /api/user/orders/list/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return Response({
            'status': 'error',
            'message': 'Only users with USER role can view orders.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True, context={'request': request})
    
    return Response({
        'status': 'success',
        'count': orders.count(),
        'orders': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request):
    """
    Submit review + review URL
    POST /api/user/reviews/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return Response({
            'status': 'error',
            'message': 'Only users with USER role can submit reviews.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Create review with current user
        order = serializer.validated_data['order']
        review = serializer.save(
            user=request.user,
            product=order.product,
            status='PENDING',
            submitted_at=timezone.now()
        )
        
        # Set cashback amount from review slot if available
        if order.review_slot:
            review.cashback_amount = order.review_slot.cashback_amount
            review.save()
        
        response_serializer = ReviewSerializer(review, context={'request': request})
        
        return Response({
            'status': 'success',
            'message': 'Review submitted successfully. Waiting for approval.',
            'review': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reviews(request):
    """
    Get list of user's reviews
    GET /api/user/reviews/list/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return Response({
            'status': 'error',
            'message': 'Only users with USER role can view reviews.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True, context={'request': request})
    
    return Response({
        'status': 'success',
        'count': reviews.count(),
        'reviews': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_wallet(request):
    """
    Get user wallet & cashback tracking
    GET /api/user/wallet/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return Response({
            'status': 'error',
            'message': 'Only users with USER role can view wallet.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get or create wallet for user
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Get recent transactions (last 20)
    transactions = wallet.transactions.all().order_by('-created_at')[:20]
    
    serializer = WalletSerializer(wallet, context={'request': request})
    
    return Response({
        'status': 'success',
        'wallet': serializer.data
    }, status=status.HTTP_200_OK)
