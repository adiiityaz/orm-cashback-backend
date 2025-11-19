from django.contrib import admin
from .models import Product, ReviewSlot


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model"""
    
    list_display = ('name', 'brand', 'price', 'currency', 'is_active', 'is_featured', 'available_slots', 'created_at')
    list_filter = ('is_active', 'is_featured', 'review_platform', 'brand', 'created_at')
    search_fields = ('name', 'sku', 'asin', 'brand__brand_name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'available_slots', 'total_slots')
    
    fieldsets = (
        ('Product Information', {
            'fields': ('brand', 'name', 'description', 'sku', 'asin')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Images', {
            'fields': ('main_image', 'additional_images')
        }),
        ('Product Links', {
            'fields': ('product_url', 'review_platform')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('available_slots', 'total_slots')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(ReviewSlot)
class ReviewSlotAdmin(admin.ModelAdmin):
    """Admin configuration for ReviewSlot model"""
    
    list_display = ('product', 'cashback_amount', 'currency', 'status', 'available_slots', 'total_slots', 'created_at')
    list_filter = ('status', 'currency', 'created_at', 'expires_at')
    search_fields = ('product__name', 'product__brand__brand_name')
    readonly_fields = ('created_at', 'updated_at', 'available_slots')
    
    fieldsets = (
        ('Slot Information', {
            'fields': ('product', 'cashback_amount', 'currency')
        }),
        ('Status', {
            'fields': ('status', 'total_slots', 'reserved_slots', 'available_slots')
        }),
        ('Requirements', {
            'fields': ('min_review_rating', 'review_deadline_days')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'expires_at')
        }),
    )
    
    ordering = ('-created_at',)
