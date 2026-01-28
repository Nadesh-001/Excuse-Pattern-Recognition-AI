import streamlit as st
import pandas as pd
from utils.helpers import init_session_state
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from database.connection import get_db_connection

# Page Config
st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")
init_session_state()
if not st.session_state.logged_in:
    st.switch_page("app.py")

apply_custom_css()
render_sidebar()

st.title("🔍 Universal Search")

# Search Bar
search_term = st.text_input("Search tasks, excuses, or analytics...", placeholder="e.g. 'server failure' or 'project alpha'")

# Filters
col1, col2, col3 = st.columns(3)
with col1:
    filter_type = st.multiselect("Type", ["Tasks", "Delays"], default=["Tasks", "Delays"])
with col2:
    filter_date = st.selectbox("Timeframe", ["All Time", "Today", "This Week", "This Month"])
with col3:
    filter_status = st.multiselect("Status/Risk", ["Pending", "Completed", "Delayed", "High Risk", "Low Risk"], default=[])

if search_term:
    conn = get_db_connection()
    results_found = False
    
    # 1. Search Tasks
    if "Tasks" in filter_type:
        st.subheader("Tasks")
        query_tasks = """
            SELECT * FROM tasks 
            WHERE (title LIKE %s OR description LIKE %s)
        """
        params_tasks = [f"%{search_term}%", f"%{search_term}%"]
        
        # Add basic role filtering (Employees see own, Managers see all)
        if st.session_state.user_role == 'employee':
            query_tasks += " AND assigned_to = %s"
            params_tasks.append(st.session_state.user_id)
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query_tasks, tuple(params_tasks))
        tasks = cursor.fetchall()
        
        if tasks:
            results_found = True
            for t in tasks:
                with st.expander(f"Task: {t['title']} ({t['status']})"):
                    st.write(t['description'])
                    st.caption(f"Deadline: {t['deadline']}")
        else:
            st.info("No matching tasks found.")

    # 2. Search Delays (Excuses)
    if "Delays" in filter_type:
        st.subheader("Delays & Patterns")
        query_delays = """
            SELECT d.*, t.title as task_title, u.full_name as user_name 
            FROM delays d 
            JOIN tasks t ON d.task_id = t.id 
            JOIN users u ON d.user_id = u.id
            WHERE d.reason_text LIKE %s
        """
        params_delays = [f"%{search_term}%"]
        
        if st.session_state.user_role == 'employee':
            query_delays += " AND d.user_id = %s"
            params_delays.append(st.session_state.user_id)
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query_delays, tuple(params_delays))
        delays = cursor.fetchall()
        
        if delays:
            results_found = True
            for d in delays:
                with st.expander(f"Excuse for '{d['task_title']}' - Risk: {d['risk_level']}"):
                    st.write(f"**Reason:** {d['reason_text']}")
                    st.write(f"**User:** {d['user_name']}")
                    st.progress(d['score_authenticity']/100, text=f"Authenticity: {d['score_authenticity']}%")
        else:
            st.info("No matching delay records found.")
            
    conn.close()
    
    if not results_found:
        st.warning("No results found matching your criteria.")

else:
    st.info("Enter a search term to begin.")
