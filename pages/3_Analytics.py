import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import init_session_state
from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from database.connection import get_db_connection

# Page Config
st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")
init_session_state()
if not st.session_state.logged_in:
    st.switch_page("app.py")

apply_custom_css()
render_sidebar()

st.title("📊 Analytics & Insights")

def get_analytics_data():
    conn = get_db_connection()
    if not conn: return None
    
    # Query: Delays over time
    df_delays = pd.read_sql("SELECT * FROM delays", conn)
    # Query: Task Status
    df_tasks = pd.read_sql("SELECT * FROM tasks", conn)
    
    conn.close()
    return df_delays, df_tasks

data = get_analytics_data()

if data:
    df_delays, df_tasks = data
    
    # Export Section
    st.sidebar.divider()
    st.sidebar.subheader("📥 Export Reports")
    if not df_delays.empty:
        csv_delays = df_delays.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Download Delays Report (CSV)",
            data=csv_delays,
            file_name='delays_report.csv',
            mime='text/csv',
        )
    if not df_tasks.empty:
        csv_tasks = df_tasks.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Download Tasks Report (CSV)",
            data=csv_tasks,
            file_name='tasks_report.csv',
            mime='text/csv',
        )

    # Row 1: High Level
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Task Completion Status")
        if not df_tasks.empty:
            fig_status = px.pie(df_tasks, names='status', title='Task Status Distribution', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No task data available.")

    with col2:
        st.subheader("Authenticity vs Avoidance")
        if not df_delays.empty:
            fig_scatter = px.scatter(
                df_delays, 
                x="score_avoidance", 
                y="score_authenticity", 
                color="risk_level",
                size="score_avoidance",
                title="Excuse Risk Correlation",
                labels={"score_avoidance": "Avoidance Score", "score_authenticity": "Authenticity Score"}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No delay data available.")

    # Row 2: Trends
    st.subheader("Delay Frequency Trend")
    if not df_delays.empty and 'created_at' in df_delays.columns:
        df_delays['created_at'] = pd.to_datetime(df_delays['created_at'])
        daily_counts = df_delays.groupby(df_delays['created_at'].dt.date).size().reset_index(name='counts')
        fig_line = px.line(daily_counts, x='created_at', y='counts', title='Daily Delay Submissions')
        st.plotly_chart(fig_line, use_container_width=True)
else:
    st.error("Could not load analytics data.")
