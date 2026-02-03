from .db import get_conn
import mysql.connector
import re

def count_admins():
    """Count total number of admins in the system."""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()

def get_or_create_org(org_name):
    """Get organization ID by name, or create if not exists."""
    if not org_name:
        return None
        
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        # Check if exists
        cursor.execute("SELECT id FROM organizations WHERE name=%s", (org_name,))
        result = cursor.fetchone()
        
        if result:
            return result['id']
            
        # Create new
        cursor.execute("INSERT INTO organizations (name) VALUES (%s)", (org_name,))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def create_user(full_name, email, password_hash, role='employee', org_id=None):
    """Create a new user with validation."""
    # Input validation
    if not full_name or not full_name.strip():
        raise ValueError("Full name cannot be empty")
    if not email or not email.strip():
        raise ValueError("Email cannot be empty")
    
    # Email format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValueError("Invalid email format")
    
    # Role validation
    valid_roles = ['employee', 'manager', 'admin']
    if role not in valid_roles:
        raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash, role, org_id) VALUES (%s, %s, %s, %s, %s)",
            (full_name.strip(), email.strip().lower(), password_hash, role, org_id)
        )
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.IntegrityError as e:
        if 'Duplicate entry' in str(e):
            raise ValueError(f"User with email {email} already exists")
        raise
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to create user: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_user_by_email(email):
    """Get user by email address."""
    if not email:
        return None
    
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email.strip().lower(),))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user by email: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_all_users(active_only=False):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT id, full_name, email, role, active_status, created_at FROM users"
        if active_only:
            sql += " WHERE active_status = TRUE"
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def update_user(user_id, full_name, email, role, active_status):
    """Update user information with validation."""
    # Validation
    if not user_id:
        raise ValueError("User ID is required")
    if not full_name or not full_name.strip():
        raise ValueError("Full name cannot be empty")
    
    valid_roles = ['employee', 'manager', 'admin']
    if role not in valid_roles:
        raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET full_name=%s, email=%s, role=%s, active_status=%s WHERE id=%s",
            (full_name.strip(), email.strip().lower(), role, active_status, user_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"User with ID {user_id} not found")
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to update user: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def delete_user(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
