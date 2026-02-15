import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.db import execute_query
from database.connection import DatabaseConnection

def run_migration():
    print("🚀 Starting Job Role Migration...")
    
    # Initialize DB Pool
    try:
        DatabaseConnection.initialize_pool(min_conn=1, max_conn=2)
    except Exception as e:
        print(f"❌ Failed to initialize pool: {e}")
        return

    sql_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'migrations', 'add_job_role.sql')
    
    try:
        with open(sql_file, 'r') as f:
            sql_content = f.read()
            
        print(f"Executing migration from: {sql_file}")
        execute_query(sql_content, fetch=False)
        print("✅ Migration executed successfully!")
        
    except Exception as e:
        print(f"❌ Error executing migration: {e}")

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_migration()
