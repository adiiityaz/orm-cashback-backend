from django.contrib import admin
from .models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model"""
    
    list_display = ('brand_name', 'user', 'is_verified', 'is_active', 'wallet_balance', 'locked_balance', 'total_products', 'created_at')
    list_filter = ('is_verified', 'is_active', 'created_at')
    search_fields = ('brand_name', 'user__email', 'user__first_name', 'user__last_name', 'gst_number')
    readonly_fields = ('created_at', 'updated_at', 'total_products', 'active_products')
    
    fieldsets = (
        ('Brand Information', {
            'fields': ('user', 'brand_name', 'description', 'logo')
        }),
        ('Contact Information', {
            'fields': ('website', 'contact_email', 'contact_phone', 'gst_number')
        }),
        ('Wallet Information', {
            'fields': ('wallet_balance', 'locked_balance', 'currency')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Statistics', {
            'fields': ('total_products', 'active_products')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    ordering = ('-created_at',)
