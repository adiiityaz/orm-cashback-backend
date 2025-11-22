# User Credentials for ORM Cashback Platform

## 🔐 Login Credentials

### 1. **ADMIN USER** (Superuser)
- **Email:** `admin@ormcashback.com`
- **Password:** `Admin@123`
- **Role:** Admin/Superuser
- **Access:** Full admin access to Django admin panel and all API endpoints
- **Login URL:** 
  - Admin Panel: http://127.0.0.1:8000/admin/
  - API Login: http://127.0.0.1:8000/api/auth/login/

---

### 2. **SHOPPER USER** (Regular User)
- **Email:** `shopper@ormcashback.com`
- **Password:** `Shopper@123`
- **Role:** USER
- **Access:** 
  - Browse products
  - Create orders
  - Submit reviews
  - View wallet balance
- **Login URL:** http://127.0.0.1:8000/api/auth/login/

---

### 3. **BRAND USER** (Brand Owner)
- **Email:** `brand@ormcashback.com`
- **Password:** `Brand@123`
- **Role:** BRAND
- **Access:**
  - Create products
  - Create review campaigns
  - View brand statistics
  - Manage wallet (add funds)
- **Brand Profile:**
  - Brand Name: Test Brand
  - Wallet Balance: $1000.00
  - Status: Verified & Active
- **Login URL:** http://127.0.0.1:8000/api/auth/login/

---

## 📝 How to Use

### For Admin Panel:
1. Visit: http://127.0.0.1:8000/admin/
2. Login with admin credentials
3. Manage all users, products, orders, reviews, etc.

### For API Testing (Postman/Thunder Client):
1. **Login Endpoint:** `POST /api/auth/login/`
   ```json
   {
     "email": "shopper@ormcashback.com",
     "password": "Shopper@123"
   }
   ```
2. **Response:** You'll get access and refresh tokens
3. **Use Token:** Add to headers: `Authorization: Bearer <access_token>`

---

## 🔄 Recreate Users

If you need to recreate these users, run:
```bash
python manage.py create_test_users
```

**Note:** The command will skip users that already exist, so it's safe to run multiple times.

---

## ⚠️ Security Note

These are test credentials. **Change passwords in production!**

---

## 📋 Quick Test Flow

1. **Login as Shopper:**
   - Get JWT token from `/api/auth/login/`
   - Browse products: `GET /api/shop/products/`
   - Create order: `POST /api/user/orders/`

2. **Login as Brand:**
   - Get JWT token from `/api/auth/login/`
   - Create product: `POST /api/brand/products/`
   - Create campaign: `POST /api/brand/review-slots/`

3. **Login as Admin:**
   - Access admin panel
   - Approve orders: `/api/admin/orders/{id}/approve/`
   - Approve reviews: `/api/admin/reviews/{id}/approve/`

---

**Created:** $(date)
**Platform:** ORM Cashback Backend
**Version:** 1.0

