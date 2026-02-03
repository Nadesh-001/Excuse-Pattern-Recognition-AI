
from repository.db import get_conn
import mysql.connector

def migrate_orgs():
    print("Starting Organization Migration...")
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        # 1. Create organizations table
        cursor.execute("SHOW TABLES LIKE 'organizations'")
        if not cursor.fetchone():
            print("Creating 'organizations' table...")
            cursor.execute("""
                CREATE TABLE organizations (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            print("'organizations' table exists.")

        # 2. Add org_id to users
        cursor.execute("DESCRIBE users")
        columns = [row[0] for row in cursor.fetchall()]
        if 'org_id' not in columns:
            print("Adding 'org_id' to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN org_id BIGINT")
            cursor.execute("ALTER TABLE users ADD CONSTRAINT fk_user_org FOREIGN KEY (org_id) REFERENCES organizations(id)")
            
            # Create default org for existing users
            print("Creating default organization...")
            cursor.execute("INSERT INTO organizations (name) VALUES ('Default Org')")
            default_org_id = cursor.lastrowid
            
            print(f"Updating existing users to org_id {default_org_id}...")
            cursor.execute("UPDATE users SET org_id = %s WHERE org_id IS NULL", (default_org_id,))
        else:
            print("'org_id' column exists in users.")

        conn.commit()
        print("Migration successful.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_orgs()
