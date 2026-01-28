import streamlit as st
import pandas as pd
from utils.helpers import init_session_state
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from database.connection import get_db_connection
from ai_engine.core import analyze_delay_reason
from ai_engine.audio import transcribe_audio
 # Audio recorder (simple approach) or file uploader for voice
import os

# Page Config
st.set_page_config(page_title="Tasks", page_icon="📝", layout="wide")
init_session_state()
if not st.session_state.logged_in:
    st.switch_page("app.py")

apply_custom_css()
render_sidebar()

import json
from ai_engine.resources import parse_file, parse_url, analyze_resource

from utils.email_service import send_email

def create_task(title, desc, assign_to_id, deadline, priority, attachments, link):
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor(dictionary=True) # Dictionary cursor for easy field access
    try:
        # Get Assigned User Email
        cursor.execute("SELECT email, full_name FROM users WHERE id = %s", (assign_to_id,))
        user = cursor.fetchone()
        
        # Insert Task
        cursor.execute(
            "INSERT INTO tasks (title, description, assigned_to, created_by, deadline, priority) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, desc, assign_to_id, st.session_state.user_id, deadline, priority)
        )
        task_id = cursor.lastrowid
        
        # Process Link
        if link:
            content = parse_url(link)
            analysis = analyze_resource(content)
            cursor.execute(
                "INSERT INTO attachments (task_id, resource_type, url_or_path, title, ai_summary, requirements_json, deadlines_json, completeness_score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (task_id, 'link', link, 'External Link', analysis.get('summary'), json.dumps(analysis.get('deadlines', [])), json.dumps(analysis.get('deadlines', [])), analysis.get('completeness', 0))
            )

        # Process Files
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
            
        for att in attachments:
            file_path = os.path.join("uploads", att.name)
            with open(file_path, "wb") as f:
                f.write(att.getbuffer())
            
            content = parse_file(file_path)
            analysis = analyze_resource(content)
            
            cursor.execute(
                "INSERT INTO attachments (task_id, resource_type, url_or_path, title, ai_summary, requirements_json, deadlines_json, completeness_score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (task_id, 'file', file_path, att.name, analysis.get('summary'), json.dumps(analysis.get('deadlines', [])), json.dumps(analysis.get('deadlines', [])), analysis.get('completeness', 0))
            )

        conn.commit()
        
        # Send Email Notification
        if user and user['email']:
            subject = f"New Task Assigned: {title}"
            body = f"Hello {user['full_name']},\n\nA new task has been assigned to you.\n\nTitle: {title}\nDeadline: {deadline}\nPriority: {priority}\n\nPlease log in to view details."
            success, msg = send_email(user['email'], subject, body)
            if success:
                st.toast("📧 Notification sent to user.")
            else:
                st.warning(f"Task created, but email failed: {msg}")

        st.success("Task created successfully with Smart Attachments!")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def get_my_tasks(user_id):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE assigned_to = %s ORDER BY deadline ASC", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def submit_delay(task_id, reason, audio_file=None):
    if audio_file:
        # Save temp file
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_file.getbuffer())
        transcribed_text = transcribe_audio("temp_audio.wav")
        final_reason = f"{reason}\n[Voice Transcript]: {transcribed_text}"
    else:
        final_reason = reason

    # AI Analysis
    analysis = analyze_delay_reason(final_reason)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO delays (task_id, user_id, reason_text, score_authenticity, score_avoidance, risk_level, ai_analysis_json) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (task_id, st.session_state.user_id, final_reason, analysis['authenticity'], analysis['avoidance'], analysis['risk_level'], str(analysis))
    )
    # Update task status
    cursor.execute("UPDATE tasks SET status='Delayed' WHERE id=%s", (task_id,))
    conn.commit()
    conn.close()
    return analysis

# --- UI ---

st.title("Task Management")

# Manager: Create Task
if st.session_state.user_role in ['manager', 'admin']:
    with st.expander("➕ Create New Task"):
        with st.form("new_task"):
            t_title = st.text_input("Title")
            t_desc = st.text_area("Description")
            t_assign = st.number_input("Assign to User ID", min_value=1, step=1)
            t_deadline = st.date_input("Deadline")
            t_prio = st.selectbox("Priority", ["Low", "Medium", "High"])
            
            # Smart Attachments
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                t_files = st.file_uploader("Attach Files (PDF, DOCX)", accept_multiple_files=True, type=['pdf', 'docx', 'txt'])
            with col_res2:
                t_link = st.text_input("Attach URL (Optional)")

            if st.form_submit_button("Create Task"):
                if t_title:
                    create_task(t_title, t_desc, t_assign, t_deadline, t_prio, t_files, t_link)
                else:
                    st.warning("Title is required")

# Employee: View Tasks
st.subheader("My Tasks")
tasks = get_my_tasks(st.session_state.user_id)

for task in tasks:
    with st.container():
        c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
        c1.markdown(f"**{task['title']}**")
        c2.caption(f"Due: {task['deadline']}")
        c3.markdown(f"**{task['status']}**") # Basic text badge
        
        if c4.button("Details", key=f"btn_{task['id']}"):
            st.session_state.active_task = task
            st.rerun()

if 'active_task' in st.session_state:
    t = st.session_state.active_task
    st.divider()
    st.markdown(f"### 📌 Task: {t['title']}")
    st.write(t['description'])
    
    # Fetch Attachments
    conn_att = get_db_connection()
    if conn_att:
        curr_att = conn_att.cursor(dictionary=True)
        curr_att.execute("SELECT * FROM attachments WHERE task_id = %s", (t['id'],))
        attachments = curr_att.fetchall()
        
        if attachments:
            st.markdown("#### 📎 Attached Resources")
            for att in attachments:
                with st.expander(f"{att['resource_type'].upper()}: {att['title'] or 'Resource'}"):
                    if att['resource_type'] == 'link':
                        st.markdown(f"**Link:** [{att['url_or_path']}]({att['url_or_path']})")
                    else:
                        st.markdown(f"**File:** `{os.path.basename(att['url_or_path'])}`")
                    
                    if att['ai_summary']:
                        st.info(f"🤖 **AI Summary:** {att['ai_summary']}")
                    
                    if att['deadlines_json']:
                        st.caption(f"📅 **A detected deadlines:** {att['deadlines_json']}")
                        
                    # Log Access
                    if st.button("Mark as Read/View", key=f"read_{att['id']}"):
                        curr_att.execute("INSERT INTO resource_logs (user_id, attachment_id) VALUES (%s, %s)", (st.session_state.user_id, att['id']))
                        conn_att.commit()
                        st.success("Access logged.")
        conn_att.close()

    if t['status'] != 'Completed':
        tab_done, tab_delay = st.tabs(["✅ Mark Complete", "⏳ Submit Delay Excuse"])
        
        with tab_done:
            if st.button("Mark as Done"):
                 conn_done = get_db_connection()
                 cursor_done = conn_done.cursor()
                 cursor_done.execute("UPDATE tasks SET status='Completed' WHERE id=%s", (t['id'],))
                 conn_done.commit()
                 conn_done.close()
                 st.success("Task completed!")
                 st.rerun()
        
        with tab_delay:
            st.warning("Submitting a delay reason will trigger AI analysis.")
            d_reason = st.text_area("Reason for delay", help="Be specific for better scores.")
            d_voice = st.file_uploader("Upload Voice Message (WAV/MP3)", type=['wav', 'mp3'])
            
            if st.button("Submit Excuse"):
                with st.spinner("AI Models Analyzing (Whisper + Mistral)..."):
                    result = submit_delay(t['id'], d_reason, d_voice)
                    st.json(result)
                    st.metric("Authenticity Score", f"{result.get('authenticity')}%")
                    st.metric("Risk Level", result.get('risk_level'))
                    if result.get('risk_level') == 'High':
                        st.error("High Risk Detected: Please provide more specific details.")
