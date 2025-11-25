from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model"""
    
    list_display = ('id', 'user', 'product', 'rating', 'status', 'cashback_amount', 'cashback_status', 'created_at')
    list_filter = ('status', 'rating', 'cashback_status', 'created_at', 'approved_at')
    search_fields = ('user__email', 'product__name', 'product__brand__brand_name', 'title', 'review_text', 'review_url')
    readonly_fields = ('created_at', 'updated_at', 'submitted_at', 'approved_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'order', 'product', 'rating', 'title', 'review_text', 'review_url')
        }),
        ('Cashback Information', {
            'fields': ('cashback_amount', 'cashback_status')
        }),
        ('Status', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at', 'approved_at')
        }),
    )
    
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'product', 'product__brand', 'order')
