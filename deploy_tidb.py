"""
TiDB Cloud Database Deployment Script
Deploys schema and migrations to your TiDB Cloud Cluster0
"""
import mysql.connector
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# TiDB Connection Details
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"),
    "port": int(os.getenv("DB_PORT", 4000)),
    "user": os.getenv("DB_USER", "Ye6vmKgkwjdG7Lt.root"),
    "password": os.getenv("DB_PASSWORD", "dObU6zfePl2yB2if"),
    "database": os.getenv("DB_NAME", "test"),
    "ssl_ca": Path(__file__).parent / "database" / "isrgrootx1.pem",
    "ssl_verify_cert": True,
    "ssl_verify_identity": True
}

def test_connection():
    """Test basic TiDB connection"""
    print("🔗 Testing TiDB Cloud connection...")
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            ssl_ca=str(DB_CONFIG["ssl_ca"]) if DB_CONFIG["ssl_ca"].exists() else None
        )
        print(f"✅ Connected successfully to {DB_CONFIG['host']}")
        
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"📊 TiDB Version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        print(f"❌ Connection failed: {e}")
        return False

def execute_sql_file(filepath, description):
    """Execute a SQL file"""
    print(f"\n📝 Executing {description}...")
    
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        return False
    
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            ssl_ca=str(DB_CONFIG["ssl_ca"]) if DB_CONFIG["ssl_ca"].exists() else None
        )
        cursor = conn.cursor()
        
        # Read and execute SQL file
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"  ✓ Statement {i}/{len(statements)} executed")
                except mysql.connector.Error as e:
                    # Ignore "already exists" errors for migrations
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"  ⚠️  Statement {i} skipped (already exists)")
                    else:
                        print(f"  ❌ Statement {i} failed: {e}")
                        raise
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ {description} completed successfully!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Failed to execute {description}: {e}")
        return False

def verify_schema():
    """Verify that all tables were created"""
    print("\n🔍 Verifying database schema...")
    
    expected_tables = ['users', 'tasks', 'attachments', 'delays', 'resource_logs', 'audit_logs']
    
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            ssl_ca=str(DB_CONFIG["ssl_ca"]) if DB_CONFIG["ssl_ca"].exists() else None
        )
        cursor = conn.cursor()
        
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            status = "✅" if table in expected_tables else "❓"
            print(f"  {status} {table}")
        
        missing = set(expected_tables) - set(tables)
        if missing:
            print(f"\n⚠️  Missing tables: {', '.join(missing)}")
        else:
            print("\n✅ All expected tables present!")
        
        cursor.close()
        conn.close()
        return len(missing) == 0
        
    except mysql.connector.Error as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main deployment process"""
    print("=" * 60)
    print("🚀 TiDB Cloud Database Deployment")
    print("=" * 60)
    
    # Step 1: Test connection
    if not test_connection():
        print("\n❌ Cannot proceed without database connection.")
        print("\nTroubleshooting:")
        print("1. Check your credentials in .env file")
        print("2. Ensure SSL certificate exists at database/isrgrootx1.pem")
        print("3. Verify your IP is whitelisted in TiDB Cloud")
        return False
    
    # Step 2: Deploy schema
    schema_file = Path(__file__).parent / "database" / "schema.sql"
    if not execute_sql_file(schema_file, "Main Schema (schema.sql)"):
        return False
    
    # Step 3: Apply migrations
    migration_file = Path(__file__).parent / "database" / "migration_academic_formulas.sql"
    if migration_file.exists():
        execute_sql_file(migration_file, "Academic Formulas Migration")
    
    # Step 4: Apply optimizations
    optimization_file = Path(__file__).parent / "database" / "optimization_indexes.sql"
    if optimization_file.exists():
        execute_sql_file(optimization_file, "Performance Optimizations")
    
    # Step 5: Verify
    if verify_schema():
        print("\n" + "=" * 60)
        print("🎉 Database deployment completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python -m streamlit run app.py")
        print("2. Test user registration and login")
        print("3. Create a test task")
        return True
    else:
        print("\n⚠️  Deployment completed with warnings.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
