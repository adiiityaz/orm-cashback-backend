from django.db import models
from django.conf import settings


class Brand(models.Model):
    """Brand profile model - linked to User with BRAND role"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='brand_profile',
        limit_choices_to={'role': 'BRAND'}
    )
    brand_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='brands/logos/', blank=True, null=True)
    
    # Contact information
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True, help_text="GST registration number")
    
    # Brand status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Wallet information (for brands)
    wallet_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Main wallet balance for brand"
    )
    locked_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Locked balance for active campaigns"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.brand_name
    
    @property
    def total_products(self):
        """Get total number of products for this brand"""
        return self.products.count()
    
    @property
    def active_products(self):
        """Get number of active products for this brand"""
        return self.products.filter(is_active=True).count()
