import sys
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Add root to path
sys.path.append(os.getcwd())

from repository.db import get_conn
from utils.hashing import hash_password
import mysql.connector

def seed_users():
    """Seed the database with default users for testing and initial setup."""
    print("=" * 50)
    print("🌱 Starting User Seeding Process...")
    print("=" * 50)
    
    try:
        conn = get_conn()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        print("💡 Tip: Check your database configuration in .env or .streamlit/secrets.toml")
        return False

    users = [
        ("admin@example.com", "Admin User", "admin123", "admin"),
        ("manager@example.com", "Manager User", "manager123", "manager"),
        ("employee@example.com", "Employee User", "employee123", "employee")
    ]

    cursor = conn.cursor()
    created_count = 0
    existing_count = 0
    
    try:
        for email, name, password, role in users:
            try:
                # Check if exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    print(f"ℹ️  User {email} already exists - skipping")
                    existing_count += 1
                else:
                    hashed = hash_password(password)
                    cursor.execute(
                        "INSERT INTO users (email, full_name, password_hash, role) VALUES (%s, %s, %s, %s)",
                        (email, name, hashed, role)
                    )
                    print(f"✅ Created user: {email} (Role: {role})")
                    created_count += 1
            except mysql.connector.IntegrityError as ie:
                print(f"⚠️  Integrity error for {email}: {ie}")
            except Exception as e:
                print(f"❌ Error creating user {email}: {e}")
        
        conn.commit()
        
        # Verify seeding
        print("\n" + "=" * 50)
        print("📊 Seeding Summary:")
        print(f"   ✅ Created: {created_count} user(s)")
        print(f"   ℹ️  Already existed: {existing_count} user(s)")
        
        # Verification query
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        print(f"   📈 Total users in database: {total}")
        print("=" * 50)
        print("🎉 Seeding Process Complete!")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Critical error during seeding: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_users()
