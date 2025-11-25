from django.db import models
from django.db import transaction
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Wallet(models.Model):
    """Wallet model - represents user's cashback wallet"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        limit_choices_to={'role': 'USER'}
    )
    
    # Balance information
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Current wallet balance"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Total statistics
    total_earned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total cashback earned (all time)"
    )
    total_withdrawn = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount withdrawn (all time)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Wallet - {self.user.email} - {self.currency} {self.balance}"
    
    def add_balance(self, amount, transaction_type='CREDIT'):
        """Add balance to wallet and create transaction"""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        with transaction.atomic():
            self.balance += amount
            if transaction_type == 'CREDIT':
                self.total_earned += amount
            self.save()
            
            # Create transaction record
            Transaction.objects.create(
                wallet=self,
                amount=amount,
                transaction_type=transaction_type,
                status='COMPLETED'
            )
        
        logger.info(f"Balance added to wallet {self.id}: {amount}, Type: {transaction_type}")
    
    def deduct_balance(self, amount, transaction_type='DEBIT'):
        """Deduct balance from wallet and create transaction"""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        
        with transaction.atomic():
            self.balance -= amount
            if transaction_type == 'WITHDRAWAL':
                self.total_withdrawn += amount
            self.save()
            
            # Create transaction record
            Transaction.objects.create(
                wallet=self,
                amount=amount,
                transaction_type=transaction_type,
                status='COMPLETED'
            )
        
        logger.info(f"Balance deducted from wallet {self.id}: {amount}, Type: {transaction_type}")


class Transaction(models.Model):
    """Transaction model - represents all wallet transactions"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('CREDIT', 'Credit (Cashback)'),
        ('DEBIT', 'Debit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('REFUND', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    # Transaction details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='USD')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Related objects
    review = models.ForeignKey(
        'reviews.Review',
        on_delete=models.SET_NULL,
        related_name='transactions',
        null=True,
        blank=True,
        help_text="Review that generated this transaction (if applicable)"
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        related_name='transactions',
        null=True,
        blank=True,
        help_text="Order related to this transaction (if applicable)"
    )
    
    # Transaction metadata
    description = models.TextField(blank=True, help_text="Transaction description or notes")
    reference_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="External reference ID (payment gateway, etc.)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'transaction_type']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['review', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.currency} {self.amount} - {self.wallet.user.email}"
    
    @property
    def is_credit(self):
        """Check if transaction is a credit"""
        return self.transaction_type == 'CREDIT'
    
    @property
    def is_debit(self):
        """Check if transaction is a debit"""
        return self.transaction_type in ['DEBIT', 'WITHDRAWAL']
