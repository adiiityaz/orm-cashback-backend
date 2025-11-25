from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
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
from .utils import (
    success_response, error_response, forbidden_response,
    StandardResultsSetPagination
)
from .constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, RECENT_TRANSACTIONS_LIMIT
from .services.product_service import ProductService
import logging

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Pagination class for user endpoints"""
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shop_products(request):
    """
    Get list of products available for reviews
    
    GET /api/shop/products/
    
    Returns:
        Response: List of available products with pagination
    """
    if not request.user.is_user:
        return forbidden_response('Only users with USER role can access this endpoint.')
    
    try:
        # Use service layer for business logic
        products = ProductService.get_available_products_for_user(request.user)
        
        # Filter by platform if provided
        platform = request.GET.get('platform')
        if platform and platform in ['AMAZON', 'FLIPKART', 'SHOPIFY', 'OTHER']:
            products = [p for p in products if p.review_platform == platform]
        
        serializer = ProductSerializer(products, many=True, context={'request': request})
        
        return success_response({
            'count': len(products),
            'products': serializer.data,
            'platform_filter': platform if platform else None
        })
    except Exception as e:
        logger.error(f"Error fetching shop products: {str(e)}", exc_info=True)
        return error_response('Failed to fetch products', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_click(request):
    """
    Track when user clicks "Buy Now" (creates draft submission)
    POST /api/user/track/
    """
    if not request.user.is_user:
        return forbidden_response('Only users with USER role can track clicks.')
    
    product_id = request.data.get('product_id')
    review_slot_id = request.data.get('review_slot_id')
    
    if not product_id:
        return error_response('Product ID is required')
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return error_response('Product not found', status_code=status.HTTP_404_NOT_FOUND)
    
    review_slot = None
    if review_slot_id:
        try:
            review_slot = ReviewSlot.objects.get(
                id=review_slot_id,
                product=product,
                status='OPEN'
            )
        except ReviewSlot.DoesNotExist:
            return error_response('Review slot not found or not available', status_code=status.HTTP_404_NOT_FOUND)
    
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
    
    return success_response({
        'draft_order': OrderSerializer(draft_order, context={'request': request}).data
    }, message='Click tracked. Draft order created.', status_code=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_order(request):
    """
    Submit purchase proof (order)
    POST /api/user/orders/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return forbidden_response('Only users with USER role can submit orders.')
    
    serializer = OrderCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Create order with current user
        order = serializer.save(user=request.user, status='PENDING', is_draft=False)
        
        # If review slot is provided, reserve it
        if order.review_slot:
            order.review_slot.reserve_slot()
        
        response_serializer = OrderSerializer(order, context={'request': request})
        
        return success_response({
            'order': response_serializer.data
        }, message='Order submitted successfully. Waiting for approval.', status_code=status.HTTP_201_CREATED)
    
    return error_response('Invalid order data', errors=serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    """
    Get list of user's orders
    GET /api/user/orders/list/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return forbidden_response('Only users with USER role can view orders.')
    
    orders = Order.objects.filter(user=request.user).select_related(
        'product', 'product__brand', 'review_slot'
    ).order_by('-created_at')
    
    # Apply pagination
    paginator = StandardResultsSetPagination()
    paginated_orders = paginator.paginate_queryset(orders, request)
    serializer = OrderSerializer(paginated_orders, many=True, context={'request': request}) if paginated_orders else OrderSerializer([], many=True)
    
    return paginator.get_paginated_response({
        'status': 'success',
        'orders': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request):
    """
    Submit review + review URL
    POST /api/user/reviews/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return forbidden_response('Only users with USER role can submit reviews.')
    
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
        
        return success_response({
            'review': response_serializer.data
        }, message='Review submitted successfully. Waiting for approval.', status_code=status.HTTP_201_CREATED)
    
    return error_response('Invalid review data', errors=serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reviews(request):
    """
    Get list of user's reviews
    GET /api/user/reviews/list/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return forbidden_response('Only users with USER role can view reviews.')
    
    reviews = Review.objects.filter(user=request.user).select_related(
        'product', 'order', 'order__product'
    ).order_by('-created_at')
    
    # Apply pagination
    paginator = StandardResultsSetPagination()
    paginated_reviews = paginator.paginate_queryset(reviews, request)
    serializer = ReviewSerializer(paginated_reviews, many=True, context={'request': request}) if paginated_reviews else ReviewSerializer([], many=True)
    
    return paginator.get_paginated_response({
        'status': 'success',
        'reviews': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_wallet(request):
    """
    Get user wallet & cashback tracking
    GET /api/user/wallet/
    """
    # Ensure user has USER role
    if not request.user.is_user:
        return forbidden_response('Only users with USER role can view wallet.')
    
    # Get or create wallet for user
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Get recent transactions
    transactions = wallet.transactions.all().order_by('-created_at')[:RECENT_TRANSACTIONS_LIMIT]
    
    serializer = WalletSerializer(wallet, context={'request': request})
    
    return success_response({
        'wallet': serializer.data
    })
