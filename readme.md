# 🚀 ORM Cashback & Review Platform (Backend)

A web application that allows D2C brands to improve their online reputation by offering cashback for real product reviews. Users can submit purchase proof, write reviews, and receive cashback, while brands manage campaigns through their dashboard.

This repository contains the backend implementation built using **Django + Django REST Framework + PostgreSQL** and tested using Postman.

**🔗 Repository:** [https://github.com/adiiityaz/orm-cashback-backend](https://github.com/adiiityaz/orm-cashback-backend)

---

## 📌 Features

### 🔐 Authentication (JWT Based)
- User Registration (USER / BRAND roles)
- Login & Token Generation
- Token Refresh
- Get Current User Details (`/api/auth/me/`)

### 🏢 Brand Dashboard API
- Create & manage products
- Create review campaigns ("review slots")
- Track orders submitted by users
- View reviews submitted by users
- View brand statistics
- Manage wallet & add funds

### 👤 User Dashboard API
- View products available for reviews
- Track "Buy Now" clicks
- Submit purchase proof (order)
- Submit review + review URL
- Wallet & Cashback tracking
- View order history

### 🧾 Admin Features
- Approve/reject orders
- Approve/reject reviews (automatic wallet crediting)
- View verification queue (pending orders & reviews)
- Process payouts
- View all users, orders & transactions

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python |
| **Framework** | Django + DRF (Django REST Framework) |
| **Database** | PostgreSQL / SQLite (Development) |
| **Auth** | JWT (Simple JWT) |
| **Testing** | Postman |
| **Optional** | Celery + Redis (for background tasks) |

---

## 📂 Project Structure

```
orm_cashback/
│
├── orm_cashback/          # Main project (settings, urls)
├── accounts/              # User model (with roles)
├── brands/                # Brand profile & storefronts
├── marketplace/           # Products & review slots
├── orders/                # Orders submitted by users
├── reviews/               # User reviews & approval
├── payments/              # Wallet & transactions
└── api/                   # API routing (views & urls)
```

---

## ⚙️ Installation & Setup

### 🔹 1. Clone the Repository

```bash
git clone https://github.com/adiiityaz/orm-cashback-backend.git
cd orm-cashback-backend
```

### 🔹 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 🔹 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- Django>=4.2.0
- djangorestframework>=3.14.0
- psycopg2-binary>=2.9.0
- django-cors-headers>=4.0.0
- djangorestframework-simplejwt>=5.2.0
- Pillow>=10.0.0 (for image handling)
- python-dotenv>=1.0.0 (for environment variables)

### 🔹 4. Setup Database

#### Option A: PostgreSQL (Production)

Create a database:
- **DB Name:** `orm_db`
- **User:** `orm_user`
- **Password:** `your_password`
- **Port:** `5432`

Add this to `settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "orm_db",
        "USER": "orm_user",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

#### Option B: SQLite (Development - Default)

SQLite is configured by default for easy development. **No setup required!**

### 🔹 5. Environment Variables (Optional)

Create a `.env` file in the project root (see `.env.example`):

```bash
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@localhost:5432/orm_db
```

> **Note:** For development, you can skip this step as defaults are provided.

### 🔹 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 🔹 7. Create Test Users (Recommended)

Create admin, shopper, and brand users automatically:

```bash
python manage.py create_test_users
```

This will create:
- **Admin:** `admin@ormcashback.com` / `Admin@123`
- **Shopper:** `shopper@ormcashback.com` / `Shopper@123`
- **Brand:** `brand@ormcashback.com` / `Brand@123`

📄 See [USER_CREDENTIALS.md](USER_CREDENTIALS.md) for details.

**OR** create a superuser manually:

```bash
python manage.py createsuperuser
```

### 🔹 8. Run Server

```bash
python manage.py runserver
```

**Visit:**
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API Base:** http://127.0.0.1:8000/api/
- **Health Check:** http://127.0.0.1:8000/api/health/

---

## 🧪 API Testing

### Using Postman/Thunder Client

1. **Login Endpoint:** `POST /api/auth/login/`
   ```json
   {
     "email": "shopper@ormcashback.com",
     "password": "Shopper@123"
   }
   ```

2. **Get Access Token** from response

3. **Add to Headers:** `Authorization: Bearer <access_token>`

### 📚 Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[SHOPPER_LOGIN_GUIDE.md](SHOPPER_LOGIN_GUIDE.md)** - Detailed login guide
- **[USER_CREDENTIALS.md](USER_CREDENTIALS.md)** - Test user credentials

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register USER / BRAND |
| POST | `/api/auth/login/` | Get JWT Token |
| POST | `/api/auth/token/refresh/` | Refresh Access Token |
| GET | `/api/auth/me/` | Get logged-in user info |

> **All protected endpoints require:**
> ```
> Authorization: Bearer <access_token>
> ```

---

## 🧾 API Endpoints

### 👤 USER Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/shop/products/` | Browse available products |
| POST | `/api/user/track/` | Track "Buy Now" click |
| POST | `/api/user/orders/` | Submit order with purchase proof |
| GET | `/api/user/orders/list/` | View my orders |
| POST | `/api/user/reviews/` | Submit review |
| GET | `/api/user/reviews/list/` | View my reviews |
| GET | `/api/user/wallet/` | View wallet balance |

### 🏢 BRAND Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/brand/products/` | View my products |
| POST | `/api/brand/products/create/` | Create product |
| POST | `/api/brand/review-slots/` | Create review campaign |
| GET | `/api/brand/stats/` | View brand statistics |
| POST | `/api/brand/add-funds/` | Add funds to wallet |

### 👑 ADMIN Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/submissions/` | View verification queue |
| POST | `/api/admin/approve/order/` | Approve order |
| POST | `/api/admin/reject/order/` | Reject order |
| POST | `/api/admin/approve/review/` | Approve review (auto-credits wallet) |
| POST | `/api/admin/reject/review/` | Reject review |
| POST | `/api/admin/process-payout/` | Process payout |

---

## 📅 Development Roadmap

| Day | Tasks | Status |
|-----|-------|--------|
| Day 1 | Setup Django, DB, apps | ✅ Complete |
| Day 2 | Custom User Model (roles) | ✅ Complete |
| Day 3 | Brand + Product + ReviewSlot models | ✅ Complete |
| Day 4 | Orders + Reviews + Wallet models | ✅ Complete |
| Day 5 | DRF setup + first API | ✅ Complete |
| Day 6 | JWT Auth | ✅ Complete |
| Day 7 | Brand APIs | ✅ Complete |
| Day 8 | User APIs | ✅ Complete |
| Day 9 | Wallet automation (signals) | ✅ Complete |
| Day 10 | Testing + API Docs + GitHub push | ✅ Complete |

---

## 🚀 Quick Start

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install: `pip install -r requirements.txt`
5. Migrate: `python manage.py migrate`
6. Create users: `python manage.py create_test_users`
7. Run: `python manage.py runserver`
8. Login: http://127.0.0.1:8000/api/auth/login/

---

## 📚 Additional Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[USER_CREDENTIALS.md](USER_CREDENTIALS.md)** - Test user credentials
- **[SHOPPER_LOGIN_GUIDE.md](SHOPPER_LOGIN_GUIDE.md)** - Detailed login guide
- **[PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md)** - Project completion checklist
- **[PHASE_COMPARISON.md](PHASE_COMPARISON.md)** - Feature comparison

---

## 📝 License

This project is part of the ORM Cashback Platform backend implementation.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**⭐ If you find this project helpful, please give it a star!**
