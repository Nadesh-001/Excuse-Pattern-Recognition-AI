from .db import get_conn
import mysql.connector

def create_log(user_id, action, details):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO audit_logs (user_id, action, details) VALUES (%s, %s, %s)",
            (user_id, action, details)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_recent_logs(limit=50):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT l.*, u.full_name as user_name, u.email as user_email
            FROM audit_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.timestamp DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
