from repository.users_repo import get_all_users, update_user, delete_user, get_user_by_email, create_user
from utils.hashing import hash_password
from services.activity_service import log_activity

def get_users_list(current_user_role):
    if current_user_role != 'admin':
        raise PermissionError("Access denied")
    return get_all_users()

def manage_update_user(admin_id, target_user_id, full_name, email, role, active_status):
    update_user(target_user_id, full_name, email, role, active_status)
    log_activity(admin_id, "UPDATE_USER", f"Updated user {email} (Role: {role}, Active: {active_status})")

def manage_delete_user(admin_id, target_user_id, target_email):
    delete_user(target_user_id)
    log_activity(admin_id, "DELETE_USER", f"Deleted user {target_email}")

def manage_create_user(admin_id, full_name, email, password, role):
    if get_user_by_email(email):
        return False, "User already exists"
    
    hashed = hash_password(password)
    create_user(full_name, email, hashed, role)
    log_activity(admin_id, "CREATE_USER", f"Created user {email} ({role})")
    return True, "User created successfully"
