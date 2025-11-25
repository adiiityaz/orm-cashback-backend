"""
PostgreSQL Database Setup Script
This script creates the database and user for the ORM Cashback project.

Run this script with: python setup_postgres_database.py
You'll be prompted for the PostgreSQL superuser (postgres) password.
"""

import psycopg2
from psycopg2 import sql
import getpass
import sys

# Database configuration
DB_NAME = 'orm_db'
DB_USER = 'orm_user'
DB_PASSWORD = 'orm_password123'  # Change this to your preferred password
DB_HOST = 'localhost'
DB_PORT = '5432'

def create_database():
    """Create database and user"""
    
    print("=" * 60)
    print("PostgreSQL Database Setup for ORM Cashback")
    print("=" * 60)
    print()
    
    # Get postgres superuser password
    print("Enter PostgreSQL superuser (postgres) password:")
    postgres_password = getpass.getpass("Password: ")
    print()
    
    try:
        # Connect to PostgreSQL server (using default 'postgres' database)
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user='postgres',
            password=postgres_password,
            database='postgres'  # Connect to default database
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("✓ Connected successfully!")
        print()
        
        # Check if database exists
        print(f"Checking if database '{DB_NAME}' exists...")
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"⚠ Database '{DB_NAME}' already exists.")
            response = input("Do you want to drop and recreate it? (yes/no): ").lower()
            if response == 'yes':
                print(f"Dropping database '{DB_NAME}'...")
                cursor.execute(
                    sql.SQL("DROP DATABASE {}").format(
                        sql.Identifier(DB_NAME)
                    )
                )
                print("✓ Database dropped.")
            else:
                print("Keeping existing database.")
        else:
            print(f"Database '{DB_NAME}' does not exist.")
        
        # Create database
        if not exists or (exists and response == 'yes'):
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_NAME)
                )
            )
            print(f"✓ Database '{DB_NAME}' created successfully!")
        print()
        
        # Check if user exists
        print(f"Checking if user '{DB_USER}' exists...")
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            (DB_USER,)
        )
        user_exists = cursor.fetchone()
        
        if user_exists:
            print(f"⚠ User '{DB_USER}' already exists.")
            response = input("Do you want to update the password? (yes/no): ").lower()
            if response == 'yes':
                print(f"Updating password for user '{DB_USER}'...")
                cursor.execute(
                    sql.SQL("ALTER USER {} WITH PASSWORD %s").format(
                        sql.Identifier(DB_USER)
                    ),
                    (DB_PASSWORD,)
                )
                print("✓ Password updated.")
        else:
            # Create user
            print(f"Creating user '{DB_USER}'...")
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(DB_USER)
                ),
                (DB_PASSWORD,)
            )
            print(f"✓ User '{DB_USER}' created successfully!")
        print()
        
        # Grant privileges
        print("Granting privileges...")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(DB_NAME),
                sql.Identifier(DB_USER)
            )
        )
        print("✓ Privileges granted on database.")
        
        # Connect to the new database to grant schema privileges
        conn.close()
        print("Connecting to new database to grant schema privileges...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user='postgres',
            password=postgres_password,
            database=DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute(
            sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(
                sql.Identifier(DB_USER)
            )
        )
        cursor.execute(
            sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}").format(
                sql.Identifier(DB_USER)
            )
        )
        cursor.execute(
            sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {}").format(
                sql.Identifier(DB_USER)
            )
        )
        print("✓ Schema privileges granted.")
        print()
        
        # Test connection with new user
        print("Testing connection with new user...")
        conn.close()
        test_conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        test_conn.close()
        print("✓ Connection test successful!")
        print()
        
        print("=" * 60)
        print("✅ Database setup completed successfully!")
        print("=" * 60)
        print()
        print("Database Configuration:")
        print(f"  Database Name: {DB_NAME}")
        print(f"  Username: {DB_USER}")
        print(f"  Password: {DB_PASSWORD}")
        print(f"  Host: {DB_HOST}")
        print(f"  Port: {DB_PORT}")
        print()
        print("Next steps:")
        print("  1. Update Django settings.py to use PostgreSQL")
        print("  2. Run: python manage.py migrate")
        print("  3. Run: python manage.py create_test_users")
        print()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection error: {e}")
        print("\nPossible issues:")
        print("  - PostgreSQL service is not running")
        print("  - Incorrect password")
        print("  - PostgreSQL is not installed")
        return False
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    success = create_database()
    sys.exit(0 if success else 1)

