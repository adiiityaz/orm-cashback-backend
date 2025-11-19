from rest_framework import serializers
from django.conf import settings
from marketplace.models import Product, ReviewSlot
from orders.models import Order
from reviews.models import Review
from payments.models import Wallet, Transaction


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model (for shop listing)"""
    brand_name = serializers.CharField(source='brand.brand_name', read_only=True)
    available_slots = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'sku', 'asin', 'price', 'currency', 
                  'main_image', 'product_url', 'review_platform', 'brand_name', 
                  'available_slots', 'is_featured', 'created_at')
        read_only_fields = ('id', 'created_at')


class ReviewSlotSerializer(serializers.ModelSerializer):
    """Serializer for ReviewSlot model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ReviewSlot
        fields = ('id', 'product', 'product_name', 'cashback_amount', 'currency', 
                  'status', 'available_slots', 'total_slots', 'min_review_rating', 
                  'review_deadline_days', 'created_at')
        read_only_fields = ('id', 'created_at', 'available_slots')


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    
    class Meta:
        model = Order
        fields = ('product', 'review_slot', 'order_id', 'order_date', 'order_amount', 
                  'currency', 'purchase_proof', 'additional_proof')
    
    def validate(self, attrs):
        """Validate order data"""
        product = attrs.get('product')
        review_slot = attrs.get('review_slot')
        
        # If review_slot is provided, ensure it belongs to the product
        if review_slot and review_slot.product != product:
            raise serializers.ValidationError({
                'review_slot': 'Review slot does not belong to the selected product.'
            })
        
        # Check if review slot is available
        if review_slot and not review_slot.is_available:
            raise serializers.ValidationError({
                'review_slot': 'This review slot is not available.'
            })
        
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    brand_name = serializers.CharField(source='product.brand.brand_name', read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'product', 'product_name', 'brand_name', 'review_slot', 
                  'order_id', 'order_date', 'order_amount', 'currency', 
                  'purchase_proof', 'additional_proof', 'status', 'rejection_reason', 
                  'is_draft', 'clicked_at', 'created_at', 'updated_at', 'approved_at')
        read_only_fields = ('id', 'status', 'rejection_reason', 'is_draft', 
                           'clicked_at', 'created_at', 'updated_at', 'approved_at')


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    
    class Meta:
        model = Review
        fields = ('order', 'rating', 'title', 'review_text', 'review_url')
    
    def validate(self, attrs):
        """Validate review data"""
        order = attrs.get('order')
        user = self.context['request'].user
        
        # Ensure order belongs to the user
        if order.user != user:
            raise serializers.ValidationError({
                'order': 'This order does not belong to you.'
            })
        
        # Ensure order is approved
        if order.status != 'APPROVED':
            raise serializers.ValidationError({
                'order': 'Order must be approved before submitting a review.'
            })
        
        # Check if review already exists for this order
        if Review.objects.filter(order=order).exists():
            raise serializers.ValidationError({
                'order': 'Review already exists for this order.'
            })
        
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'order', 'order_id', 'product', 'product_name', 'rating', 
                  'title', 'review_text', 'review_url', 'status', 'rejection_reason', 
                  'cashback_amount', 'cashback_status', 'created_at', 'updated_at', 
                  'submitted_at', 'approved_at')
        read_only_fields = ('id', 'status', 'rejection_reason', 'cashback_amount', 
                           'cashback_status', 'created_at', 'updated_at', 
                           'submitted_at', 'approved_at')


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    
    class Meta:
        model = Transaction
        fields = ('id', 'amount', 'currency', 'transaction_type', 'status', 
                  'description', 'reference_id', 'created_at', 'completed_at')
        read_only_fields = ('id', 'status', 'created_at', 'completed_at')


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet model"""
    transactions = TransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wallet
        fields = ('id', 'balance', 'currency', 'total_earned', 'total_withdrawn', 
                  'transactions', 'created_at', 'updated_at')
        read_only_fields = ('id', 'balance', 'total_earned', 'total_withdrawn', 
                           'created_at', 'updated_at')

