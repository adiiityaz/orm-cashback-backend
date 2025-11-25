from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.conf import settings
from brands.models import Brand
from payments.models import Transaction
from decimal import Decimal, InvalidOperation
from .utils import success_response, error_response, server_error_response, not_found_response
from .constants import RAZORPAY_AMOUNT_DIVISOR
import json
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def razorpay_webhook(request):
    """
    Handle Razorpay payment webhook
    POST /api/payment/webhook/razorpay/
    """
    # IP whitelist check (optional but recommended)
    allowed_ips = getattr(settings, 'RAZORPAY_WEBHOOK_IPS', [])
    if allowed_ips:
        client_ip = request.META.get('REMOTE_ADDR')
        if client_ip not in allowed_ips:
            logger.warning(f"Webhook request from unauthorized IP: {client_ip}")
            return error_response('Unauthorized', status_code=status.HTTP_403_FORBIDDEN)
    
    # Get webhook signature from headers
    webhook_signature = request.headers.get('X-Razorpay-Signature', '')
    webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
    
    # Verify webhook signature (required in production)
    if not webhook_secret:
        logger.error("RAZORPAY_WEBHOOK_SECRET not configured")
        return server_error_response('Webhook configuration error')
    
    payload = request.body
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(webhook_signature, expected_signature):
        logger.warning("Invalid webhook signature")
        return error_response('Invalid signature', status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Parse webhook payload
    try:
        payload = json.loads(request.body)
        event = payload.get('event')
        payment_data = payload.get('payload', {}).get('payment', {}).get('entity', {})
        
        # Handle payment success
        if event == 'payment.captured':
            order_id = payment_data.get('order_id', '')
            payment_id = payment_data.get('id', '')
            
            # Validate and convert amount
            try:
                amount_paise = Decimal(str(payment_data.get('amount', 0)))
                if amount_paise <= 0:
                    raise ValueError("Invalid amount")
                amount = amount_paise / RAZORPAY_AMOUNT_DIVISOR  # Razorpay amounts are in paise
            except (ValueError, InvalidOperation, TypeError) as e:
                logger.error(f"Invalid amount in webhook: {str(e)}")
                return error_response('Invalid payment amount')
            
            # Extract brand user ID from order notes or metadata
            notes = payment_data.get('notes', {})
            brand_user_id = notes.get('brand_user_id')
            
            if brand_user_id:
                try:
                    with transaction.atomic():
                        brand = Brand.objects.select_for_update().get(user_id=brand_user_id)
                        # Add funds to brand wallet atomically
                        brand.wallet_balance += amount
                        brand.save()
                        
                        logger.info(f"Payment processed: {payment_id}, Brand: {brand.id}, Amount: {amount}")
                        
                        return success_response(message='Payment processed successfully')
                except Brand.DoesNotExist:
                    logger.error(f"Brand not found for user_id: {brand_user_id}")
                    return not_found_response('Brand not found')
                except Exception as e:
                    logger.error(f"Error processing payment webhook: {str(e)}", exc_info=True)
                    return server_error_response('Payment processing failed')
        
        return success_response(message='Webhook received')
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook payload: {str(e)}")
        return error_response('Invalid JSON payload')
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {str(e)}", exc_info=True)
        return server_error_response('Webhook processing failed')

