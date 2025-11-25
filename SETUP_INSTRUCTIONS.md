# 🚀 PostgreSQL Setup - Choose Your Method

## Method 1: Using Environment Variable (Recommended)

Set the PostgreSQL password as an environment variable, then run the script:

```powershell
# Set password (replace 'your_password' with your actual postgres password)
$env:PGPASSWORD='your_postgres_password'

# Run setup
cd "D:\BRC PROJECT 1"
venv\Scripts\activate
python setup_postgres_simple.py
```

## Method 2: Using pgAdmin (GUI - Easiest)

1. **Open pgAdmin 4** (search in Start Menu)

2. **Connect to PostgreSQL:**
   - Enter your postgres password when prompted

3. **Create Database:**
   - Right-click **"Databases"** → **Create** → **Database**
   - **Name:** `orm_db`
   - **Owner:** `postgres`
   - Click **Save**

4. **Create User:**
   - Expand **"Login/Group Roles"**
   - Right-click → **Create** → **Login/Group Role**
   - **General tab:**
     - **Name:** `orm_user`
   - **Definition tab:**
     - **Password:** `orm_password123`
   - **Privileges tab:**
     - ✅ **Can login?** → **Yes**
   - Click **Save**

5. **Grant Permissions:**
   - Right-click on `orm_db` → **Properties**
   - Go to **Security** tab
   - Click **+** to add privilege
   - **Grantee:** `orm_user`
   - **Privileges:** Select all (SELECT, INSERT, UPDATE, DELETE, etc.)
   - Click **Save**

6. **Grant Schema Privileges:**
   - Right-click on `orm_db` → **Query Tool**
   - Run these commands:
   ```sql
   GRANT ALL ON SCHEMA public TO orm_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO orm_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO orm_user;
   ```

## Method 3: Using psql Command Line

1. **Open Command Prompt or PowerShell**

2. **Navigate to PostgreSQL bin:**
   ```powershell
   cd "C:\Program Files\PostgreSQL\18\bin"
   ```

3. **Connect to PostgreSQL:**
   ```powershell
   .\psql.exe -U postgres
   ```
   (Enter your postgres password)

4. **Run SQL commands:**
   ```sql
   CREATE DATABASE orm_db;
   CREATE USER orm_user WITH PASSWORD 'orm_password123';
   GRANT ALL PRIVILEGES ON DATABASE orm_db TO orm_user;
   \c orm_db
   GRANT ALL ON SCHEMA public TO orm_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO orm_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO orm_user;
   \q
   ```

## After Database Setup:

Once the database is created (using any method above), run:

```powershell
cd "D:\BRC PROJECT 1"
venv\Scripts\activate

# Test connection
python manage.py check --database default

# Run migrations
python manage.py migrate

# Create test users
python manage.py create_test_users

# Start server
python manage.py runserver
```

---

**Which method do you prefer?** I recommend Method 2 (pgAdmin) as it's the easiest and most visual.

