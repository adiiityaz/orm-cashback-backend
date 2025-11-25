from django.urls import path, include
from . import views
from . import user_views
from . import brand_views
from . import admin_views
from . import upload_views
from . import payment_views

app_name = 'api'

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    
    # Authentication endpoints
    path('auth/', include('accounts.urls')),
    
    # User endpoints
    path('shop/products/', user_views.shop_products, name='shop_products'),
    path('user/track/', user_views.track_click, name='track_click'),
    path('user/orders/', user_views.submit_order, name='submit_order'),
    path('user/orders/list/', user_views.user_orders, name='user_orders'),
    path('user/reviews/', user_views.submit_review, name='submit_review'),
    path('user/reviews/list/', user_views.user_reviews, name='user_reviews'),
    path('user/wallet/', user_views.user_wallet, name='user_wallet'),
    
    # Brand endpoints
    path('brand/products/', brand_views.brand_products, name='brand_products'),
    path('brand/products/create/', brand_views.create_product, name='create_product'),
    path('brand/products/<int:product_id>/', brand_views.update_product, name='update_product'),
    path('brand/review-slots/', brand_views.create_campaign, name='create_campaign'),
    path('brand/stats/', brand_views.brand_stats, name='brand_stats'),
    path('brand/add-funds/', brand_views.add_funds, name='add_funds'),
    
    # Admin endpoints
    path('admin/submissions/', admin_views.verification_queue, name='verification_queue'),
    path('admin/approve/order/', admin_views.approve_order, name='approve_order'),
    path('admin/reject/order/', admin_views.reject_order, name='reject_order'),
    path('admin/approve/review/', admin_views.approve_review, name='approve_review'),
    path('admin/reject/review/', admin_views.reject_review, name='reject_review'),
    path('admin/process-payout/', admin_views.process_payout, name='process_payout'),
    
    # File upload endpoint
    path('upload/', upload_views.upload_file, name='upload_file'),
    
    # Payment webhook
    path('payment/webhook/razorpay/', payment_views.razorpay_webhook, name='razorpay_webhook'),
]

