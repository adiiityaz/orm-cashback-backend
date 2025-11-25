from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):
    """Handle order status changes before saving"""
    if instance.pk:  # Only for existing orders
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            # Check if status changed from something else to APPROVED
            if old_instance.status != 'APPROVED' and instance.status == 'APPROVED':
                instance.approved_at = timezone.now()
        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    """Handle order status changes after saving"""
    # If order is rejected or cancelled, release the review slot
    if instance.status in ['REJECTED', 'CANCELLED'] and instance.review_slot:
        try:
            instance.review_slot.release_slot()
            logger.info(f"Review slot released for order {instance.id}")
        except Exception as e:
            logger.error(f"Error releasing review slot for order {instance.id}: {str(e)}", exc_info=True)

