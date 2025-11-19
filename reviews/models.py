from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """Review model - represents user reviews submitted for products"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        limit_choices_to={'role': 'USER'}
    )
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='review',
        help_text="Order associated with this review"
    )
    product = models.ForeignKey(
        'marketplace.Product',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    # Review details
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField(help_text="The actual review content")
    review_url = models.URLField(
        help_text="URL of the review on the platform (Amazon, Flipkart, etc.)"
    )
    
    # Review status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for rejection if review is rejected"
    )
    
    # Cashback information
    cashback_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Cashback amount earned from this review"
    )
    cashback_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSED', 'Processed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['product', 'status']),
            models.Index(fields=['status', 'rating']),
        ]
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name} - {self.rating} stars"
    
    @property
    def is_pending(self):
        """Check if review is pending approval"""
        return self.status == 'PENDING'
    
    @property
    def is_approved(self):
        """Check if review is approved"""
        return self.status == 'APPROVED'
    
    @property
    def is_rejected(self):
        """Check if review is rejected"""
        return self.status == 'REJECTED'
