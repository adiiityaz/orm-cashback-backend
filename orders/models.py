from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Order(models.Model):
    """Order model - represents purchase proof submitted by users"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role': 'USER'}
    )
    product = models.ForeignKey(
        'marketplace.Product',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    review_slot = models.ForeignKey(
        'marketplace.ReviewSlot',
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True
    )
    
    # Order details
    order_id = models.CharField(max_length=200, help_text="Order ID from the purchase platform")
    order_date = models.DateField(help_text="Date when the order was placed")
    order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total amount of the order"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Purchase proof
    purchase_proof = models.ImageField(
        upload_to='orders/proofs/',
        help_text="Screenshot or image of purchase confirmation"
    )
    additional_proof = models.ImageField(
        upload_to='orders/proofs/',
        blank=True,
        null=True,
        help_text="Additional proof if needed"
    )
    
    # Click tracking
    clicked_at = models.DateTimeField(blank=True, null=True, help_text="When user clicked 'Buy Now'")
    is_draft = models.BooleanField(default=False, help_text="Draft submission before proof upload")
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for rejection if order is rejected"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['product', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_id} - {self.user.email} - {self.product.name}"
    
    @property
    def is_pending(self):
        """Check if order is pending approval"""
        return self.status == 'PENDING'
    
    @property
    def is_approved(self):
        """Check if order is approved"""
        return self.status == 'APPROVED'
    
    @property
    def is_rejected(self):
        """Check if order is rejected"""
        return self.status == 'REJECTED'
