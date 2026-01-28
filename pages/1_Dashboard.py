import streamlit as st
from utils.helpers import init_session_state
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from database.connection import get_db_connection
import pandas as pd

# Page Config
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
init_session_state()
if not st.session_state.logged_in:
    st.switch_page("app.py")

apply_custom_css()
render_sidebar()

st.title(f"👋 Welcome back, {st.session_state.user_name}")

def get_stats(user_id, role):
    conn = get_db_connection()
    if not conn: return {}
    cursor = conn.cursor(dictionary=True)
    
    stats = {}
    if role == 'employee':
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s AND status='Pending'", (user_id,))
        stats['pending'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s AND status='Delayed'", (user_id,))
        stats['delayed'] = cursor.fetchone()['count']
        # Avg Authenticity
        cursor.execute("SELECT AVG(score_authenticity) as avg_score FROM delays WHERE user_id = %s", (user_id,))
        res = cursor.fetchone()['avg_score']
        stats['auth_score'] = round(res, 1) if res else 0
    
    else: # Manager/Admin
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status='Pending'")
        stats['pending'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM delays")
        stats['total_delays'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM delays WHERE risk_level='High'")
        stats['high_risk'] = cursor.fetchone()['count']

    cursor.close()
    conn.close()
    return stats

stats = get_stats(st.session_state.user_id, st.session_state.user_role)

# Metrics Row
st.markdown("### 🚀 Overview")

if st.session_state.user_role == 'employee':
    m1, m2, m3, m4 = stats.get('pending', 0), stats.get('delayed', 0), stats.get('auth_score', 0), "Low"
    l1, l2, l3, l4 = "Pending Tasks", "My Delays", "Avg Authenticity", "Risk Level"
else:
    m1, m2, m3, m4 = stats.get('pending', 0), stats.get('total_delays', 0), stats.get('high_risk', 0), "98%"
    l1, l2, l3, l4 = "Team Pending", "Total Delays", "High Risk", "System Health"

st.markdown(f"""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
    <div class="glass-card">
        <div style="color: #9CA3AF; font-size: 0.9rem;">{l1}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #FAFAFA;">{m1}</div>
    </div>
    <div class="glass-card">
        <div style="color: #9CA3AF; font-size: 0.9rem;">{l2}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #FAFAFA;">{m2}</div>
    </div>
    <div class="glass-card">
        <div style="color: #9CA3AF; font-size: 0.9rem;">{l3}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #818CF8;">{m3}</div>
    </div>
    <div class="glass-card">
        <div style="color: #9CA3AF; font-size: 0.9rem;">{l4}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #34D399;">{m4}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Content Grid
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### 📌 Recent Activity")
    st.markdown("""
    <div class="glass-card" style="min-height: 200px;">
        <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="background: rgba(79, 70, 229, 0.2); padding: 5px; border-radius: 5px;">📅</span>
            <div>
                <div style="font-weight: 600;">System Update</div>
                <div style="font-size: 0.8rem; color: #9CA3AF;">Just now</div>
            </div>
        </div>
        <div style="color: #D1D5DB;">Dashboard updated with new premium UI theme.</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("### ⚡ Quick Actions")
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        if st.button("📝 New Task", use_container_width=True):
            st.switch_page("pages/2_Tasks.py")
        st.markdown("</div>", unsafe_allow_html=True)
