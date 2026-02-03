from repository.users_repo import get_user_by_email, create_user
from utils.hashing import verify_password, hash_password
from services.activity_service import log_activity
from services.permission_service import load_user_permissions
from services.audit_service import log_action, AuditActions
import re

def authenticate_user(email, password):
    """Authenticate user with email and password."""
    # Input validation
    if not email or not password:
        raise ValueError("Email and password are required")
    
    # Clean inputs
    email = email.strip()
    password = password.strip()
    
    user = get_user_by_email(email)
    
    if not user:
        print(f"⚠️ Login attempt for non-existent user: {email}")
        return None
    
    # Check active status
    if not user.get('active_status', True):
        print(f"⚠️ Login attempt for deactivated account: {email}")
        raise ValueError("Account deactivated. Please contact administrator.")
        
    if verify_password(password, user['password_hash']):
        log_activity(user['id'], "LOGIN", f"User {user['full_name']} logged in")
        
        # Load permissions into session (RBAC)
        import streamlit as st
        st.session_state.user_role = user['role']
        st.session_state.user_id = user['id']
        st.session_state.org_id = user.get('org_id')
        load_user_permissions()
        
        # Audit log
        log_action(AuditActions.USER_LOGIN, f"Successful login from {email}")
        
        print(f"✅ Successful login: {email}")
        return user
    else:
        print(f"⚠️ Failed login attempt: {email} (incorrect password)")
        
    return None

def register_user(full_name, email, password, role='employee', org_name=None, org_id=None):
    """Register a new user with single-admin policy and organization support."""
    from repository.users_repo import count_admins, get_or_create_org, create_user as repo_create_user
    
    # Input validation
    if not full_name or not full_name.strip():
        return False, "Full name is required"
    
    if not email or not email.strip():
        return False, "Email is required"
    
    # Email format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Invalid email format"
    
    # Password strength validation
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # 🔴 GLOBAL ADMIN CHECK (Restored)
    if role == 'admin':
        admin_count = count_admins()
        if admin_count >= 1:
            return False, "System already has an Admin account. Only one global admin is allowed."
            
    # Organization Handling
    final_org_id = None
    if org_id:
        final_org_id = org_id
    elif org_name:
        try:
            final_org_id = get_or_create_org(org_name)
        except Exception as e:
            return False, f"Organization error: {str(e)}"
    
    # For now, if no org provided and not admin, default to a generic one or fail?
    # In this strict mode, we should require org. But for backward compatibility with existing calls...
    # If role is ADMIN, they typically define the org name.
    if not final_org_id and role == 'admin':
         # First admin defines the org
         if not org_name:
             # Fallback or error? Let's use 'My Organization' as default for first admin
             final_org_id = get_or_create_org("Primary Organization")
             
    if not final_org_id:
        # If still no org ID, use default 1 (migration created Default Org)
        # Check if default org exists (assumed ID 1 from migration)
        final_org_id = 1 

    # Check if exists
    if get_user_by_email(email):
        return False, "User with this email already exists"
        
    try:
        hashed = hash_password(password)
        # We need to import create_user from repo (renamed locally to avoid conflict)
        user_id = repo_create_user(full_name, email, hashed, role, org_id=final_org_id)
        print(f"✅ New user registered: {email} (ID: {user_id}, Role: {role}, Org: {final_org_id})")
        return True, "User registered successfully"
    except ValueError as ve:
        return False, str(ve)
    except Exception as e:
        print(f"❌ Registration error for {email}: {e}")
        return False, f"Registration failed: {str(e)}"
