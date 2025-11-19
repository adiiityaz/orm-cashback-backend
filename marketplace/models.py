from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Product(models.Model):
    """Product model - linked to Brand"""
    
    brand = models.ForeignKey(
        'brands.Brand',
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    asin = models.CharField(max_length=50, blank=True, null=True, help_text="Amazon Standard Identification Number")
    
    # Product details
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Product images
    main_image = models.ImageField(upload_to='products/main/', blank=True, null=True)
    additional_images = models.JSONField(default=list, blank=True)
    
    # Product links
    product_url = models.URLField(help_text="Link to product on brand's website/store")
    review_platform = models.CharField(
        max_length=50,
        choices=[
            ('AMAZON', 'Amazon'),
            ('FLIPKART', 'Flipkart'),
            ('SHOPIFY', 'Shopify Store'),
            ('OTHER', 'Other'),
        ],
        default='OTHER'
    )
    
    # Product status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.brand.brand_name}"
    
    @property
    def available_slots(self):
        """Get number of available review slots for this product"""
        return self.review_slots.filter(status='OPEN').count()
    
    @property
    def total_slots(self):
        """Get total number of review slots for this product"""
        return self.review_slots.count()


class ReviewSlot(models.Model):
    """Review Slot model - represents available review opportunities for products"""
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('RESERVED', 'Reserved'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='review_slots'
    )
    
    # Slot details
    cashback_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cashback amount for completing this review"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Slot status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    # Requirements
    min_review_rating = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Minimum rating required for review"
    )
    review_deadline_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1)],
        help_text="Number of days user has to submit review after order approval"
    )
    
    # Slot limits
    total_slots = models.PositiveIntegerField(
        default=1,
        help_text="Total number of slots available"
    )
    reserved_slots = models.PositiveIntegerField(
        default=0,
        help_text="Number of slots currently reserved"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Review Slot'
        verbose_name_plural = 'Review Slots'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'status']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.get_status_display()} ({self.available_slots}/{self.total_slots})"
    
    @property
    def available_slots(self):
        """Calculate available slots"""
        return max(0, self.total_slots - self.reserved_slots)
    
    @property
    def is_available(self):
        """Check if slot is available for reservation"""
        return self.status == 'OPEN' and self.available_slots > 0
    
    def reserve_slot(self):
        """Reserve one slot"""
        if self.is_available:
            self.reserved_slots += 1
            if self.reserved_slots >= self.total_slots:
                self.status = 'RESERVED'
            self.save()
            return True
        return False
    
    def release_slot(self):
        """Release one slot"""
        if self.reserved_slots > 0:
            self.reserved_slots -= 1
            if self.status == 'RESERVED' and self.reserved_slots < self.total_slots:
                self.status = 'OPEN'
            self.save()
            return True
        return False
