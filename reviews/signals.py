from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Review
from api.services.wallet_service import WalletService
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Review)
def review_pre_save(sender, instance, **kwargs):
    """Handle review status changes before saving"""
    if instance.pk:  # Only for existing reviews
        try:
            old_instance = Review.objects.get(pk=instance.pk)
            # Check if status changed from something else to APPROVED
            if old_instance.status != 'APPROVED' and instance.status == 'APPROVED':
                instance.approved_at = timezone.now()
        except Review.DoesNotExist:
            pass


@receiver(post_save, sender=Review)
def review_post_save(sender, instance, created, **kwargs):
    """Automatically credit wallet when review is approved"""
    # Only process if review is approved and cashback hasn't been processed
    if instance.status == 'APPROVED' and instance.cashback_status == 'PENDING':
        try:
            # Get or create wallet for the user
            currency = instance.order.currency if instance.order else 'USD'
            wallet, wallet_created = Wallet.objects.get_or_create(
                user=instance.user,
                defaults={'currency': currency}
            )
            
            # Only process if cashback amount is greater than 0
            if instance.cashback_amount and instance.cashback_amount > 0:
                # Use service layer for wallet operations
                success = WalletService.credit_wallet_for_review(instance)
                
                if success:
                    # Update review cashback status
                    instance.cashback_status = 'PROCESSED'
                    # Use update to avoid triggering signal again
                    Review.objects.filter(pk=instance.pk).update(
                        cashback_status='PROCESSED'
                    )
                    logger.info(f"Cashback processed for review {instance.id}, Amount: {instance.cashback_amount}")
                else:
                    # Mark cashback as failed if there's an error
                    instance.cashback_status = 'FAILED'
                    Review.objects.filter(pk=instance.pk).update(
                        cashback_status='FAILED'
                    )
                    logger.error(f"Failed to process cashback for review {instance.id}")
        
        except Exception as e:
            # Handle any errors gracefully
            logger.error(f"Error in review_post_save signal for review {instance.id}: {str(e)}", exc_info=True)

