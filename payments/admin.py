from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Admin configuration for Wallet model"""
    
    list_display = ('user', 'balance', 'currency', 'total_earned', 'total_withdrawn', 'created_at')
    list_filter = ('currency', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'total_earned', 'total_withdrawn')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Balance Information', {
            'fields': ('balance', 'currency')
        }),
        ('Statistics', {
            'fields': ('total_earned', 'total_withdrawn')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for Transaction model"""
    
    list_display = ('id', 'wallet', 'amount', 'currency', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'currency', 'created_at', 'completed_at')
    search_fields = ('wallet__user__email', 'description', 'reference_id', 'review__review_url')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('wallet', 'amount', 'currency', 'transaction_type', 'status')
        }),
        ('Related Objects', {
            'fields': ('review', 'order')
        }),
        ('Metadata', {
            'fields': ('description', 'reference_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('wallet', 'wallet__user', 'review', 'order')
