import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.db import execute_query
from database.connection import DatabaseConnection

def check_analytics_data():
    print("🔎 Checking Analytics Data Coverage...\n")
    try:
        DatabaseConnection.initialize_pool(min_conn=1, max_conn=2)
        
        # 1. Check Users
        print("\n--- Users ---")
        users = execute_query("SELECT id, email, role, full_name FROM users", fetch=True)
        for u in users:
            print(f"User: {u['email']} (ID: {u['id']}, Role: {u['role']})")
            
            # 2. Check Tasks for User
            task_count = execute_query("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s", (u['id'],), fetch=True)[0]['count']
            print(f"  - Tasks Assigned: {task_count}")
            
            # 3. Check Delays for User
            delay_count = execute_query("SELECT COUNT(*) as count FROM delays WHERE user_id = %s", (u['id'],), fetch=True)[0]['count']
            print(f"  - Delays Submitted: {delay_count}")
            
            # 4. Check Analytics Summary View (if exists and populated)
            # The summary table is 'user_analytics_summary'
            summary = execute_query("SELECT * FROM user_analytics_summary WHERE user_id = %s", (u['id'],), fetch=True)
            if summary:
                print(f"  - Summary Table Entry: FOUND (Total Tasks: {summary[0]['total_tasks']})")
            else:
                 print(f"  - Summary Table Entry: NOT FOUND (This might be why analytics are empty)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_analytics_data()
