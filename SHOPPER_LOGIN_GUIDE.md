# How to Login as Shopper User

## 🔐 Shopper Credentials
- **Email:** `shopper@ormcashback.com`
- **Password:** `Shopper@123`

---

## Method 1: Using Postman (Recommended)

### Step 1: Open Postman
1. Open Postman application
2. Create a new request

### Step 2: Configure Login Request
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/auth/login/`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "email": "shopper@ormcashback.com",
    "password": "Shopper@123"
  }
  ```

### Step 3: Send Request
Click "Send" button

### Step 4: Get Response
You'll receive a response like:
```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": 2,
    "email": "shopper@ormcashback.com",
    "first_name": "John",
    "last_name": "Shopper",
    "role": "USER"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Step 5: Use Access Token
Copy the `access` token and use it in subsequent API calls:
- **Header Name:** `Authorization`
- **Header Value:** `Bearer <access_token>`

Example:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Method 2: Using cURL (Command Line)

### Windows PowerShell:
```powershell
$body = @{
    email = "shopper@ormcashback.com"
    password = "Shopper@123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login/" -Method POST -Body $body -ContentType "application/json"
$response | ConvertTo-Json
```

### Linux/Mac Terminal:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "shopper@ormcashback.com",
    "password": "Shopper@123"
  }'
```

---

## Method 3: Using Python Requests

```python
import requests

# Login endpoint
url = "http://127.0.0.1:8000/api/auth/login/"

# Login data
data = {
    "email": "shopper@ormcashback.com",
    "password": "Shopper@123"
}

# Send login request
response = requests.post(url, json=data)

# Get response
result = response.json()
print(result)

# Extract access token
access_token = result['tokens']['access']
print(f"\nAccess Token: {access_token}")

# Use token for authenticated requests
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Example: Get user wallet
wallet_url = "http://127.0.0.1:8000/api/user/wallet/"
wallet_response = requests.get(wallet_url, headers=headers)
print(wallet_response.json())
```

---

## Method 4: Using Thunder Client (VS Code Extension)

1. Install Thunder Client extension in VS Code
2. Create new request:
   - **Method:** POST
   - **URL:** `http://127.0.0.1:8000/api/auth/login/`
   - **Body:** JSON
     ```json
     {
       "email": "shopper@ormcashback.com",
       "password": "Shopper@123"
     }
     ```
3. Send request
4. Copy the `access` token from response
5. Use it in subsequent requests as: `Authorization: Bearer <token>`

---

## 📋 After Login - What You Can Do

Once logged in, you can use these endpoints with your access token:

### 1. Browse Products
```
GET http://127.0.0.1:8000/api/shop/products/
Headers: Authorization: Bearer <access_token>
```

### 2. Track Click (Before Purchase)
```
POST http://127.0.0.1:8000/api/user/track/
Headers: Authorization: Bearer <access_token>
Body: {
  "product_id": 1
}
```

### 3. Submit Order
```
POST http://127.0.0.1:8000/api/user/orders/
Headers: Authorization: Bearer <access_token>
Body: {
  "product_id": 1,
  "order_id": "ORD123456",
  "order_amount": 99.99,
  ...
}
```

### 4. View Your Orders
```
GET http://127.0.0.1:8000/api/user/orders/list/
Headers: Authorization: Bearer <access_token>
```

### 5. Submit Review
```
POST http://127.0.0.1:8000/api/user/reviews/
Headers: Authorization: Bearer <access_token>
Body: {
  "order_id": 1,
  "rating": 5,
  "review_text": "Great product!",
  ...
}
```

### 6. View Wallet
```
GET http://127.0.0.1:8000/api/user/wallet/
Headers: Authorization: Bearer <access_token>
```

### 7. Get Current User Info
```
GET http://127.0.0.1:8000/api/auth/me/
Headers: Authorization: Bearer <access_token>
```

---

## 🔄 Refresh Token

If your access token expires, use the refresh token:

```
POST http://127.0.0.1:8000/api/auth/token/refresh/
Body: {
  "refresh": "<refresh_token>"
}
```

Response:
```json
{
  "access": "new_access_token_here"
}
```

---

## ⚠️ Important Notes

1. **Access Token Expiry:** Access tokens expire after 60 minutes (default)
2. **Refresh Token Expiry:** Refresh tokens expire after 7 days
3. **Always Include Token:** All protected endpoints require the `Authorization: Bearer <token>` header
4. **Server Must Be Running:** Make sure Django server is running on `http://127.0.0.1:8000`

---

## 🧪 Quick Test

Test if login works:

```powershell
# PowerShell
$body = @{
    email = "shopper@ormcashback.com"
    password = "Shopper@123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login/" -Method POST -Body $body -ContentType "application/json"
```

If successful, you'll see the tokens in the response!

---

**Need Help?** Check `API_DOCUMENTATION.md` for full API details.

