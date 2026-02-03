
from repository.db import get_conn

def check_schema():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DESCRIBE users")
        columns = [row[0] for row in cursor.fetchall()]
        print("Users Columns:", columns)
        
        cursor.execute("SHOW TABLES LIKE 'organizations'")
        org_result = cursor.fetchone()
        if org_result:
            print("Table 'organizations' exists.")
        else:
            print("Table 'organizations' DOES NOT exist.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
