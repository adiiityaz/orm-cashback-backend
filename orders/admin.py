from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model"""
    
    list_display = ('order_id', 'user', 'product', 'order_amount', 'currency', 'status', 'is_draft', 'created_at')
    list_filter = ('status', 'is_draft', 'currency', 'created_at', 'approved_at')
    search_fields = ('order_id', 'user__email', 'product__name', 'product__brand__brand_name')
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'product', 'review_slot', 'order_id', 'order_date', 'order_amount', 'currency')
        }),
        ('Purchase Proof', {
            'fields': ('purchase_proof', 'additional_proof')
        }),
        ('Click Tracking', {
            'fields': ('clicked_at', 'is_draft')
        }),
        ('Status', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'approved_at')
        }),
    )
    
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'product', 'product__brand', 'review_slot')
