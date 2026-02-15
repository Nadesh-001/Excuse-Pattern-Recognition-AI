import os
import sys

# Add parent directory to path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.db import execute_query

def run_optimization():
    print("🚀 Starting Database Optimization...")
    
    # Initialize DB Pool
    try:
        from database.connection import DatabaseConnection
        DatabaseConnection.initialize_pool(min_conn=1, max_conn=2)
    except Exception as e:
        print(f"❌ Failed to initialize pool: {e}")
        return

    sql_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'optimization.sql')
    
    try:
        with open(sql_file, 'r') as f:
            sql_content = f.read()
            
        statements = sql_content.split(';')
        
        for statement in statements:
            if statement.strip():
                stmt = statement.strip()
                print(f"Executing: {stmt[:50]}...")
                # Determine if we should fetch results
                should_fetch = stmt.upper().startswith('SELECT') or stmt.upper().startswith('WITH') or 'RETURNING' in stmt.upper()
                
                try:
                    execute_query(stmt, fetch=should_fetch)
                    print("✅ Success")
                except Exception as e:
                    # Ignore "no results to fetch" error if we expected fetch but got none (edge case)
                    if "no results to fetch" in str(e).lower():
                         print("✅ Success (No results returned)")
                    else:
                        print(f"❌ Error executing statement: {e}")
                
        print("🎉 Database Optimization Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_optimization()
