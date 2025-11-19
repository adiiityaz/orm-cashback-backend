from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from orders.models import Order
from reviews.models import Review
from payments.models import Wallet, Transaction
from brands.models import Brand


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
        return Response({
            'status': 'error',
            'message': 'Only admin users can access this endpoint.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get pending orders
    pending_orders = Order.objects.filter(status='PENDING').order_by('-created_at')
    
    # Get pending reviews
    pending_reviews = Review.objects.filter(status='PENDING').order_by('-created_at')
    
    from .serializers import OrderSerializer, ReviewSerializer
    
    orders_data = OrderSerializer(pending_orders, many=True, context={'request': request}).data
    reviews_data = ReviewSerializer(pending_reviews, many=True, context={'request': request}).data
    
    return Response({
        'status': 'success',
        'pending_orders': {
            'count': pending_orders.count(),
            'data': orders_data
        },
        'pending_reviews': {
            'count': pending_reviews.count(),
            'data': reviews_data
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_order(request):
    """
    Approve an order
    POST /api/admin/approve/order/
    """
    if not is_admin(request.user):
        return Response({
            'status': 'error',
            'message': 'Only admin users can approve orders.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    order_id = request.data.get('order_id')
    if not order_id:
        return Response({
            'status': 'error',
            'message': 'Order ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if order.status != 'PENDING':
        return Response({
            'status': 'error',
            'message': f'Order is already {order.status}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Approve the order
    order.status = 'APPROVED'
    order.approved_at = timezone.now()
    order.save()
    
    from .serializers import OrderSerializer
    
    return Response({
        'status': 'success',
        'message': 'Order approved successfully',
        'order': OrderSerializer(order, context={'request': request}).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_order(request):
    """
    Reject an order
    POST /api/admin/reject/order/
    """
    if not is_admin(request.user):
        return Response({
            'status': 'error',
            'message': 'Only admin users can reject orders.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    order_id = request.data.get('order_id')
    rejection_reason = request.data.get('rejection_reason', '')
    
    if not order_id:
        return Response({
            'status': 'error',
            'message': 'Order ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if order.status != 'PENDING':
        return Response({
            'status': 'error',
            'message': f'Order is already {order.status}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Reject the order
    order.status = 'REJECTED'
    order.rejection_reason = rejection_reason
    order.save()
    
    # Release review slot if exists
    if order.review_slot:
        order.review_slot.release_slot()
    
    from .serializers import OrderSerializer
    
    return Response({
        'status': 'success',
        'message': 'Order rejected successfully',
        'order': OrderSerializer(order, context={'request': request}).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_review(request):
    """
    Approve a review (triggers wallet crediting via signals)
    POST /api/admin/approve/review/
    """
    if not is_admin(request.user):
        return Response({
            'status': 'error',
            'message': 'Only admin users can approve reviews.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    review_id = request.data.get('review_id')
    if not review_id:
        return Response({
            'status': 'error',
            'message': 'Review ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Review not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if review.status != 'PENDING':
        return Response({
            'status': 'error',
            'message': f'Review is already {review.status}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Approve the review (signals will handle wallet crediting)
    review.status = 'APPROVED'
    review.approved_at = timezone.now()
    review.save()
    
    from .serializers import ReviewSerializer
    
    return Response({
        'status': 'success',
        'message': 'Review approved successfully. Wallet credited automatically.',
        'review': ReviewSerializer(review, context={'request': request}).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_review(request):
    """
    Reject a review
    POST /api/admin/reject/review/
    """
    if not is_admin(request.user):
        return Response({
            'status': 'error',
            'message': 'Only admin users can reject reviews.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    review_id = request.data.get('review_id')
    rejection_reason = request.data.get('rejection_reason', '')
    
    if not review_id:
        return Response({
            'status': 'error',
            'message': 'Review ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Review not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if review.status != 'PENDING':
        return Response({
            'status': 'error',
            'message': f'Review is already {review.status}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
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
    
    return Response({
        'status': 'success',
        'message': 'Review rejected successfully. Funds refunded to brand.',
        'review': ReviewSerializer(review, context={'request': request}).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payout(request):
    """
    Process user payout (mark as paid)
    POST /api/admin/process-payout/
    """
    if not is_admin(request.user):
        return Response({
            'status': 'error',
            'message': 'Only admin users can process payouts.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    transaction_id = request.data.get('transaction_id')
    reference_id = request.data.get('reference_id', '')
    
    if not transaction_id:
        return Response({
            'status': 'error',
            'message': 'Transaction ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        transaction = Transaction.objects.get(
            id=transaction_id,
            transaction_type='WITHDRAWAL',
            status='PENDING'
        )
    except Transaction.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Withdrawal transaction not found or already processed'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Mark transaction as completed
    transaction.status = 'COMPLETED'
    transaction.completed_at = timezone.now()
    if reference_id:
        transaction.reference_id = reference_id
    transaction.save()
    
    from .serializers import TransactionSerializer
    
    return Response({
        'status': 'success',
        'message': 'Payout processed successfully',
        'transaction': TransactionSerializer(transaction).data
    }, status=status.HTTP_200_OK)

