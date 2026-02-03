import streamlit as st
import pandas as pd
from utils.session import require_auth
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from services.permission_service import require_permission, Permissions
from services.audit_service import log_action, AuditActions
from repository.users_repo import update_user
from utils.hashing import hash_password

# Page Config
st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")
require_auth()

apply_custom_css()
render_sidebar(active_page="Profile")

# Permission Check
require_permission(Permissions.EDIT_PROFILE)

st.title("👤 My Profile")

# Get current user
user_id = st.session_state.user_id
user_name = st.session_state.user_name
user_email = st.session_state.user_email
user_role = st.session_state.role

# Profile Information Card
st.markdown("""
<div class="dashboard-card" style="margin-bottom: 24px;">
    <div class="metric-label">ACCOUNT INFORMATION</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**User ID:**")
    st.code(user_id)
    
    st.markdown("**Full Name:**")
    new_name = st.text_input("", value=user_name, label_visibility="collapsed", key="profile_name")

with col2:
    st.markdown("**Email Address:**")
    st.text_input("", value=user_email, disabled=True, label_visibility="collapsed", help="Email cannot be changed")
    
    st.markdown("**Role:**")
    # Display role badge
    role_colors = {
        'admin': '#dc2626',
        'manager': '#7c3aed', 
        'employee': '#10b981'
    }
    role_color = role_colors.get(user_role, '#94a3b8')
    st.markdown(f"""
        <div style="
            background-color: {role_color}20;
            color: {role_color};
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
        ">{user_role}</div>
    """, unsafe_allow_html=True)

st.write("")

# Save Profile Button
if st.button("💾 Save Profile", type="primary"):
    if new_name and new_name != user_name:
        try:
            # Update user in database (need to add this function to users_repo)
            from repository.db import get_conn
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET full_name = %s WHERE id = %s",
                (new_name, user_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            # Update session
            st.session_state.user_name = new_name
            
            # Log action
            log_action(AuditActions.PROFILE_UPDATED, f"Name changed from '{user_name}' to '{new_name}'")
            
            st.success("✅ Profile updated successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error updating profile: {e}")
    else:
        st.info("No changes detected")

st.divider()

# Change Password Section
st.markdown("""
<div class="dashboard-card" style="margin-bottom: 24px;">
    <div class="metric-label">CHANGE PASSWORD</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    current_pw = st.text_input("Current Password", type="password", key="current_pw")
    new_pw = st.text_input("New Password", type="password", key="new_pw")

with col2:
    confirm_pw = st.text_input("Confirm New Password", type="password", key="confirm_pw")

if st.button("🔒 Change Password", type="secondary"):
    if not current_pw or not new_pw or not confirm_pw:
        st.error("All password fields are required")
    elif new_pw != confirm_pw:
        st.error("New passwords do not match")
    elif len(new_pw) < 6:
        st.error("Password must be at least 6 characters")
    else:
        try:
            # Verify current password
            from utils.hashing import verify_password
            from repository.users_repo import get_user_by_id
            
            user = get_user_by_id(user_id)
            
            if not verify_password(current_pw, user['password_hash']):
                st.error("Current password is incorrect")
            else:
                # Update password
                new_hash = hash_password(new_pw)
                
                conn = get_conn()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE id = %s",
                    (new_hash, user_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                
                # Log action
                log_action(AuditActions.PASSWORD_CHANGED, "Password changed successfully")
                
                st.success("✅ Password changed successfully!")
                
        except Exception as e:
            st.error(f"❌ Error changing password: {e}")

st.divider()

# Permissions Section
st.markdown("""
<div class="dashboard-card" style="margin-bottom: 24px;">
    <div class="metric-label">MY PERMISSIONS</div>
</div>
""", unsafe_allow_html=True)

permissions = st.session_state.get('permissions', set())

if permissions:
    # Create a nice grid display
    perm_list = sorted(list(permissions))
    cols = st.columns(3)
    
    for idx, perm in enumerate(perm_list):
        with cols[idx % 3]:
            st.markdown(f"""
                <div style="
                    background: #eff6ff;
                    border-left: 3px solid #2563eb;
                    padding: 8px 12px;
                    border-radius: 6px;
                    margin-bottom: 8px;
                    font-size: 0.85rem;
                    font-weight: 500;
                    color: #1e293b;
                ">
                    ✓ {perm.replace('_', ' ').title()}
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("No permissions loaded. Please log out and log in again.")
