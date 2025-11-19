# ORM Cashback API Documentation

## Base URL
```
http://127.0.0.1:8000/api/
```

## Authentication

All protected endpoints require JWT authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## 🔐 Authentication Endpoints

### 1. Register User
**POST** `/api/auth/register/`

Register a new user (USER or BRAND role).

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "password2": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "role": "USER"  // or "BRAND"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "USER"
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  }
}
```

---

### 2. Login
**POST** `/api/auth/login/`

Login and get JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "USER"
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  }
}
```

---

### 3. Refresh Token
**POST** `/api/auth/token/refresh/`

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh": "refresh_token_here"
}
```

**Response (200 OK):**
```json
{
  "access": "new_access_token_here"
}
```

---

### 4. Get Current User
**GET** `/api/auth/me/`

Get current logged-in user details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "role": "USER",
    "is_active": true,
    "date_joined": "2025-01-01T00:00:00Z",
    "last_login": "2025-01-01T12:00:00Z"
  }
}
```

---

## 👤 User Endpoints (Require USER Role)

### 5. Get Shop Products
**GET** `/api/shop/products/`

Get list of products available for reviews (filters out completed campaigns).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 10,
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "description": "Product description",
      "price": "99.99",
      "currency": "USD",
      "main_image": "/media/products/main/image.jpg",
      "product_url": "https://example.com/product",
      "review_platform": "AMAZON",
      "brand_name": "Brand Name",
      "available_slots": 5,
      "is_featured": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 6. Track Click
**POST** `/api/user/track/`

Track when user clicks "Buy Now" (creates draft submission).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "product_id": 1,
  "review_slot_id": 1
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Click tracked. Draft order created.",
  "draft_order": {...}
}
```

---

### 7. Submit Order
**POST** `/api/user/orders/`

Submit purchase proof (order).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `product`: Product ID (integer)
- `review_slot`: Review Slot ID (integer, optional)
- `order_id`: Order ID from platform (string)
- `order_date`: Order date (YYYY-MM-DD)
- `order_amount`: Order amount (decimal)
- `currency`: Currency code (string, default: "USD")
- `purchase_proof`: Purchase proof image (file)
- `additional_proof`: Additional proof image (file, optional)

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Order submitted successfully. Waiting for approval.",
  "order": {
    "id": 1,
    "product": 1,
    "product_name": "Product Name",
    "brand_name": "Brand Name",
    "order_id": "ORD123456",
    "order_date": "2025-01-01",
    "order_amount": "99.99",
    "currency": "USD",
    "status": "PENDING",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

---

### 8. Get User Orders
**GET** `/api/user/orders/list/`

Get list of user's orders.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 5,
  "orders": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Product Name",
      "brand_name": "Brand Name",
      "order_id": "ORD123456",
      "order_date": "2025-01-01",
      "order_amount": "99.99",
      "currency": "USD",
      "status": "APPROVED",
      "created_at": "2025-01-01T00:00:00Z",
      "approved_at": "2025-01-01T01:00:00Z"
    }
  ]
}
```

---

### 9. Submit Review
**POST** `/api/user/reviews/`

Submit review + review URL.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "order": 1,
  "rating": 5,
  "title": "Great Product!",
  "review_text": "This product exceeded my expectations...",
  "review_url": "https://amazon.com/review/12345"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Review submitted successfully. Waiting for approval.",
  "review": {
    "id": 1,
    "order": 1,
    "order_id": "ORD123456",
    "product": 1,
    "product_name": "Product Name",
    "rating": 5,
    "title": "Great Product!",
    "review_text": "This product exceeded my expectations...",
    "review_url": "https://amazon.com/review/12345",
    "status": "PENDING",
    "cashback_amount": "10.00",
    "cashback_status": "PENDING",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

---

### 10. Get User Reviews
**GET** `/api/user/reviews/list/`

Get list of user's reviews.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 3,
  "reviews": [
    {
      "id": 1,
      "order": 1,
      "order_id": "ORD123456",
      "product": 1,
      "product_name": "Product Name",
      "rating": 5,
      "title": "Great Product!",
      "review_text": "This product exceeded my expectations...",
      "review_url": "https://amazon.com/review/12345",
      "status": "APPROVED",
      "cashback_amount": "10.00",
      "cashback_status": "PROCESSED",
      "created_at": "2025-01-01T00:00:00Z",
      "approved_at": "2025-01-01T02:00:00Z"
    }
  ]
}
```

---

### 11. Get User Wallet
**GET** `/api/user/wallet/`

Get wallet & cashback tracking.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "wallet": {
    "id": 1,
    "balance": "50.00",
    "currency": "USD",
    "total_earned": "100.00",
    "total_withdrawn": "50.00",
    "transactions": [
      {
        "id": 1,
        "amount": "10.00",
        "currency": "USD",
        "transaction_type": "CREDIT",
        "status": "COMPLETED",
        "description": "Cashback for approved review: Product Name",
        "created_at": "2025-01-01T00:00:00Z",
        "completed_at": "2025-01-01T00:00:00Z"
      }
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

---

## 🏥 Health Check

### 25. Health Check
**GET** `/api/health/`

Check if API is running (public endpoint, no authentication required).

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "ORM Cashback API is running",
  "version": "1.0.0"
}
```

---

---

## 🏢 Brand Endpoints (Require BRAND Role)

### 12. Get Brand Products
**GET** `/api/brand/products/`

Get list of brand's products.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 5,
  "products": [...]
}
```

---

### 13. Create Product
**POST** `/api/brand/products/create/`

Create a new product.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `name`: Product name (required)
- `description`: Product description (required)
- `sku`: SKU (optional)
- `asin`: ASIN (optional)
- `price`: Product price (required)
- `currency`: Currency code (default: "USD")
- `main_image`: Product image (file, optional)
- `product_url`: Product URL (required)
- `review_platform`: AMAZON/FLIPKART/SHOPIFY/OTHER (required)

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Product created successfully",
  "product": {...}
}
```

---

### 14. Create Campaign (Review Slot)
**POST** `/api/brand/review-slots/`

Create a review campaign. Validates wallet balance and locks funds.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "product": 1,
  "cashback_amount": "10.00",
  "currency": "USD",
  "total_slots": 10,
  "min_review_rating": 3,
  "review_deadline_days": 7
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Campaign created successfully",
  "campaign": {...},
  "locked_balance": "100.00"
}
```

---

### 15. Get Brand Stats
**GET** `/api/brand/stats/`

Get brand dashboard statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "stats": {
    "wallet_balance": "1000.00",
    "locked_balance": "500.00",
    "available_balance": "500.00",
    "currency": "USD",
    "total_products": 10,
    "active_products": 8,
    "total_slots": 50,
    "reserved_slots": 20,
    "available_slots": 30,
    "total_orders": 25,
    "approved_orders": 20,
    "pending_orders": 5,
    "total_reviews": 18,
    "approved_reviews": 15,
    "reviews_acquired": 15,
    "total_spent": "150.00"
  }
}
```

---

### 16. Add Funds (Payment Gateway)
**POST** `/api/brand/add-funds/`

Generate payment order for adding funds (Razorpay integration).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "amount": "1000.00"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Payment order created",
  "order_id": "order_abc123",
  "amount": "1000.00",
  "razorpay_key_id": "rzp_test_xxx"
}
```

---

## 👑 Admin Endpoints (Require Admin/Staff Role)

### 17. Verification Queue
**GET** `/api/admin/submissions/`

Get all pending submissions for verification.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "pending_orders": {
    "count": 5,
    "data": [...]
  },
  "pending_reviews": {
    "count": 3,
    "data": [...]
  }
}
```

---

### 18. Approve Order
**POST** `/api/admin/approve/order/`

Approve an order.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "order_id": 1
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Order approved successfully",
  "order": {...}
}
```

---

### 19. Reject Order
**POST** `/api/admin/reject/order/`

Reject an order and release review slot.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "order_id": 1,
  "rejection_reason": "Invalid purchase proof"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Order rejected successfully",
  "order": {...}
}
```

---

### 20. Approve Review
**POST** `/api/admin/approve/review/`

Approve a review (automatically credits wallet via signals).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "review_id": 1
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Review approved successfully. Wallet credited automatically.",
  "review": {...}
}
```

---

### 21. Reject Review
**POST** `/api/admin/reject/review/`

Reject a review and refund to brand.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "review_id": 1,
  "rejection_reason": "Review does not meet requirements"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Review rejected successfully. Funds refunded to brand.",
  "review": {...}
}
```

---

### 22. Process Payout
**POST** `/api/admin/process-payout/`

Process user payout (mark withdrawal as paid).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "transaction_id": 1,
  "reference_id": "TXN123456"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Payout processed successfully",
  "transaction": {...}
}
```

---

## 📤 File Upload

### 23. Upload File
**POST** `/api/upload/`

Upload image file and get public URL.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `file`: Image file (required, max 10MB)

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "file_url": "/media/uploads/20250101_120000_image.jpg",
  "file_path": "uploads/20250101_120000_image.jpg",
  "file_size": 1024000,
  "content_type": "image/jpeg"
}
```

---

## 💳 Payment Webhook

### 24. Razorpay Webhook
**POST** `/api/payment/webhook/razorpay/`

Handle Razorpay payment webhook (public endpoint, signature verified).

**Note:** This endpoint is called by Razorpay when payment is successful. It automatically updates brand wallet balance.

---

## 📊 API Documentation

Interactive API documentation is available at:
```
http://127.0.0.1:8000/api/docs/
```

---

## 🔒 Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "status": "error",
  "message": "Only users with USER role can access this endpoint."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## 📝 Notes

- All timestamps are in UTC
- All monetary values are in decimal format (string)
- Image uploads use multipart/form-data
- JWT access tokens expire after 60 minutes
- JWT refresh tokens expire after 7 days
- Wallet is automatically credited when review is approved (via signals)

