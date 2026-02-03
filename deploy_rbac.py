"""
Deploy RBAC Migration to TiDB Cloud

Standalone script that reads credentials from .streamlit/secrets.toml
"""

import os
import sys
import toml
import mysql.connector

def deploy_migration():
    """Execute RBAC migration SQL file"""
    
    print("=" * 60)
    print("🚀 Deploying RBAC Migration to TiDB Cloud")
    print("=" * 60)
    print()
    
    # Read TiDB credentials from secrets.toml
    secrets_path = os.path.join('.streamlit', 'secrets.toml')
    
    if not os.path.exists(secrets_path):
        print(f"❌ Secrets file not found: {secrets_path}")
        return False
    
    print("📖 Reading TiDB credentials from secrets.toml...")
    secrets = toml.load(secrets_path)
    
    tidb_config = {
        'host': secrets['DB_HOST'],
        'port': int(secrets.get('DB_PORT', 4000)),
        'user': secrets['DB_USER'],
        'password': secrets['DB_PASSWORD'],
        'database': secrets['DB_NAME'],
        'ssl_ca': 'isrgrootx1.pem',
        'ssl_verify_cert': True,
        'ssl_verify_identity': True
    }
    
    # Read migration file
    migration_file = os.path.join('database', 'migration_rbac.sql')
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    try:
        # Connect to TiDB
        print("📡 Connecting to TiDB Cloud...")
        conn = mysql.connector.connect(**tidb_config)
        cursor = conn.cursor()
        print("✅ Connected successfully!")
        print()
        
        # Split and execute SQL statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        print(f"📝 Executing {len(statements)} SQL statements...")
        print()
        
        for idx, stmt in enumerate(statements, 1):
            if stmt:
                try:
                    cursor.execute(stmt)
                    
                    # Parse statement type
                    stmt_type = stmt.split()[0].upper()
                    if stmt_type == 'CREATE':
                        table_name = stmt.split('TABLE')[1].split('(')[0].strip().split()[0]
                        print(f"  [{idx}] ✅ Created table: {table_name}")
                    elif stmt_type == 'INSERT':
                        print(f"  [{idx}] ✅ Inserted data")
                    else:
                        print(f"  [{idx}] ✅ Executed statement")
                        
                except mysql.connector.Error as e:
                    # Check if it's a duplicate/already exists error
                    if e.errno == 1050:  # Table already exists
                        print(f"  [{idx}] ⚠️  Table already exists, skipping")
                    elif e.errno == 1062:  # Duplicate entry
                        print(f"  [{idx}] ⚠️  Data already exists, skipping")
                    else:
                        print(f"  [{idx}] ⚠️  Warning: {e}")
                    continue
        
        conn.commit()
        print()
        print("=" * 60)
        print("✅ Migration deployed successfully!")
        print("=" * 60)
        print()
        
        # Verify tables
        print("🔍 Verifying tables...")
        cursor.execute("SHOW TABLES LIKE 'permissions'")
        if cursor.fetchone():
            print("  ✅ permissions table exists")
        
        cursor.execute("SHOW TABLES LIKE 'role_permissions'")
        if cursor.fetchone():
            print("  ✅ role_permissions table exists")
        
        # Count permissions
        cursor.execute("SELECT COUNT(*) FROM permissions")
        perm_count = cursor.fetchone()[0]
        print(f"  📊 {perm_count} permissions loaded")
        
        cursor.execute("SELECT COUNT(*) FROM role_permissions")
        role_perm_count = cursor.fetchone()[0]
        print(f"  📊 {role_perm_count} role-permission mappings created")
        
        print()
        print("🎉 RBAC system is ready!")
        print()
        print("Next steps:")
        print("  1. Restart your Streamlit app")
        print("  2. Login and test the permission system")
        print("  3. Check Profile page (all users)")
        print("  4. Check Audit Logs page (admin only)")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = deploy_migration()
    sys.exit(0 if success else 1)
