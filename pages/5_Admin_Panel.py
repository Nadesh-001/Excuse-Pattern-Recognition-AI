import streamlit as st
import pandas as pd
import sys
import os

# Allow running directly by adding parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.helpers import init_session_state, signup_user
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from database.connection import get_db_connection

# Page Config
st.set_page_config(page_title="Admin Panel", page_icon="🛡️", layout="wide")
init_session_state()

# Auth Check
if not st.session_state.logged_in:
    st.switch_page("app.py")
if st.session_state.user_role != 'admin':
    st.error("⛔ Access Denied: Admin privileges required.")
    st.stop()

apply_custom_css()
render_sidebar()

st.title("🛡️ Admin Administration")

tab_users, tab_logs, tab_settings = st.tabs(["User Management", "Audit Logs", "System Settings"])

with tab_users:
    st.subheader("Manage Users")
    
    st.subheader("Manage Users")
    
    conn = get_db_connection()
    if conn:
        # Fetch clean dataframe
        df_users = pd.read_sql("SELECT id, full_name, email, role, created_at FROM users", conn)
        
        # User Selection for Profile View
        start_col, end_col = st.columns([1, 2])
        with start_col:
            selected_user_id = st.selectbox("Select Employee to View Profile", df_users['id'].tolist(), format_func=lambda x: df_users[df_users['id']==x]['full_name'].values[0])
        
        if selected_user_id:
            cursor = conn.cursor(dictionary=True)
            # Get Stats
            cursor.execute("SELECT COUNT(*) as total FROM tasks WHERE assigned_to = %s", (selected_user_id,))
            total_tasks = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as delayed FROM tasks WHERE assigned_to = %s AND status='Delayed'", (selected_user_id,))
            total_delayed = cursor.fetchone()['delayed']
            
            cursor.execute("SELECT AVG(score_authenticity) as auth, AVG(score_avoidance) as avoid FROM delays WHERE user_id = %s", (selected_user_id,))
            scores = cursor.fetchone()
            
            # Risk Calc
            risk_label = "Low"
            if scores['avoid'] and scores['avoid'] > 60: risk_label = "High"
            elif scores['avoid'] and scores['avoid'] > 40: risk_label = "Medium"
            
            # Display Profile Card
            with end_col:
                st.markdown(f"### 👤 Profile: {df_users[df_users['id']==selected_user_id]['full_name'].values[0]}")
                m1, m2, m3 = st.columns(3)
                m1.metric("Reliability", f"{int(((total_tasks-total_delayed)/total_tasks)*100) if total_tasks else 100}%")
                m2.metric("Avg Authenticity", f"{int(scores['auth'] or 0)}%")
                m3.metric("Risk Level", risk_label, delta_color="inverse")
                
                st.caption(f"Email: {df_users[df_users['id']==selected_user_id]['email'].values[0]}")
                st.caption(f"Role: {df_users[df_users['id']==selected_user_id]['role'].values[0]}")

        st.divider()
        st.dataframe(df_users, use_container_width=True)
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
                    success, msg = signup_user(new_name, new_email, new_pass, new_role)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("All fields required.")

with tab_logs:
    st.subheader("System Audit Logs")
    # Placeholder for audit logs table
    st.info("System logs will appear here (Database Table: audit_logs)")

with tab_settings:
    st.subheader("AI Configuration")
    st.slider("Risk Threshold (High)", 50, 90, 60, help="Score above this triggers High Risk alert")
    st.toggle("Maintenance Mode")
