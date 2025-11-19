🚀 ORM Cashback & Review Platform (Backend)

A web application that allows D2C brands to improve their online reputation by offering cashback for real product reviews.
Users can submit purchase proof, write reviews, and receive cashback, while brands manage campaigns through their dashboard.

This repository contains the backend implementation built using Django + Django REST Framework + PostgreSQL and tested using Postman.

📌 Features (Backend)
🔐 Authentication (JWT Based)

User Registration (USER / BRAND roles)

Login & Token Generation

Get Current User Details (/auth/me/)

🏢 Brand Dashboard API

Create & manage products

Create review campaigns (“review slots”)

Track orders submitted by users

View reviews submitted by users

👤 User Dashboard API

View products available for reviews

Submit purchase proof (order)

Submit review + review URL

Wallet & Cashback tracking

🧾 Admin Features (Future)

Approve/reject reviews

View all users, orders & transactions

Fraud detection & flagging

🛠 Tech Stack
Layer	Technology
Language	Python
Framework	Django + DRF (Django REST Framework)
Database	PostgreSQL
Auth	JWT (Simple JWT)
Testing	Postman
Optional	Celery + Redis (for background tasks)
📂 Project Structure
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

⚙️ Installation & Setup
🔹 1. Clone the Repository
git clone https://github.com/your-username/orm_cashback.git
cd orm_cashback

🔹 2. Create Virtual Environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

🔹 3. Install Dependencies
pip install -r requirements.txt


Or manually:

pip install django djangorestframework psycopg2-binary \
django-cors-headers djangorestframework-simplejwt

🔹 4. Setup PostgreSQL Database

Create a database:

DB Name: orm_db  
User: orm_user  
Password: your_password  
Port: 5432


Add this to settings.py:

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

🔹 5. Run Migrations
python manage.py makemigrations
python manage.py migrate

🔹 6. Create Superuser
python manage.py createsuperuser

🔹 7. Run Server
python manage.py runserver


Visit → http://127.0.0.1:8000/admin/

🧪 API Testing (Postman)

Import postman_collection.json into Postman and test endpoints:

🔐 Authentication
Method	Endpoint	Description
POST	/api/auth/register/	Register USER / BRAND
POST	/api/auth/login/	Get JWT Token
GET	/api/auth/me/	Get logged-in user info

Send all protected API calls with:

Authorization: Bearer <access_token>

🧾 Basic User Flow (API Level)
👤 USER

GET /api/shop/products/

POST /api/user/orders/

POST /api/user/reviews/

GET /api/user/wallet/

🏢 BRAND

GET /api/brand/products/

POST /api/brand/products/

POST /api/brand/review-slots/

GET /api/brand/orders/ (future)

📅 Day-Wise Backend Roadmap
Day	Tasks
Day 1	Setup Django, DB, apps
Day 2	Custom User Model (roles)
Day 3	Brand + Product + ReviewSlot models
Day 4	Orders + Reviews + Wallet models
Day 5	DRF setup + first API
Day 6	JWT Auth
Day 7	Brand APIs
Day 8	User APIs
Day 9	Wallet automation (signals)
Day 10	Testing + API Docs + GitHub push

