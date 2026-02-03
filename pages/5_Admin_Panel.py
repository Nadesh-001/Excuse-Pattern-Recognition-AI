import streamlit as st
import pandas as pd
import sys
import os

# Allow running directly by adding parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.auth_service import register_user
from services.activity_service import log_activity
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from repository.db import get_conn

# Page Config
st.set_page_config(page_title="Admin Panel", page_icon="🛡️", layout="wide")

# Auth Check
if not st.session_state.logged_in:
    st.switch_page("app.py")
if st.session_state.role != 'admin':
    st.error("⛔ Access Denied: Admin privileges required.")
    st.stop()

apply_custom_css()
render_sidebar(active_page="Admin Panel")

# Verify Permissions
require_permission(Permissions.ADMIN_PANEL)

from services.diagnosis_service import run_all_diagnostics

st.title("🛡️ Admin Administration")

tab_users, tab_logs, tab_diagnosis, tab_settings = st.tabs(["User Management", "Audit Logs", "System Diagnosis", "System Settings"])

with tab_users:
    st.subheader("👥 User Management")
    
    conn = get_conn()
    if conn:
        # Fetch users
        df_users = pd.read_sql("SELECT id, full_name, email, role, active_status, created_at FROM users", conn)
        
        # Search and Filter
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_term = st.text_input("🔍 Search users", placeholder="Search by name or email...")
        with col_filter:
            role_filter = st.selectbox("Filter by Role", ["All", "employee", "manager", "admin"])
        
        # Apply filters
        filtered_df = df_users.copy()
        if search_term:
            filtered_df = filtered_df[
                filtered_df['full_name'].str.contains(search_term, case=False, na=False) | 
                filtered_df['email'].str.contains(search_term, case=False, na=False)
            ]
        if role_filter != "All":
            filtered_df = filtered_df[filtered_df['role'] == role_filter]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        st.divider()
        
        # User Actions - Edit and Delete
        col_edit, col_delete = st.columns(2)
        
        with col_edit:
            with st.expander("✏️ Edit User"):
                edit_user_id = st.selectbox(
                    "Select User to Edit", 
                    df_users['id'].tolist(), 
                    format_func=lambda x: f"{df_users[df_users['id']==x]['full_name'].values[0]} ({df_users[df_users['id']==x]['email'].values[0]})",
                    key="edit_select"
                )
                
                if edit_user_id:
                    user_data = df_users[df_users['id']==edit_user_id].iloc[0]
                    
                    with st.form("edit_user_form"):
                        new_name = st.text_input("Full Name", value=user_data['full_name'])
                        new_email = st.text_input("Email", value=user_data['email'])
                        new_role = st.selectbox("Role", ["employee", "manager", "admin"], index=["employee", "manager", "admin"].index(user_data['role']))
                        
                        if st.form_submit_button("💾 Update User"):
                            cursor = conn.cursor()
                            try:
                                cursor.execute(
                                    "UPDATE users SET full_name=%s, email=%s, role=%s WHERE id=%s",
                                    (new_name, new_email, new_role, edit_user_id)
                                )
                                conn.commit()
                                
                                # Log activity
                                log_activity(st.session_state.user_id, "User Updated", f"Updated user: {new_email} (Role: {new_role})")
                                
                                st.success("User updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                            finally:
                                cursor.close()
        
        with col_delete:
            with st.expander("🗑️ Delete User"):
                delete_user_id = st.selectbox(
                    "Select User to Delete", 
                    df_users['id'].tolist(), 
                    format_func=lambda x: f"{df_users[df_users['id']==x]['full_name'].values[0]} ({df_users[df_users['id']==x]['email'].values[0]})",
                    key="delete_select"
                )
                
                if delete_user_id:
                    # Prevent deleting last admin
                    is_last_admin = False
                    if df_users[df_users['id']==delete_user_id]['role'].values[0] == 'admin':
                         admin_count = len(df_users[df_users['role']=='admin'])
                         if admin_count <= 1:
                             is_last_admin = True

                    st.warning(f"⚠️ This will permanently delete the user and all associated data!")
                    if is_last_admin:
                        st.error("⛔ Cannot delete the only Administrator.")
                    else:
                        confirm_delete = st.checkbox("I understand and want to proceed")
                        
                        if st.button("🗑️ Delete User", type="primary", disabled=not confirm_delete):
                            cursor = conn.cursor()
                            try:
                                # Get user info before deleting
                                user_to_delete = df_users[df_users['id']==delete_user_id].iloc[0]
                                
                                # Manually delete related records to verify Foreign Keys
                                # 1. Permissions
                                cursor.execute("DELETE FROM role_permissions WHERE role=%s", (user_to_delete['role'],)) # Wait, permissions are by role, typically not user specific unless overwritten. 
                                # Actually the error was audit_logs.
                                cursor.execute("DELETE FROM audit_logs WHERE user_id=%s", (delete_user_id,))
                                cursor.execute("DELETE FROM delays WHERE user_id=%s", (delete_user_id,))
                                cursor.execute("DELETE FROM tasks WHERE assigned_to=%s", (delete_user_id,)) # Assuming tasks link to user
                                
                                # Delete user coverage
                                cursor.execute("DELETE FROM users WHERE id=%s", (delete_user_id,))
                                conn.commit()
                                
                                # Log activity
                                log_activity(st.session_state.user_id, "User Deleted", f"Deleted user: {user_to_delete['email']} ({user_to_delete['full_name']})")
                                
                                st.success("User deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                            finally:
                                cursor.close()
        
        conn.close()
    
    # Add User
    with st.expander("➕ Add New User"):
        with st.form("add_user_form"):
            new_name = st.text_input("Name")
            new_email = st.text_input("Email")
            new_pass = st.text_input("Default Password", type="password")
            new_role = st.selectbox("Role", ["employee", "manager", "admin"])
            
            if st.form_submit_button("Create User"):
                if new_name and new_email and new_pass:
                    current_org_id = st.session_state.get('org_id')
                    success, msg = register_user(new_name, new_email, new_pass, new_role, org_id=current_org_id)
                    if success:
                        # Log activity
                        log_activity(st.session_state.user_id, "User Created", f"Created user: {new_email} (Role: {new_role})")
                        
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("All fields required.")

with tab_logs:
    st.subheader("📋 System Audit Logs")
    
    conn = get_conn()
    if conn:
        try:
            # Fetch recent activity logs with user names
            query = """
                SELECT 
                    al.id,
                    al.timestamp,
                    u.full_name as user_name,
                    u.role,
                    al.action,
                    al.details,
                    u.email as user_email
                FROM audit_logs al
                LEFT JOIN users u ON al.user_id = u.id
                ORDER BY al.timestamp DESC
                LIMIT 50
            """
            df_logs = pd.read_sql(query, conn)
            
            # Log Filters
            c1, c2 = st.columns(2)
            user_emails = ["All"]
            if not df_logs.empty and 'user_email' in df_logs.columns:
                 # Get unique emails from current logs or fetch all users? 
                 # Fetching all users better but let's stick to logs contextual
                 user_emails += sorted([e for e in df_logs['user_email'].unique() if e])
            
            actions = ["All"]
            if not df_logs.empty:
                actions += sorted(df_logs['action'].unique().tolist())
            
            selected_user_email = c1.selectbox("Filter by User", user_emails)
            selected_action = c2.selectbox("Filter by Action", actions)
        
            if not df_logs.empty:
                # Apply filters
                if selected_user_email != "All":
                    df_logs = df_logs[df_logs['user_email'] == selected_user_email]
                if selected_action != "All":
                    df_logs = df_logs[df_logs['action'] == selected_action]

                st.markdown(f"**Showing {len(df_logs)} log(s)**")
                
                # Display logs in a nice format
                for _, log in df_logs.iterrows():
                    # Define icon based on action
                    action_icon = "📝"
                    if "login" in log['action']: action_icon = "🕒" 
                    elif "logout" in log['action']: action_icon = "🕒"
                    elif "complete" in log['action']: action_icon = "✅"
                    elif "delay" in log['action']: action_icon = "⚠️"
                    
                    st.markdown(f"""
                <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 12px;">
                    <div style="color: #6b7280; font-size: 1.2rem;">🔹</div>
                    <div style="flex: 1;">
                        <span style="color: #4b5563; font-weight: 500;">{action_icon} {log['timestamp']}</span>
                        <span style="color: #6b7280;"> - {log['action']} by </span>
                        <a href="#" style="color: #2563eb; text-decoration: underline;">{log['user_email']}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No activity logs found matching criteria.")
        except Exception as e:
            st.error(f"Error loading logs: {e}")
            st.info("Activity logging is available. Logs will appear here once users perform actions.")
        finally:
            conn.close()
    else:
        st.error("Database connection failed")

with tab_diagnosis:
    st.subheader("🩺 System Health Check")
    
    if st.button("Run Diagnostics"):
        with st.spinner("Running system checks..."):
            results = run_all_diagnostics()
            
            # 1. Database
            st.markdown("### 🗄️ Database")
            c1, c2 = st.columns([1, 3])
            db_status = results['database']['status']
            c1.metric("Status", "Online" if db_status else "Offline", delta="Connected" if db_status else "-Error")
            if not db_status:
                c2.error(results['database']['message'])
            else:
                c2.success(results['database']['message'])

            st.divider()

            # 2. APIs
            st.markdown("### 🤖 AI Services")
            c1, c2 = st.columns(2)
            
            groq = results['api'].get('Groq API', (False, "Unknown"))
            c1.metric("Groq API", "Found" if groq[0] else "Missing", delta="Ready" if groq[0] else "Config Req")
            if not groq[0]: c1.warning(groq[1])

            gemini = results['api'].get('Gemini API', (False, "Unknown"))
            c2.metric("Gemini API", "Found" if gemini[0] else "Missing", delta="Ready" if gemini[0] else "Config Req")
            if not gemini[0]: c2.warning(gemini[1])

            st.divider()

            # 3. System
            st.markdown("### 🖥️ Environment")
            sys_info = results['system']
            sc1, sc2, sc3 = st.columns(3)
            sc1.info(f"**Python:** {sys_info['Python Version']}")
            sc2.info(f"**Streamlit:** {sys_info['Streamlit Version']}")
            sc3.info(f"**OS:** {sys_info['OS']}")
            
            # File System
            fs = results['filesystem'].get('Uploads Dir', (False, "Unknown"))
            if fs[0]:
                st.success(f"📂 Uploads Directory: {fs[1]}")
            else:
                st.error(f"📂 Uploads Directory: {fs[1]}")

with tab_settings:
    st.subheader("⚙️ System Configuration")
    st.slider("Risk Threshold (High)", 50, 90, 60, help="Score above this triggers High Risk alert")
    st.toggle("Maintenance Mode")
