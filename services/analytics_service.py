from repository.db import get_conn
import pandas as pd

def get_analytics_data():
    conn = get_conn()
    if not conn: return None, None
    try:
        # Optimize: Select only columns needed for analytics charts
        df_delays = pd.read_sql("""
            SELECT id, task_id, user_id, score_authenticity, score_avoidance, 
                   risk_level, ai_analysis_json, submitted_at 
            FROM delays
        """, conn)
        
        df_tasks = pd.read_sql("""
            SELECT id, status, priority, created_at, deadline 
            FROM tasks
        """, conn)
        return df_delays, df_tasks
    finally:
        conn.close()
