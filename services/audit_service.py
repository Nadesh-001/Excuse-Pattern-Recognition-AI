"""
Audit Service - System Audit Logging

Provides functions to:
- Log sensitive actions to audit_logs table
- Retrieve audit logs for admin viewing
- Track user activities
"""

from flask import session
from datetime import datetime
from repository.db import get_conn

def log_action(action: str, details: str = None, target_user_id: int = None):
    """
    Log a sensitive action to the audit_logs table.
    
    Args:
        action: Action type (e.g., 'USER_LOGIN', 'ROLE_CHANGED')
        details: Additional details about the action
        target_user_id: Optional ID of affected user (for role changes, etc.)
    """
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return  # Can't log without a user
        
        conn = get_conn()
        cursor = conn.cursor()
        
        # Build details string
        full_details = details or ""
        if target_user_id:
            full_details += f" | Target User ID: {target_user_id}"
        
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, details)
            VALUES (%s, %s, %s)
        """, (user_id, action, full_details))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Audit log error: {e}")


def get_audit_logs(limit: int = 100, action_filter: str = None):
    """
    Retrieve audit logs from database.
    
    Args:
        limit: Maximum number of logs to retrieve
        action_filter: Optional action type filter
        
    Returns:
        List of audit log dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if action_filter:
            query = """
                SELECT 
                    a.id,
                    a.timestamp,
                    u.full_name as user_name,
                    u.email,
                    a.action,
                    a.details
                FROM audit_logs a
                JOIN users u ON u.id = a.user_id
                WHERE a.action LIKE %s
                ORDER BY a.timestamp DESC
                LIMIT %s
            """
            cursor.execute(query, (f"%{action_filter}%", limit))
        else:
            query = """
                SELECT 
                    a.id,
                    a.timestamp,
                    u.full_name as user_name,
                    u.email,
                    a.action,
                    a.details
                FROM audit_logs a
                JOIN users u ON u.id = a.user_id
                ORDER BY a.timestamp DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
        
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return logs
        
    except Exception as e:
        print(f"Error retrieving audit logs: {e}")
        return []


# Common audit action types
class AuditActions:
    USER_LOGIN = 'USER_LOGIN'
    USER_LOGOUT = 'USER_LOGOUT'
    ROLE_CHANGED = 'ROLE_CHANGED'
    TASK_CREATED = 'TASK_CREATED'
    TASK_DELETED = 'TASK_DELETED'
    PROFILE_UPDATED = 'PROFILE_UPDATED'
    PASSWORD_CHANGED = 'PASSWORD_CHANGED'
    PERMISSION_DENIED = 'PERMISSION_DENIED'
    USER_REGISTERED = 'USER_REGISTERED'
