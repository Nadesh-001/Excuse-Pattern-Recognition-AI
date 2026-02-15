"""
Supabase Setup Script
Automates database schema deployment and initial setup
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment."""
    from urllib.parse import quote_plus
    
    password = os.getenv("SUPABASE_DB_PASSWORD")
    
    if not password or password == "your_database_password_here":
        print("\n⚠️  ERROR: SUPABASE_DB_PASSWORD not set!")
        print("\n📝 Steps to fix:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Navigate to Settings → Database → Database Settings")
        print("3. Find or reset your database password")
        print("4. Update .env file:")
        print("   SUPABASE_DB_PASSWORD=your_actual_password")
        print("\n")
        sys.exit(1)
    
    # URL encode password to handle special characters like @
    encoded_password = quote_plus(password)
    return f"postgresql://postgres:{encoded_password}@db.qdivjebqgpiyilitzsjm.supabase.co:5432/postgres"


def deploy_schema():
    """Deploy database schema from SQL file."""
    print("\n🚀 Deploying Supabase Schema...")
    print("=" * 60)
    
    database_url = get_database_url()
    schema_file = os.path.join(os.path.dirname(__file__), "supabase_schema.sql")
    
    if not os.path.exists(schema_file):
        print(f"✗ Schema file not found: {schema_file}")
        sys.exit(1)
    
    try:
        # Connect to database
        print("📡 Connecting to Supabase...")
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Read schema file
        print(f"📄 Reading schema file: {schema_file}")
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema
        print("⚙️  Executing SQL schema...")
        cursor.execute(schema_sql)
        
        # Verify tables
        print("\n✅ Schema deployed successfully!")
        print("\n📊 Verifying tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n✓ Found {len(tables)} tables:")
        for table in tables:
            print(f"  • {table[0]}")
        
        # Verify admin user
        cursor.execute("SELECT email, role FROM users WHERE role = 'admin' LIMIT 1")
        admin = cursor.fetchone()
        if admin:
            print(f"\n✓ Default admin created: {admin[0]}")
            print("  Password: admin123")
            print("  ⚠️  Change this password after first login!")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("1. Run: python flask_app.py")
        print("2. Navigate to: http://localhost:5000")
        print("3. Login with admin@example.com / admin123")
        print("4. Change admin password in profile")
        print("\n")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n✗ Connection Error: {e}")
        print("\n💡 Possible solutions:")
        print("1. Check SUPABASE_DB_PASSWORD in .env")
        print("2. Verify password in Supabase dashboard")
        print("3. Ensure database is accessible (not paused)")
        return False
        
    except psycopg2.Error as e:
        print(f"\n✗ Database Error: {e}")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        return False


def test_connection():
    """Test database connection."""
    print("\n🔍 Testing Database Connection...")
    print("=" * 60)
    
    database_url = get_database_url()
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ Connected to PostgreSQL")
        print(f"  Version: {version.split(',')[0]}")
        
        cursor.close()
        conn.close()
        
        print("=" * 60)
        print("✅ Connection successful!")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   SUPABASE SETUP - Flask Task Management System")
    print("=" * 60)
    
    # Step 1: Test connection
    if not test_connection():
        sys.exit(1)
    
    # Step 2: Deploy schema
    if not deploy_schema():
        sys.exit(1)
    
    print("🎉 All done! Your database is ready to use.\n")
