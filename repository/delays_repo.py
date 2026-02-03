from .db import get_conn
import mysql.connector
import json

def create_delay(task_id, user_id, reason_text, reason_audio_path, score_authenticity, score_avoidance, risk_level, ai_feedback, ai_analysis_json, delay_duration=0, proof_path=None):
    """Create delay record with validation."""
    # ... (validations ok) ...
    # ... 
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Ensure json is stringified
        if isinstance(ai_analysis_json, dict):
            ai_analysis_json = json.dumps(ai_analysis_json)
        elif ai_analysis_json and not isinstance(ai_analysis_json, str):
            raise ValueError("AI analysis must be a dict or JSON string")
            
        cursor.execute("""
            INSERT INTO delays (task_id, user_id, reason_text, reason_audio_path, score_authenticity, score_avoidance, risk_level, ai_feedback, ai_analysis_json, delay_duration, proof_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (task_id, user_id, reason_text.strip(), reason_audio_path, score_authenticity, score_avoidance, risk_level, ai_feedback, ai_analysis_json, delay_duration, proof_path))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as e:
        conn.rollback()
        raise Exception(f"Database error creating delay: {str(e)}")
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to create delay: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_delays_all():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT d.*, t.title as task_title, u.email as user_email
            FROM delays d
            LEFT JOIN tasks t ON d.task_id = t.id
            LEFT JOIN users u ON d.user_id = u.id
            ORDER BY d.submitted_at DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_delays_by_user(user_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT d.*, t.title as task_title 
            FROM delays d
            LEFT JOIN tasks t ON d.task_id = t.id
            WHERE d.user_id = %s
            ORDER BY d.submitted_at DESC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_user_delay_history(user_id, limit=5):
    """Formula 10: Get recent delays for behavioral consistency."""
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, score_authenticity, score_avoidance, submitted_at, ai_analysis_json
            FROM delays
            WHERE user_id = %s
            ORDER BY submitted_at DESC
            LIMIT %s
        """, (user_id, limit))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"❌ Error fetching delay history: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def count_user_delays(user_id):
    """Formula 5: Count total delays for employee."""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM delays WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except mysql.connector.Error as e:
        print(f"❌ Error counting delays: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()
