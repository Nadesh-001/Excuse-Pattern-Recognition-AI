import streamlit as st
import pandas as pd
from datetime import datetime
from utils.session import require_auth
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from services.permission_service import require_permission, Permissions
from services.audit_service import get_audit_logs

# Page Config
st.set_page_config(page_title="Audit Logs", page_icon="📜", layout="wide")
require_auth()

apply_custom_css()
render_sidebar(active_page="Audit Logs")

# Admin-only access
require_permission(Permissions.VIEW_AUDIT_LOGS)

st.title("📜 System Audit Logs")

st.markdown("""
View all system activities and security events. Audit logs track user logins, role changes, 
profile updates, and other sensitive actions.
""")

st.divider()

# Filters
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    action_filter = st.text_input("🔍 Filter by action", placeholder="e.g., LOGIN, ROLE_CHANGED")

with col2:
    limit = st.number_input("Show records", min_value=10, max_value=500, value=100, step=10)

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.write("")

# Fetch audit logs
logs = get_audit_logs(limit=limit, action_filter=action_filter if action_filter else None)

if logs:
    # Convert to DataFrame for better display
    df = pd.DataFrame(logs)
    
    # Format timestamp
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Reorder columns
    column_order = ['timestamp', 'user_name', 'email', 'action', 'details']
    df = df[[col for col in column_order if col in df.columns]]
    
    # Rename for display
    df.columns = ['Timestamp', 'User', 'Email', 'Action', 'Details']
    
    # Display stats
    st.markdown("### 📊 Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        unique_users = df['User'].nunique()
        st.metric("Unique Users", unique_users)
    
    with col3:
        unique_actions = df['Action'].nunique()
        st.metric("Action Types", unique_actions)
    
    with col4:
        login_count = len(df[df['Action'].str.contains('LOGIN', na=False)])
        st.metric("Login Events", login_count)
    
    st.divider()
    
    # Display table
    st.markdown("### 📋 Audit Trail")
    
    st.dataframe(
        df,
        use_container_width=True,
        height=500,
        hide_index=True
    )
    
    # Download option
    st.download_button(
        label="📥 Download as CSV",
        data=df.to_csv(index=False),
        file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
else:
    st.info("No audit logs found matching your criteria.")

st.divider()

# Action Legend
with st.expander("ℹ️ Action Types Reference"):
    st.markdown("""
    **Common Audit Actions:**
    - **USER_LOGIN**: User successfully logged in
    - **USER_LOGOUT**: User logged out
    - **USER_REGISTERED**: New user account created
    - **ROLE_CHANGED**: Admin changed a user's role
    - **PROFILE_UPDATED**: User updated their profile
    - **PASSWORD_CHANGED**: User changed their password
    - **TASK_CREATED**: New task created
    - **TASK_DELETED**: Task deleted
    - **PERMISSION_DENIED**: Failed authorization attempt
    """)
