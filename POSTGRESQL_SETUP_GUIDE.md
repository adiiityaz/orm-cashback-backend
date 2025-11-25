# 🐘 PostgreSQL Setup Guide for Windows

Complete step-by-step guide to set up PostgreSQL for your Django project.

---

## 📋 Prerequisites

- Windows 10/11
- Administrator access
- Internet connection

---

## Step 1: Download PostgreSQL

1. **Visit PostgreSQL official website:**
   - Go to: https://www.postgresql.org/download/windows/
   - Click **"Download the installer"**

2. **Or use direct download:**
   - Go to: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Select **PostgreSQL 16** (or latest version)
   - Choose **Windows x86-64** installer
   - Click **Download**

---

## Step 2: Install PostgreSQL

1. **Run the installer:**
   - Double-click the downloaded `.exe` file
   - Click **Next** on the welcome screen

2. **Choose installation directory:**
   - Default: `C:\Program Files\PostgreSQL\16`
   - Click **Next**

3. **Select components:**
   - ✅ PostgreSQL Server (required)
   - ✅ pgAdmin 4 (GUI tool - recommended)
   - ✅ Stack Builder (optional)
   - ✅ Command Line Tools (recommended)
   - Click **Next**

4. **Choose data directory:**
   - Default: `C:\Program Files\PostgreSQL\16\data`
   - Click **Next**

5. **Set PostgreSQL superuser password:**
   - **Password:** `postgres` (or choose a strong password)
   - **⚠️ IMPORTANT:** Remember this password!
   - Click **Next**

6. **Set port:**
   - Default: `5432`
   - Keep default, click **Next**

7. **Choose locale:**
   - Default: `[Default locale]`
   - Click **Next**

8. **Review settings:**
   - Click **Next** to proceed

9. **Installation:**
   - Wait for installation to complete (5-10 minutes)
   - Click **Finish**

---

## Step 3: Verify Installation

1. **Open Command Prompt (as Administrator):**
   - Press `Win + X`
   - Select **"Windows PowerShell (Admin)"** or **"Command Prompt (Admin)"**

2. **Check PostgreSQL version:**
   ```bash
   psql --version
   ```
   - Should show: `psql (PostgreSQL) 16.x`

3. **Check if PostgreSQL service is running:**
   ```bash
   # PowerShell
   Get-Service postgresql*
   
   # Or check in Services
   # Press Win + R, type: services.msc
   # Look for "postgresql-x64-16" service
   ```

---

## Step 4: Create Database and User

### Option A: Using pgAdmin (GUI - Recommended)

1. **Open pgAdmin 4:**
   - Search for "pgAdmin 4" in Start Menu
   - Open the application

2. **Connect to server:**
   - Enter password you set during installation
   - Click **Save Password** (optional)

3. **Create Database:**
   - Right-click on **Databases** → **Create** → **Database**
   - **Database name:** `orm_db`
   - **Owner:** `postgres` (default)
   - Click **Save**

4. **Create User:**
   - Expand **Login/Group Roles**
   - Right-click → **Create** → **Login/Group Role**
   - **General tab:**
     - **Name:** `orm_user`
   - **Definition tab:**
     - **Password:** `orm_password123` (or your choice)
   - **Privileges tab:**
     - ✅ Can login? → **Yes**
     - ✅ Create databases? → **Yes** (optional)
   - Click **Save**

5. **Grant permissions:**
   - Right-click on `orm_db` database → **Properties**
   - Go to **Security** tab
   - Click **+** to add privilege
   - **Grantee:** `orm_user`
   - **Privileges:** Select all (SELECT, INSERT, UPDATE, DELETE, etc.)
   - Click **Save**

### Option B: Using Command Line (psql)

1. **Open Command Prompt:**
   ```bash
   # Navigate to PostgreSQL bin directory
   cd "C:\Program Files\PostgreSQL\16\bin"
   ```

2. **Connect to PostgreSQL:**
   ```bash
   psql -U postgres
   ```
   - Enter password when prompted

3. **Create database:**
   ```sql
   CREATE DATABASE orm_db;
   ```

4. **Create user:**
   ```sql
   CREATE USER orm_user WITH PASSWORD 'orm_password123';
   ```

5. **Grant privileges:**
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE orm_db TO orm_user;
   ```

6. **Connect to new database:**
   ```sql
   \c orm_db
   ```

7. **Grant schema privileges:**
   ```sql
   GRANT ALL ON SCHEMA public TO orm_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO or_user;
   ```

8. **Exit psql:**
   ```sql
   \q
   ```

---

## Step 5: Install Python PostgreSQL Adapter

1. **Activate your virtual environment:**
   ```bash
   cd "D:\BRC PROJECT 1"
   venv\Scripts\activate
   ```

2. **Install psycopg2:**
   ```bash
   pip install psycopg2-binary
   ```
   - This should already be in your `requirements.txt`

3. **Verify installation:**
   ```bash
   python -c "import psycopg2; print('psycopg2 installed successfully')"
   ```

---

## Step 6: Update Django Settings

1. **Open `orm_cashback/settings.py`**

2. **Update DATABASES configuration:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'orm_db',
           'USER': 'orm_user',
           'PASSWORD': 'orm_password123',  # Your password
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

   **OR use environment variables (recommended):**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.getenv('DB_NAME', 'orm_db'),
           'USER': os.getenv('DB_USER', 'orm_user'),
           'PASSWORD': os.getenv('DB_PASSWORD', 'orm_password123'),
           'HOST': os.getenv('DB_HOST', 'localhost'),
           'PORT': os.getenv('DB_PORT', '5432'),
       }
   }
   ```

3. **Update `.env` file (if using):**
   ```bash
   DB_NAME=orm_db
   DB_USER=orm_user
   DB_PASSWORD=orm_password123
   DB_HOST=localhost
   DB_PORT=5432
   ```

---

## Step 7: Test Database Connection

1. **Test connection from Python:**
   ```bash
   python manage.py dbshell
   ```
   - If successful, you'll see: `psql (PostgreSQL) ...`
   - Type `\q` to exit

2. **Or test with Django:**
   ```bash
   python manage.py check --database default
   ```

---

## Step 8: Run Migrations

1. **Delete old SQLite database (optional):**
   ```bash
   # Backup first if needed
   # Then delete: db.sqlite3
   ```

2. **Create migrations (if needed):**
   ```bash
   python manage.py makemigrations
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Or create test users:**
   ```bash
   python manage.py create_test_users
   ```

---

## Step 9: Verify Everything Works

1. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Test admin panel:**
   - Visit: http://127.0.0.1:8000/admin/
   - Login with your admin credentials

3. **Test API:**
   - Visit: http://127.0.0.1:8000/api/health/

---

## 🔧 Troubleshooting

### Issue 1: "Connection refused"
**Solution:**
- Check if PostgreSQL service is running:
  ```bash
  Get-Service postgresql*
  ```
- Start service if stopped:
  ```bash
  Start-Service postgresql-x64-16
  ```

### Issue 2: "Authentication failed"
**Solution:**
- Verify username and password in `settings.py`
- Check `pg_hba.conf` file (usually in `C:\Program Files\PostgreSQL\16\data\`)
- Ensure password authentication is enabled

### Issue 3: "Database does not exist"
**Solution:**
- Create database using pgAdmin or psql (see Step 4)

### Issue 4: "Permission denied"
**Solution:**
- Grant proper privileges to user (see Step 4)

### Issue 5: "psycopg2 installation failed"
**Solution:**
- Install Visual C++ Build Tools
- Or use: `pip install psycopg2-binary` (pre-compiled)

---

## 📝 Quick Reference

### PostgreSQL Service Commands
```bash
# Check status
Get-Service postgresql*

# Start service
Start-Service postgresql-x64-16

# Stop service
Stop-Service postgresql-x64-16

# Restart service
Restart-Service postgresql-x64-16
```

### Common psql Commands
```bash
# Connect to database
psql -U orm_user -d orm_db

# List all databases
\l

# List all tables
\dt

# Describe table
\d table_name

# Exit
\q
```

### Database Connection String Format
```
postgresql://username:password@host:port/database
Example: postgresql://orm_user:orm_password123@localhost:5432/orm_db
```

---

## ✅ Checklist

- [ ] PostgreSQL installed
- [ ] PostgreSQL service running
- [ ] Database `orm_db` created
- [ ] User `orm_user` created
- [ ] Permissions granted
- [ ] `psycopg2-binary` installed
- [ ] Django settings updated
- [ ] Database connection tested
- [ ] Migrations run successfully
- [ ] Test users created
- [ ] Admin panel accessible

---

## 🎉 Success!

If all steps completed successfully, your Django project is now using PostgreSQL!

**Next Steps:**
- Your frontend can connect to the same API endpoints
- No changes needed in frontend code
- Database is production-ready

---

**Need Help?**
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Django Database Setup: https://docs.djangoproject.com/en/stable/ref/databases/

