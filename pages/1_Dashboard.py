import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.session import require_auth
from services.analytics_service import get_analytics_data
from services.task_service import service_get_tasks, service_submit_delay, service_complete_task
from services.ai_service import get_ai_response
from utils.time_utils import calculate_time_status, get_elapsed_str
from components.styling import apply_custom_css
from components.sidebar import render_sidebar

# Page Config
st.set_page_config(page_title="Dashboard", page_icon="🚀", layout="wide")
require_auth()

apply_custom_css()
render_sidebar(active_page="Dashboard")

# --- Data Fetching ---
# Analytics Data
# This returns (df_delays, df_tasks) usually
analytics_data = get_analytics_data()
df_delays = analytics_data[0] if analytics_data else None
df_tasks_all = analytics_data[1] if analytics_data else None

# User specific data
user_id = st.session_state.user_id
user_role = st.session_state.role

# Initialize user_tasks_df
user_tasks_df = None
if df_tasks_all is not None and not df_tasks_all.empty and user_role == 'employee' and 'assigned_to' in df_tasks_all.columns:
    user_tasks_df = df_tasks_all[df_tasks_all['assigned_to'] == user_id]

# Calculate Stats
counts = {'pending': 0, 'delayed': 0, 'auth_score': 0, 'total_delays': 0, 'high_risk': 0}

if df_tasks_all is not None and not df_tasks_all.empty:
    if user_role == 'employee':
        if user_tasks_df is not None:
            counts['pending'] = len(user_tasks_df[user_tasks_df['status'] == 'Pending'])
            counts['delayed'] = len(user_tasks_df[user_tasks_df['status'] == 'Delayed'])
    else:
        counts['pending'] = len(df_tasks_all[df_tasks_all['status'] == 'Pending'])

if df_delays is not None and not df_delays.empty:
    if user_role == 'employee':
        user_delays = df_delays[df_delays['user_id'] == user_id]
        counts['auth_score'] = round(user_delays['score_authenticity'].mean(), 1) if not user_delays.empty else 0
    else:
        counts['total_delays'] = len(df_delays)
        counts['high_risk'] = len(df_delays[df_delays['risk_level'] == 'High'])

# --- New Experimental Dashboard Layout ---

# 1. Header Section (Welcome + Search/Actions)
st.markdown(f"""
<div class="welcome-card">
    <div style="display: flex; justify-content: space-between; align-items: start;">
        <div>
            <h1 style="margin: 0; font-size: 2.5rem;">Welcome, {st.session_state.user_name.split()[0]}!</h1>
            <p style="margin-top: 8px; font-size: 1.1rem; opacity: 0.9;">
                You have <b>{counts['pending']} pending tasks</b> today.
            </p>
        </div>
        <div style="text-align: right; background: rgba(255,255,255,0.2); padding: 12px 20px; border-radius: 16px; backdrop-filter: blur(10px);">
             <div style="font-size: 0.9rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 0.05em;">Efficiency</div>
             <div style="font-size: 1.8rem; font-weight: 800;">{counts.get('auth_score', 98)}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Main Content Grid (Left: 2/3 Tasks/Charts, Right: 1/3 Widgets)
c_main, c_side = st.columns([2.2, 1])

with c_main:
    # --- Quick Stats Row ---
    st.markdown("### 📊 Overview")
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="dashboard-card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">📋</div>
            <div class="metric-value">{len(user_tasks_df) if user_tasks_df is not None else 0}</div>
            <div class="metric-label">Total Tasks</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="dashboard-card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">⏳</div>
            <div class="metric-value" style="color: #f59e0b;">{counts['pending']}</div>
            <div class="metric-label">Pending</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="dashboard-card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">✅</div>
            <div class="metric-value" style="color: #10b981;">{len(user_tasks_df[user_tasks_df['status'] == 'Completed']) if user_tasks_df is not None else 0}</div>
            <div class="metric-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("") # Spacer

    # --- Active Tasks List (Mimicking "Main Task" cards) ---
    st.markdown("### 📝 Active Tasks")
    
    if user_tasks_df is not None and not user_tasks_df.empty:
        pending_tasks = user_tasks_df[user_tasks_df['status'] == 'Pending']
        if not pending_tasks.empty:
            for i, task in pending_tasks.head(5).iterrows():
                # Color code based on priority
                prio_colors = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}
                prio_bg = prio_colors.get(task['priority'], "#cbd5e1")
                
                st.markdown(f"""
                <div class="dashboard-card" style="padding: 0; margin-bottom: 16px; overflow: hidden; display: flex; flex-direction: column;">
                    <div style="padding: 20px; border-left: 6px solid {prio_bg};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; font-size: 1.1rem; color: #334155;">{task['title']}</h4>
                                <p style="margin: 4px 0 0 0; font-size: 0.9rem; color: #94a3b8;">
                                    Deadline: {task['deadline']} • Est: {task['estimated_minutes']}m
                                </p>
                            </div>
                            <div>
                                <span style="background: {prio_bg}20; color: {prio_bg}; padding: 6px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem;">
                                    {task['priority']}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action Buttons inside a container for proper Streamlit alignment
                # We use a container to keep it "inside" the conceptual card area
                # (Streamlit doesn't allow embedding buttons in HTML)
        else:
            st.info("🎉 No pending tasks! You're all caught up.")
    else:
        st.info("No tasks found.")

with c_side:
    # --- Right Sidebar Widgets (Plan, Efficiency, Team) ---
    
    # 1. Action Menu
    st.markdown("""
    <div class="dashboard-card" style="margin-bottom: 24px;">
        <div class="metric-label">Actions</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ New Task", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Tasks.py")
        
    st.write("")
    st.write("")

    # 2. Efficiency / Authenticity Widget
    st.markdown(f"""
    <div class="dashboard-card" style="margin-bottom: 24px;">
        <div class="metric-label">Avg Authenticity</div>
        <div style="height: 150px; display: flex; align-items: center; justify-content: center;">
             <!-- Circular Progress Placeholder -->
             <div style="width: 120px; height: 120px; border-radius: 50%; border: 12px solid #f1f5f9; border-top-color: #3b82f6; display: flex; align-items: center; justify-content: center;">
                 <div style="font-size: 1.5rem; font-weight: 800; color: #1e293b;">{counts.get('auth_score', 0)}%</div>
             </div>
        </div>
        <p style="text-align: center; font-size: 0.8rem; margin-top: 10px;">Based on your delay reasons</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. AI Insights Widget
    st.markdown("""
    <div class="dashboard-card">
        <div class="metric-label">AI Insights</div>
        <div class="task-row">
            <div class="task-icon" style="background: #eff6ff; color: #3b82f6;">💡</div>
            <div style="font-size: 0.9rem;">Delay patterns allow for <b>15%</b> optimization.</div>
        </div>
        <div class="task-row">
            <div class="task-icon" style="background: #f0fdf4; color: #10b981;">📈</div>
            <div style="font-size: 0.9rem;">Productivity up by <b>5%</b> this week.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #cbd5e1; font-size: 0.8rem;">Excuse Pattern Recognition AI • v1.0</div>', unsafe_allow_html=True)

