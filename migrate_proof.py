
from repository.db import get_conn
import mysql.connector

def migrate():
    print("Starting migration...")
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("SHOW COLUMNS FROM delays LIKE 'proof_path'")
        result = cursor.fetchone()
        
        if not result:
            print("Adding proof_path column to delays table...")
            cursor.execute("ALTER TABLE delays ADD COLUMN proof_path VARCHAR(255) DEFAULT NULL")
            print("Column added successfully.")
        else:
            print("Column proof_path already exists.")
            
        conn.commit()
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
