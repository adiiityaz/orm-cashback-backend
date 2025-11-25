from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce

from accounts.models import User
from orders.models import Order
from reviews.models import Review
from payments.models import Wallet, Transaction
from brands.models import Brand
from .utils import (
    success_response, error_response, forbidden_response,
    not_found_response, server_error_response,
    StandardResultsSetPagination
)
from .constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
import logging

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Pagination class for admin endpoints"""
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE


def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verification_queue(request):
    """
    Get all pending submissions for verification
    GET /api/admin/submissions/
    """
    if not is_admin(request.user):
        return forbidden_response('Only admin users can access this endpoint.')
    
    # Get pending orders with optimized queries
    pending_orders = Order.objects.filter(status='PENDING').select_related(
        'user', 'product', 'product__brand', 'review_slot'
    ).order_by('-created_at')
    
    # Get pending reviews with optimized queries
    pending_reviews = Review.objects.filter(status='PENDING').select_related(
        'user', 'product', 'order'
    ).order_by('-created_at')
    
    # Apply pagination
    paginator = StandardResultsSetPagination()
    
    from .serializers import OrderSerializer, ReviewSerializer
    
    paginated_orders = paginator.paginate_queryset(pending_orders, request)
    paginated_reviews = paginator.paginate_queryset(pending_reviews, request)
    
    orders_data = OrderSerializer(paginated_orders, many=True, context={'request': request}).data if paginated_orders else []
    reviews_data = ReviewSerializer(paginated_reviews, many=True, context={'request': request}).data if paginated_reviews else []
    
    return success_response({
        'pending_orders': {
            'count': pending_orders.count(),
            'next': paginator.get_next_link() if paginated_orders else None,
            'previous': paginator.get_previous_link() if paginated_orders else None,
            'data': orders_data
        },
        'pending_reviews': {
            'count': pending_reviews.count(),
            'next': paginator.get_next_link() if paginated_reviews else None,
            'previous': paginator.get_previous_link() if paginated_reviews else None,
            'data': reviews_data
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_order(request):
    """
    Approve an order
    POST /api/admin/approve/order/
    """
    if not is_admin(request.user):
        return forbidden_response('Only admin users can approve orders.')
    
    order_id = request.data.get('order_id')
    if not order_id:
        return error_response('Order ID is required')
    
    try:
        order = Order.objects.select_related('user', 'product', 'product__brand').get(id=order_id)
    except Order.DoesNotExist:
        return not_found_response('Order not found')
    
    # Verify order belongs to a valid user
    if not order.user or not order.user.is_active:
        return error_response('Invalid order')
    
    if order.status != 'PENDING':
        return error_response('Order is already processed')
    
    # Approve the order
    order.status = 'APPROVED'
    order.approved_at = timezone.now()
    order.save()
    
    logger.info(f"Order {order.id} approved by admin {request.user.id}")
    
    from .serializers import OrderSerializer
    
    return success_response({
        'order': OrderSerializer(order, context={'request': request}).data
    }, message='Order approved successfully')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_order(request):
    """
    Reject an order
    POST /api/admin/reject/order/
    """
    if not is_admin(request.user):
        return forbidden_response('Only admin users can reject orders.')
    
    order_id = request.data.get('order_id')
    rejection_reason = request.data.get('rejection_reason', '')
    
    if not order_id:
        return error_response('Order ID is required')
    
    try:
        order = Order.objects.select_related('user', 'product', 'product__brand').get(id=order_id)
    except Order.DoesNotExist:
        return not_found_response('Order not found')
    
    # Verify order belongs to a valid user
    if not order.user or not order.user.is_active:
        return error_response('Invalid order')
    
    if order.status != 'PENDING':
        return error_response('Order is already processed')
    
    # Reject the order
    order.status = 'REJECTED'
    order.rejection_reason = rejection_reason
    order.save()
    
    # Release review slot if exists
    if order.review_slot:
        order.review_slot.release_slot()
    
    from .serializers import OrderSerializer
    
    return success_response({
        'order': OrderSerializer(order, context={'request': request}).data
    }, message='Order rejected successfully')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_review(request):
    """
    Approve a review (triggers wallet crediting via signals)
    POST /api/admin/approve/review/
    """
    if not is_admin(request.user):
        return forbidden_response('Only admin users can approve reviews.')
    
    review_id = request.data.get('review_id')
    if not review_id:
        return error_response('Review ID is required')
    
    try:
        review = Review.objects.select_related('user', 'product', 'order').get(id=review_id)
    except Review.DoesNotExist:
        return not_found_response('Review not found')
    
    # Verify review belongs to a valid user
    if not review.user or not review.user.is_active:
        return error_response('Invalid review')
    
    if review.status != 'PENDING':
        return error_response('Review is already processed')
    
    # Approve the review (signals will handle wallet crediting)
    review.status = 'APPROVED'
    review.approved_at = timezone.now()
    review.save()
    
    logger.info(f"Review {review.id} approved by admin {request.user.id}")
    
    from .serializers import ReviewSerializer
    
    return success_response({
        'review': ReviewSerializer(review, context={'request': request}).data
    }, message='Review approved successfully. Wallet credited automatically.')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_review(request):
    """
    Reject a review
    POST /api/admin/reject/review/
    """
    if not is_admin(request.user):
        return forbidden_response('Only admin users can reject reviews.')
    
    review_id = request.data.get('review_id')
    rejection_reason = request.data.get('rejection_reason', '')
    
    if not review_id:
        return error_response('Review ID is required')
    
    try:
        review = Review.objects.select_related('user', 'product', 'order').get(id=review_id)
    except Review.DoesNotExist:
        return not_found_response('Review not found')
    
    # Verify review belongs to a valid user
    if not review.user or not review.user.is_active:
        return error_response('Invalid review')
    
    if review.status != 'PENDING':
        return error_response('Review is already processed')
    
    # Reject the review
    review.status = 'REJECTED'
    review.rejection_reason = rejection_reason
    review.save()
    
    # Release review slot and refund to brand
    if review.order and review.order.review_slot:
        review_slot = review.order.review_slot
        cashback_amount = review.cashback_amount or review_slot.cashback_amount
        
        # Release slot
        review_slot.release_slot()
        
        # Refund to brand's wallet
        brand = review.order.product.brand
        brand.locked_balance -= cashback_amount
        brand.wallet_balance += cashback_amount
        brand.save()
    
    from .serializers import ReviewSerializer
    
    return success_response({
        'review': ReviewSerializer(review, context={'request': request}).data
    }, message='Review rejected successfully. Funds refunded to brand.')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payout(request):
    """
    Process user payout (mark as paid)
    POST /api/admin/process-payout/
    """
    if not is_admin(request.user):
        return forbidden_response('Only admin users can process payouts.')
    
    transaction_id = request.data.get('transaction_id')
    reference_id = request.data.get('reference_id', '')
    
    if not transaction_id:
        return error_response('Transaction ID is required')
    
    try:
        transaction = Transaction.objects.get(
            id=transaction_id,
            transaction_type='WITHDRAWAL',
            status='PENDING'
        )
    except Transaction.DoesNotExist:
        return not_found_response('Withdrawal transaction not found or already processed')
    
    # Mark transaction as completed
    transaction.status = 'COMPLETED'
    transaction.completed_at = timezone.now()
    if reference_id:
        transaction.reference_id = reference_id
    transaction.save()
    
    from .serializers import TransactionSerializer
    
    return success_response({
        'transaction': TransactionSerializer(transaction).data
    }, message='Payout processed successfully')

