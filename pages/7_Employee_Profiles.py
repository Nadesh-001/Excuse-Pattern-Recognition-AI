import streamlit as st
import pandas as pd
from utils.session import require_auth
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from repository.db import get_conn

# Page Config
st.set_page_config(page_title="Employee Profiles", page_icon="👥", layout="wide")
require_auth()
if st.session_state.role not in ['manager', 'admin']:
    st.error("⛔ Access Denied: Manager or Admin privileges required.")
    st.stop()

apply_custom_css()
render_sidebar(active_page="Employee Profiles")

st.title("👥 Employee Profiles")

conn = get_conn()
if not conn:
    st.error("Database connection failed")
    st.stop()

# Fetch only employees (not managers or admins)
df_employees = pd.read_sql("SELECT id, full_name, email, created_at FROM users WHERE role='employee'", conn)

if df_employees.empty:
    st.info("No employees found in the system.")
    conn.close()
    st.stop()

# Employee Selection
selected_emp_id = st.selectbox(
    "Select Employee",
    df_employees['id'].tolist(),
    format_func=lambda x: f"{df_employees[df_employees['id']==x]['full_name'].values[0]} - {df_employees[df_employees['id']==x]['email'].values[0]}"
)

if selected_emp_id:
    emp_data = df_employees[df_employees['id']==selected_emp_id].iloc[0]
    
    st.markdown(f"## 👤 {emp_data['full_name']}")
    st.caption(f"📧 {emp_data['email']} | Joined: {emp_data['created_at']}")
    
    st.divider()
    
    # Fetch employee statistics
    cursor = conn.cursor(dictionary=True)
    
    # Task stats
    cursor.execute("SELECT COUNT(*) as total FROM tasks WHERE assigned_to = %s", (selected_emp_id,))
    total_tasks = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as completed FROM tasks WHERE assigned_to = %s AND status='Completed'", (selected_emp_id,))
    completed_tasks = cursor.fetchone()['completed']
    
    cursor.execute("SELECT COUNT(*) as delayed FROM tasks WHERE assigned_to = %s AND status='Delayed'", (selected_emp_id,))
    delayed_tasks = cursor.fetchone()['delayed']
    
    cursor.execute("SELECT COUNT(*) as pending FROM tasks WHERE assigned_to = %s AND status='Pending'", (selected_emp_id,))
    pending_tasks = cursor.fetchone()['pending']
    
    # Delay stats
    cursor.execute("SELECT AVG(score_authenticity) as auth, AVG(score_avoidance) as avoid, COUNT(*) as delay_count FROM delays WHERE user_id = %s", (selected_emp_id,))
    delay_stats = cursor.fetchone()
    
    # Calculate metrics
    completion_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    avg_auth = int(delay_stats['auth'] or 0)
    avg_avoid = int(delay_stats['avoid'] or 0)
    
    # Risk level
    risk_level = "Low"
    risk_color = "#34D399"
    if avg_avoid > 60:
        risk_level = "High"
        risk_color = "#F87171"
    elif avg_avoid > 40:
        risk_level = "Medium"
        risk_color = "#FBBF24"
    
    # Display Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", total_tasks)
    col2.metric("Completion Rate", f"{completion_rate}%")
    col3.metric("Avg Authenticity", f"{avg_auth}%")
    col4.metric("Risk Level", risk_level)
    
    st.divider()
    
    # Task Breakdown
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📊 Task Status Breakdown")
        status_data = pd.DataFrame({
            'Status': ['Completed', 'Pending', 'Delayed'],
            'Count': [completed_tasks, pending_tasks, delayed_tasks]
        })
        st.dataframe(status_data, use_container_width=True)
    
    with col_b:
        st.subheader("🎯 Performance Summary")
        st.markdown(f"""
        - **Total Delays Submitted:** {delay_stats['delay_count']}
        - **Average Avoidance Score:** {avg_avoid}%
        - **Risk Assessment:** <span style="color: {risk_color}; font-weight: bold;">{risk_level}</span>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Employee Tasks
    st.subheader("📝 All Tasks")
    cursor.execute("SELECT id, title, status, priority, deadline, created_at FROM tasks WHERE assigned_to = %s ORDER BY created_at DESC", (selected_emp_id,))
    tasks = cursor.fetchall()
    
    if tasks:
        df_tasks = pd.DataFrame(tasks)
        st.dataframe(df_tasks, use_container_width=True)
        
        # Delete Tasks Section
        st.divider()
        with st.expander("🗑️ Delete Employee Tasks"):
            st.warning("⚠️ This action will permanently delete selected tasks!")
            
            task_to_delete = st.selectbox(
                "Select Task to Delete",
                df_tasks['id'].tolist(),
                format_func=lambda x: f"{df_tasks[df_tasks['id']==x]['title'].values[0]} (ID: {x})"
            )
            
            confirm = st.checkbox("I confirm deletion")
            
            if st.button("🗑️ Delete Task", type="primary", disabled=not confirm):
                try:
                    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_to_delete,))
                    conn.commit()
                    st.success("Task deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("No tasks assigned to this employee.")
    
    cursor.close()

conn.close()
