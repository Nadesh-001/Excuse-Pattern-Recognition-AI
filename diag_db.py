
from database.connection import DatabaseConnection
from repository.db import execute_query
from services.analytics_service import STATS_QUERY
import json
from decimal import Decimal

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def run_diagnostics():
    DatabaseConnection.initialize_pool()
    users = execute_query('SELECT id, email, role FROM users')
    print(f"Total users in system: {len(users)}")
    
    for u in users:
        print(f"\n--- Diagnostics for User {u['id']} ({u['email']}, Role: {u['role']}) ---")
        
        # Check tasks
        tasks = execute_query('SELECT id, title, assigned_to FROM tasks WHERE assigned_to = %s', (u['id'],))
        print(f"Tasks assigned: {len(tasks)}")
        
        # Check delays
        delays = execute_query('SELECT id, task_id, score_authenticity, risk_level FROM delays WHERE user_id = %s', (u['id'],))
        print(f"Delays recorded: {len(delays)}")
        
        # Run Stats Query
        res = execute_query(STATS_QUERY, (u['id'], u['id']))
        # Convert Decimals to floats for printing
        res_list = []
        for row in res:
            res_list.append({k: (float(v) if isinstance(v, Decimal) else v) for k, v in row.items()})
        print(f"Stats Query Result: {json.dumps(res_list, indent=2)}")

if __name__ == "__main__":
    run_diagnostics()
