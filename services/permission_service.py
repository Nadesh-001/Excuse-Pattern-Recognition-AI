"""
Permission Service - RBAC Permission Management

Provides functions to:
- Load permissions for a role from database
- Check if current user has a permission
- Guard/protect pages and features
"""

import streamlit as st
from repository.db import get_conn

def get_permissions_for_role(role: str) -> set:
    """
    Load all permission codes for a given role from database.
    
    Args:
        role: Role name (employee, manager, admin)
        
    Returns:
        Set of permission codes
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT permission_code 
            FROM role_permissions 
            WHERE role = %s
        """, (role,))
        
        permissions = {row[0] for row in cursor.fetchall()}
        cursor.close()
        conn.close()
        
        return permissions
    except Exception as e:
        print(f"Error loading permissions: {e}")
        return set()


def load_user_permissions():
    """
    Load permissions for current user and store in session state.
    Should be called after login.
    """
    user_role = st.session_state.get('user_role', 'employee')
    st.session_state.permissions = get_permissions_for_role(user_role)


def has_permission(permission_code: str) -> bool:
    """
    Check if current user has a specific permission.
    
    Args:
        permission_code: Permission code to check (e.g., 'VIEW_ANALYTICS')
        
    Returns:
        True if user has permission, False otherwise
    """
    if 'permissions' not in st.session_state:
        load_user_permissions()
    
    return permission_code in st.session_state.get('permissions', set())


def require_permission(permission_code: str, error_message: str = None):
    """
    Guard function - stops page execution if user lacks permission.
    
    Args:
        permission_code: Required permission
        error_message: Optional custom error message
    """
    if not has_permission(permission_code):
        if error_message is None:
            error_message = f"⛔ Access Denied: You need '{permission_code}' permission to access this page."
        
        st.error(error_message)
        st.stop()


# Permission Constants (for easy reference)
class Permissions:
    VIEW_DASHBOARD = 'VIEW_DASHBOARD'
    VIEW_TASKS = 'VIEW_TASKS'
    CREATE_TASK = 'CREATE_TASK'
    EDIT_TASK = 'EDIT_TASK'
    DELETE_TASK = 'DELETE_TASK'
    VIEW_ANALYTICS = 'VIEW_ANALYTICS'
    MANAGE_EMPLOYEES = 'MANAGE_EMPLOYEES'
    ADMIN_PANEL = 'ADMIN_PANEL'
    VIEW_AUDIT_LOGS = 'VIEW_AUDIT_LOGS'
    EDIT_PROFILE = 'EDIT_PROFILE'
    MANAGE_ROLES = 'MANAGE_ROLES'
    USE_CHATBOT = 'USE_CHATBOT'
