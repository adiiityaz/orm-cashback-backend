# 🚀 Quick PostgreSQL Setup - Step by Step

## ✅ Already Completed:
- ✅ PostgreSQL 18 is installed and running
- ✅ psycopg2-binary is installed
- ✅ Django settings.py updated to use PostgreSQL

## 📝 Next Steps:

### Step 1: Create Database and User

Run the setup script (it will ask for your PostgreSQL postgres user password):

```bash
cd "D:\BRC PROJECT 1"
venv\Scripts\activate
python setup_postgres_database.py
```

**When prompted:**
- Enter your PostgreSQL **postgres** user password (the one you set during PostgreSQL installation)
- The script will create:
  - Database: `orm_db`
  - User: `orm_user`
  - Password: `orm_password123`

### Step 2: Test Database Connection

After the script completes, test the connection:

```bash
python manage.py check --database default
```

### Step 3: Run Migrations

Create all database tables:

```bash
python manage.py migrate
```

### Step 4: Create Test Users

```bash
python manage.py create_test_users
```

### Step 5: Verify Everything Works

```bash
python manage.py runserver
```

Visit:
- Admin: http://127.0.0.1:8000/admin/
- API: http://127.0.0.1:8000/api/health/

---

## 🔧 Alternative: Manual Setup (if script doesn't work)

If you prefer to set up manually using pgAdmin:

1. **Open pgAdmin 4**
2. **Connect to PostgreSQL server** (enter postgres password)
3. **Right-click "Databases" → Create → Database**
   - Name: `orm_db`
   - Owner: `postgres`
4. **Right-click "Login/Group Roles" → Create → Login/Group Role**
   - Name: `orm_user`
   - Password: `orm_password123`
   - Can login: ✅ Yes
5. **Right-click `orm_db` → Properties → Security**
   - Add `orm_user` with all privileges

---

## 📝 Current Configuration

**Database Settings (in settings.py):**
- Database: `orm_db`
- User: `orm_user`
- Password: `orm_password123`
- Host: `localhost`
- Port: `5432`

**To change password:** Edit `orm_cashback/settings.py` or set environment variables.

---

## ✅ Success Checklist

- [ ] Database `orm_db` created
- [ ] User `orm_user` created
- [ ] Database connection tested
- [ ] Migrations run successfully
- [ ] Test users created
- [ ] Server running without errors

---

**Need help?** See `POSTGRESQL_SETUP_GUIDE.md` for detailed instructions.

