"""
Wallet service for handling wallet operations
"""
from decimal import Decimal
from django.db import transaction
from payments.models import Wallet, Transaction
from reviews.models import Review
import logging

logger = logging.getLogger(__name__)


class WalletService:
    """Service for wallet-related operations"""
    
    @staticmethod
    @transaction.atomic
    def credit_wallet_for_review(review: Review) -> bool:
        """
        Credit wallet when review is approved
        
        Args:
            review: Review instance that was approved
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            currency = review.order.currency if review.order else 'USD'
            wallet, _ = Wallet.objects.get_or_create(
                user=review.user,
                defaults={'currency': currency}
            )
            
            if review.cashback_amount and review.cashback_amount > 0:
                wallet.balance += review.cashback_amount
                wallet.total_earned += review.cashback_amount
                wallet.save()
                
                Transaction.objects.create(
                    wallet=wallet,
                    amount=review.cashback_amount,
                    currency=currency,
                    transaction_type='CREDIT',
                    status='COMPLETED',
                    review=review,
                    order=review.order,
                    description=f"Cashback for approved review: {review.product.name}",
                )
                
                logger.info(f"Wallet credited: User {review.user.id}, Amount: {review.cashback_amount}")
                return True
        except Exception as e:
            logger.error(f"Error crediting wallet for review {review.id}: {str(e)}", exc_info=True)
            return False
        
        return False

