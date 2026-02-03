import streamlit as st
import pandas as pd
from datetime import date, datetime
from utils.session import require_auth
from services.task_service import service_create_task, service_get_tasks, service_submit_delay, service_complete_task
from services.user_service import get_users_list
from utils.time_utils import calculate_time_status
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from repository.resources_repo import get_resources_by_task, log_resource_access
import os
import json

# Page Config
st.set_page_config(page_title="Task Management", page_icon="📝", layout="wide")
require_auth()

apply_custom_css()
render_sidebar(active_page="Tasks")

st.title("Task Management")

# --- Manager: Create Task ---
if st.session_state.role in ['manager', 'admin']:
    with st.expander("➕ Create New Task"):
        with st.form("new_task"):
            t_title = st.text_input("Title")
            t_desc = st.text_area("Description")
            
            # User Selection
            users = get_users_list('admin') # Managers call this too
            # Filter for employees ideally, but all users ok for now
            user_options = {u['full_name']: u['id'] for u in users}
            selected_user_name = st.selectbox("Assign to", options=list(user_options.keys()))
            t_assign_id = user_options[selected_user_name] if user_options else None

            t_deadline = st.date_input("Deadline")
            t_prio = st.selectbox("Priority", ["Low", "Medium", "High"])
            
            col_time1, col_time2 = st.columns(2)
            with col_time1:
                t_est_hours = st.number_input("Est. Hours", min_value=0, max_value=999, value=0)
            with col_time2:
                t_est_mins = st.number_input("Est. Minutes", min_value=0, max_value=59, step=15, value=0)

            # Attachments
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                t_files = st.file_uploader("Attach Files (PDF, DOCX)", accept_multiple_files=True, type=['pdf', 'docx', 'txt'])
            with col_res2:
                t_link_str = st.text_input("Attach URL (Optional)")

            if st.form_submit_button("Create Task"):
                if t_title and t_assign_id:
                    links = [t_link_str] if t_link_str else []
                    
                    service_create_task(
                        manager_id=st.session_state.user_id,
                        title=t_title, 
                        description=t_desc, 
                        assigned_to=t_assign_id, 
                        priority=t_prio, 
                        deadline=t_deadline, 
                        est_hours=t_est_hours, 
                        est_minutes=t_est_mins,
                        links=links,
                        files=t_files # Helper logic in service needs to handle files or pass
                    )
                    st.success(f"Task '{t_title}' created successfully!")
                    st.rerun()
                else:
                    st.warning("Title and Assignee are required")

# --- View Tasks ---
st.subheader("My Tasks")

# Search and Filter
col_search, col_filter, col_prio = st.columns([2, 1, 1])
search_query = col_search.text_input("🔍 Search tasks...", label_visibility="collapsed", placeholder="Search tasks...")
status_filter = col_filter.selectbox("Status", ["All", "Pending", "Completed"], label_visibility="collapsed")
prio_filter = col_prio.selectbox("Priority", ["All", "High", "Medium", "Low"], label_visibility="collapsed")

tasks = service_get_tasks(st.session_state.user_id, st.session_state.role)

if tasks:
    # Filter in Python (ideal would be SQL but this is fine for now)
    if search_query:
        tasks = [t for t in tasks if search_query.lower() in t['title'].lower()]
    if status_filter != "All":
        tasks = [t for t in tasks if t['status'] == status_filter]
    if prio_filter != "All":
        tasks = [t for t in tasks if t['priority'] == prio_filter]

    st.markdown(f"**Showing {len(tasks)} task(s)**")

    for task in tasks:
        # Task Card Container
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card" style="padding: 24px; margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0; color: #0f172a; font-size: 1.5rem;">{task['title']}</h3>
                        <p style="color: #64748b; margin-top: 8px;">{task['description'] or 'No description provided'}</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {'rgba(16, 185, 129, 0.2)' if task['status']=='Completed' else 'rgba(251, 146, 60, 0.2)' if task['status']=='Completed Over Time' else 'rgba(239, 68, 68, 0.2)' if task['status']=='Delayed' else 'rgba(59, 130, 246, 0.2)'}; 
                                     color: {'#10b981' if task['status']=='Completed' else '#fb923c' if task['status']=='Completed Over Time' else '#ef4444' if task['status']=='Delayed' else '#60a5fa'}; 
                                     padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                            { '✅ Completed' if task['status']=='Completed' else '🟠 Completed Over Time' if task['status']=='Completed Over Time' else '🔴 Delayed' if task['status']=='Delayed' else '⏳ Pending' }
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metadata Row (Outside the HTML block for Streamlit widgets if needed, but styling better inside? 
            # Combining Streamlit columns for layout)
            
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                prio_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}.get(task['priority'], "#9ca3af")
                st.markdown(f"**Priority:** <span style='color:{prio_color}; font-weight:800'>● {task['priority']}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**Deadline:** {task['deadline']}")
            with c3:
                # Need email or name. service_get_tasks returns joined columns assigned_to_email
                assigned = task.get('assigned_to_email', 'Unknown')
                st.markdown(f"**Assigned to:** [{assigned}](mailto:{assigned})")

            st.write("") # Spacer

            # Metrics Row (Estimated, Elapsed, Status)
            m1, m2, m3 = st.columns(3)
            
            with m1:
                # Estimated
                est_hour_str = f"{task['estimated_minutes'] // 60}h {task['estimated_minutes'] % 60}m" if task['estimated_minutes'] else "N/A"
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="color: #60a5fa; font-size: 0.8rem; font-weight: 600; margin-bottom: 4px;">⏱️ Estimated</div>
                    <div style="color: #93c5fd; font-size: 1.2rem; font-weight: 700;">{est_hour_str}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m2:
                # Elapsed (Yellow Card)
                # Need to calculate elapsed string
                from utils.time_utils import get_elapsed_str, calculate_time_status
                elapsed_txt = get_elapsed_str(task['created_at'])
                st.markdown(f"""
                <div style="background: rgba(253, 224, 71, 0.1); border: 1px solid #facc15; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="color: #ca8a04; font-size: 0.8rem; font-weight: 600; margin-bottom: 4px;">⏱️ Elapsed</div>
                    <div style="color: #facc15; font-size: 1.2rem; font-weight: 700;">{elapsed_txt}</div>
                </div>
                """, unsafe_allow_html=True)

            with m3:
                # Status / Details Button
                # We can put the button here or a status summary
                time_status, color = calculate_time_status(task['status'], task['created_at'], task['estimated_minutes'])
                if time_status:
                     st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; text-align: center;">
                        <div style="color: #9ca3af; font-size: 0.8rem; font-weight: 600; margin-bottom: 4px;">📊 Status</div>
                        <div style="color: {color}; font-size: 0.9rem; font-weight: 600;">{time_status}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Action Button
            if st.button("View Details & Actions", key=f"btn_{task['id']}", use_container_width=True):
                st.session_state.active_task = task
                st.rerun()
            
            st.divider()

else:
    st.info("No tasks found matching your criteria.")

# --- Task Details View ---
if 'active_task' in st.session_state:
    t = st.session_state.active_task
    st.divider()
    st.markdown(f"### 📌 Task: {t['title']}")
    st.write(t['description'])
    
    # Attachments
    attachments = get_resources_by_task(t['id'])
    if attachments:
        st.markdown("#### 📎 Attached Resources")
        for att in attachments:
            with st.expander(f"{att['resource_type'].upper()}: {att['title'] or 'Resource'}"):
                st.markdown(f"**Link:** [{att['url_or_path']}]({att['url_or_path']})")
                if att['ai_summary']:
                     st.info(f"🤖 **AI Summary:** {att['ai_summary']}")
                if st.button("Mark as Read/View", key=f"read_{att['id']}"):
                     log_resource_access(st.session_state.user_id, att['id'])
                     st.success("Access logged.")

    if t['status'] != 'Completed':
        tab_done, tab_delay = st.tabs(["✅ Mark Complete", "⏳ Submit Delay Excuse"])
        
        with tab_done:
            if st.button("Mark as Done", key=f"done_btn_{t['id']}"):
                 service_complete_task(st.session_state.user_id, t['id'], t['title'])
                 st.success("Task completed!")
                 st.session_state.active_task['status'] = 'Completed'
                 st.rerun()
        
        with tab_delay:
            st.warning("Submitting a delay reason will trigger AI analysis.")
            d_reason = st.text_area("Reason for delay", help="Be specific for better scores.")
            
            # Proof Upload
            proof_file = st.file_uploader("📄 Upload Proof (Optional)", type=['png', 'jpg', 'jpeg', 'pdf'], help="Attach documents or images verifying your reason.")
            
            if st.button("Submit Excuse"):
                with st.spinner("Analyzing excuse using explicit formulas..."):
                    result = service_submit_delay(st.session_state.user_id, t['id'], t['title'], d_reason, proof_file=proof_file)
                    
                    # Display results with category
                    st.success("✅ Excuse submitted successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Authenticity Score", f"{result.get('authenticity_score', 0)}%")
                    
                    with col2:
                        st.metric("Avoidance Score", f"{result.get('avoidance_score', 0)}%")
                    
                    with col3:
                        risk_level = result.get('risk_level', 'Medium')
                        risk_color = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}.get(risk_level, '🟡')
                        st.metric("Risk Level", f"{risk_color} {risk_level}")
                    
                    # Category display (Formula 13)
                    category = result.get('category', 'Other')
                    category_icons = {
                        'Technical': '🔧',
                        'Workload': '📊',
                        'Personal': '👤',
                        'Communication': '💬',
                        'External': '🌐',
                        'Other': '❓'
                    }
                    icon = category_icons.get(category, '❓')
                    st.info(f"{icon} **Category:** {category}")
                    
                    # Show detailed breakdown
                    with st.expander("📊 Detailed Analysis"):
                        st.json(result)
