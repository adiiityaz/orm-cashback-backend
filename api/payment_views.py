from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from brands.models import Brand
from payments.models import Transaction
from django.conf import settings
from decimal import Decimal
import json
import hmac
import hashlib


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def razorpay_webhook(request):
    """
    Handle Razorpay payment webhook
    POST /api/payment/webhook/razorpay/
    """
    # Get webhook signature from headers
    webhook_signature = request.headers.get('X-Razorpay-Signature', '')
    webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
    
    # Verify webhook signature (in production)
    if webhook_secret:
        payload = request.body
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(webhook_signature, expected_signature):
            return Response({
                'status': 'error',
                'message': 'Invalid signature'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Parse webhook payload
    try:
        payload = json.loads(request.body)
        event = payload.get('event')
        payment_data = payload.get('payload', {}).get('payment', {}).get('entity', {})
        
        # Handle payment success
        if event == 'payment.captured':
            order_id = payment_data.get('order_id', '')
            amount = Decimal(str(payment_data.get('amount', 0))) / 100  # Razorpay amounts are in paise
            payment_id = payment_data.get('id', '')
            
            # Extract brand user ID from order notes or metadata
            notes = payment_data.get('notes', {})
            brand_user_id = notes.get('brand_user_id')
            
            if brand_user_id:
                try:
                    brand = Brand.objects.get(user_id=brand_user_id)
                    # Add funds to brand wallet
                    brand.wallet_balance += amount
                    brand.save()
                    
                    # Note: Transaction model requires wallet (User wallet only)
                    # For brand payments, we just update brand wallet_balance
                    # Transaction records are for user wallets only
                    
                    return Response({
                        'status': 'success',
                        'message': 'Payment processed successfully'
                    }, status=status.HTTP_200_OK)
                except Brand.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': 'Brand not found'
                    }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'status': 'success',
            'message': 'Webhook received'
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'status': 'error',
            'message': 'Invalid JSON payload'
        }, status=status.HTTP_400_BAD_REQUEST)

