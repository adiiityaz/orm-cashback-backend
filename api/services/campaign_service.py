"""
Campaign service for handling review campaign operations
"""
from decimal import Decimal, InvalidOperation
from django.db import transaction
from brands.models import Brand
from marketplace.models import Product, ReviewSlot
from api.constants import DEFAULT_CURRENCY
import logging

logger = logging.getLogger(__name__)


class CampaignService:
    """Service for campaign-related operations"""
    
    @staticmethod
    def validate_campaign_data(
        cashback_amount: Decimal,
        total_slots: int,
        brand: Brand
    ) -> tuple[bool, str, Decimal]:
        """
        Validate campaign creation data
        
        Args:
            cashback_amount: Cashback amount per review
            total_slots: Total number of review slots
            brand: Brand instance
            
        Returns:
            tuple: (is_valid, error_message, total_cost)
        """
        if cashback_amount <= 0:
            return False, 'Cashback amount must be greater than 0', Decimal('0')
        
        if total_slots <= 0:
            return False, 'Total slots must be greater than 0', Decimal('0')
        
        total_cost = cashback_amount * total_slots
        available_balance = brand.wallet_balance - brand.locked_balance
        
        if available_balance < total_cost:
            return False, 'Insufficient balance', total_cost
        
        return True, '', total_cost
    
    @staticmethod
    @transaction.atomic
    def create_campaign(
        product: Product,
        brand: Brand,
        cashback_amount: Decimal,
        total_slots: int,
        **campaign_data
    ) -> ReviewSlot:
        """
        Create a review campaign (review slot) with balance locking
        
        Args:
            product: Product instance
            brand: Brand instance
            cashback_amount: Cashback amount per review
            total_slots: Total number of slots
            **campaign_data: Additional campaign data
            
        Returns:
            ReviewSlot: Created review slot instance
        """
        total_cost = cashback_amount * total_slots
        
        # Create review slot
        review_slot = ReviewSlot.objects.create(
            product=product,
            cashback_amount=cashback_amount,
            total_slots=total_slots,
            currency=campaign_data.get('currency', DEFAULT_CURRENCY),
            status='OPEN',
            **{k: v for k, v in campaign_data.items() if k not in ['currency']}
        )
        
        # Lock the balance atomically
        brand.locked_balance += total_cost
        brand.save()
        
        logger.info(f"Campaign created: ReviewSlot {review_slot.id}, Brand {brand.id}, Locked: {total_cost}")
        
        return review_slot

