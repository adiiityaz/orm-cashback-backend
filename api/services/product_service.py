"""
Product service for handling product-related operations
"""
from django.db.models import Prefetch, Q
from marketplace.models import Product, ReviewSlot
from orders.models import Order
from reviews.models import Review
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """Service for product-related operations"""
    
    @staticmethod
    def get_available_products_for_user(user: User):
        """
        Get products available for user to review (optimized query)
        
        Args:
            user: User instance
            
        Returns:
            QuerySet: Products with available slots that user hasn't completed
        """
        # Optimize query with select_related and prefetch_related
        products = Product.objects.filter(
            is_active=True
        ).select_related('brand').prefetch_related(
            Prefetch(
                'review_slots',
                queryset=ReviewSlot.objects.filter(status='OPEN'),
                to_attr='open_slots'
            )
        ).distinct()
        
        # Pre-fetch user's completed reviews to avoid N+1
        user_completed_product_ids = Review.objects.filter(
            user=user,
            status='APPROVED'
        ).values_list('product_id', flat=True).distinct()
        
        # Filter products that have open slots and user hasn't completed
        available_products = []
        for product in products:
            if hasattr(product, 'open_slots') and len(product.open_slots) > 0:
                if product.id not in user_completed_product_ids:
                    available_products.append(product)
        
        return available_products

