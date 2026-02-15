"""
Permission Utility Functions
Provides centralized permission checking and role hierarchy validation
"""

def has_permission(user_role, action):
    """
    Central permission checking function.
    
    Args:
        user_role: User's role (employee/manager/admin)
        action: Action to check (e.g., 'create_task', 'view_all_tasks')
        
    Returns:
        Boolean indicating if role has permission for action
    
    Example:
        if has_permission(session.get('user_role'), 'create_task'):
            # Allow task creation
    """
    permissions = {
        'employee': [
            'view_own_tasks',
            'complete_task',
            'submit_delay',
            'use_chatbot',
            'view_own_analytics',
            'edit_own_profile'
        ],
        'manager': [
            'view_own_tasks',
            'view_team_tasks',
            'create_task',
            'assign_task',
            'complete_task',
            'submit_delay',
            'use_chatbot',
            'view_team_analytics',
            'export_reports',
            'view_employee_profiles',
            'edit_own_profile'
        ],
        'admin': ['*']  # All permissions
    }
    
    user_permissions = permissions.get(user_role, [])
    return '*' in user_permissions or action in user_permissions


def role_hierarchy_check(required_role, user_role):
    """
    Check if user role meets minimum requirement using hierarchy.
    Useful for routes requiring "at least manager" access.
    
    Args:
        required_role: Minimum role required ('employee', 'manager', or 'admin')
        user_role: User's current role
        
    Returns:
        Boolean indicating if user role meets or exceeds required role
        
    Example:
        if role_hierarchy_check('manager', session.get('user_role')):
            # User is manager or admin
    """
    hierarchy = {
        'employee': 1,
        'manager': 2,
        'admin': 3
    }
    return hierarchy.get(user_role, 0) >= hierarchy.get(required_role, 0)


def check_task_ownership(task_id, user_id, user_role):
    """
    Check if user can access a specific task.
    
    Args:
        task_id: Task ID to check
        user_id: Current user ID  
        user_role: Current user role
        
    Returns:
        Boolean indicating access permission
        
    Example:
        if not check_task_ownership(task_id, session['user_id'], session.get('user_role')):
            return redirect(url_for('tasks'))
    """
    from repository.tasks_repo import get_task_by_id
    
    task = get_task_by_id(task_id)
    if not task:
        return False
    
    # Admins can access everything
    if user_role == 'admin':
        return True
    
    # Managers can access all tasks (or team tasks if org-based)
    if user_role == 'manager':
        return True
    
    # Employees can only access their own assigned tasks
    return task['assigned_to'] == user_id
