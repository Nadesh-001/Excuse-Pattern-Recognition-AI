import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.session import require_auth
from services.analytics_service import get_analytics_data
from components.styling import apply_custom_css
from components.sidebar import render_sidebar

# Page Config
st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")
require_auth()

apply_custom_css()
render_sidebar(active_page="Analytics")

st.title("📊 Analytics & Insights")

# Data fetching replaced by service
# get_analytics_data() imported from service

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
    
    # Combined Export
    if not df_tasks.empty and not df_delays.empty:
        # Merge tasks and delays
        df_combined = pd.merge(
            df_tasks, 
            df_delays, 
            left_on='id', 
            right_on='task_id', 
            how='left',
            suffixes=('_task', '_delay')
        )
        csv_combined = df_combined.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="📊 Download Combined Report (CSV)",
            data=csv_combined,
            file_name='combined_report.csv',
            mime='text/csv',
            type="primary"
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

    # Row 1.5: Categories and Risk (New)
    st.divider()
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("Delay Categories")
        if not df_delays.empty and 'category' in df_delays.columns:
            # Check if category column exists, if not try to parse from json or use dummy
            # Assuming 'category' column might not exist in schema yet, let's check or parse
            # Actually schema.sql showed 'category' wasn't there, it was inside ai_analysis_json
            # We need to extract it if not present.
            # For robustness, let's extract from ai_analysis_json if needed
            
            cats = []
            for index, row in df_delays.iterrows():
                # Try simple column first
                if 'category' in row: 
                    cats.append(row['category'])
                elif 'ai_analysis_json' in row:
                    try:
                        import json
                        import re
                        # Fix potential single quote JSON issues
                        json_str = row['ai_analysis_json'].replace("'", '"')
                        data = json.loads(json_str)
                        cats.append(data.get('category', 'Uncategorized'))
                    except:
                        cats.append('Uncategorized')
                else:
                    cats.append('Unknown')
            
            df_cats = pd.DataFrame({'Category': cats})
            fig_cat = px.bar(df_cats['Category'].value_counts().reset_index(), x='index', y='Category', title="Common Delay Reasons", labels={'index': 'Category', 'Category': 'Count'})
            st.plotly_chart(fig_cat, use_container_width=True)

    # Risk Distribution Cards
    st.subheader("Risk Level Distribution")
    if not df_delays.empty and 'risk_level' in df_delays.columns:
        risk_counts = df_delays['risk_level'].value_counts()
        low = risk_counts.get('Low', 0)
        med = risk_counts.get('Medium', 0)
        high = risk_counts.get('High', 0)
        
        r1, r2, r3 = st.columns(3)
        
        with r1:
            st.markdown(f"""
            <div style="background: rgba(52, 211, 153, 0.2); border: 1px solid #34D399; border-radius: 12px; padding: 24px; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 800; color: #065F46;">{low}</div>
                <div style="color: #064E3B; font-weight: 600;">Low Risk</div>
            </div>
            """, unsafe_allow_html=True)
            
        with r2:
            st.markdown(f"""
            <div style="background: rgba(251, 191, 36, 0.2); border: 1px solid #FBBF24; border-radius: 12px; padding: 24px; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 800; color: #92400E;">{med}</div>
                <div style="color: #78350F; font-weight: 600;">Medium Risk</div>
            </div>
            """, unsafe_allow_html=True)
            
        with r3:
            st.markdown(f"""
            <div style="background: rgba(248, 113, 113, 0.2); border: 1px solid #F87171; border-radius: 12px; padding: 24px; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 800; color: #991B1B;">{high}</div>
                <div style="color: #7F1D1D; font-weight: 600;">High Risk</div>
            </div>
            """, unsafe_allow_html=True)

    # Performance Analytics (Gauges)
    st.divider()
    st.subheader("Your Performance Analytics")
    
    if not df_delays.empty:
        import plotly.graph_objects as go
        
        avg_auth = df_delays['score_authenticity'].mean()
        avg_avoid = df_delays.get('score_avoidance', pd.Series([0])).mean()
        
        g1, g2 = st.columns(2)
        
        with g1:
            fig_auth = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_auth,
                title = {'text': "Average Authenticity"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#10B981"},
                    'steps': [
                        {'range': [0, 50], 'color': "#fee2e2"},
                        {'range': [50, 80], 'color': "#fef3c7"},
                        {'range': [80, 100], 'color': "#d1fae5"}
                    ]
                }
            ))
            st.plotly_chart(fig_auth, use_container_width=True)
            
        with g2:
             fig_avoid = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_avoid,
                title = {'text': "Average Avoidance"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#EF4444"},
                    'steps': [
                        {'range': [0, 50], 'color': "#d1fae5"}, # Low avoidance is good (Green)
                        {'range': [50, 100], 'color': "#fee2e2"} # High avoidance is bad (Red)
                    ]
                }
            ))
             st.plotly_chart(fig_avoid, use_container_width=True)

    st.subheader("Delay Frequency Trend")
    # Use submitted_at for delays
    date_col = 'submitted_at' if 'submitted_at' in df_delays.columns else 'created_at'
    
    if not df_delays.empty and date_col in df_delays.columns:
        df_delays[date_col] = pd.to_datetime(df_delays[date_col])
        daily_counts = df_delays.groupby(df_delays[date_col].dt.date).size().reset_index(name='counts')
        fig_line = px.line(daily_counts, x=date_col, y='counts', title='Daily Delay Submissions')
        st.plotly_chart(fig_line, use_container_width=True)

# ============================================================================
# MANAGER INSIGHTS PANEL (Formulas 16-18 - Manager/Admin Only)
# ============================================================================
role = st.session_state.get('role', '')

if role in ['manager', 'admin']:
    st.write("")
    st.write("")
    st.divider()
    st.subheader("🎯 Employee Risk Insights")
    st.caption("Employees identified as high-risk based on delay count (Formula 16-18)")
    
    # Get all users and calculate risk levels
    from repository.users_repo import get_all_users
    from repository.delays_repo import count_user_delays
    from utils import scoring_engine
    
    try:
        all_users = get_all_users()
        employees = [u for u in all_users if u.get('role') == 'employee']
        
        high_risk_employees = []
        
        for emp in employees:
            emp_id = emp.get('id')
            emp_name = emp.get('full_name', 'Unknown')
            
            # Formula 5: Count delays
            delay_count = count_user_delays(emp_id)
            
            # Formulas 16-18: Calculate risk level
            risk_level = scoring_engine.calculate_risk_level(delay_count)
            
            # Only show high-risk employees
            if risk_level == "High":
                high_risk_employees.append({
                    'name': emp_name,
                    'delay_count': delay_count,
                    'risk': risk_level
                })
        
        if high_risk_employees:
            st.warning(f"⚠️ **{len(high_risk_employees)} employees** currently at high risk")
            
            for emp_data in high_risk_employees:
                with st.expander(f"🔴 {emp_data['name']} - {emp_data['risk']} Risk"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.metric("Delay Count", emp_data['delay_count'])
                        
                        # Risk badge
                        st.markdown("""
                        <div style="background: #fee2e2; border: 1px solid #ef4444; 
                                    padding: 8px; border-radius: 8px; text-align: center; margin-top: 10px;">
                            <span style="color: #991b1b; font-weight: 600;">⚠️ HIGH RISK</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.write("**Recommended Actions:**")
                        
                        # Logic-based recommendations (not AI)
                        if emp_data['delay_count'] > 5:
                            st.error("🔧 **Action Required:** Review task deadlines and workload distribution")
                            st.write("- Consider extending deadlines for complex tasks")
                            st.write("- Evaluate if employee needs additional support or resources")
                        elif emp_data['delay_count'] > 3:
                            st.warning("💬 **Follow-Up Meeting:** Schedule 1-on-1 discussion")
                            st.write("- Understand root causes of delays")
                            st.write("- Identify potential blockers or challenges")
                        else:
                            st.info("📊 **Monitor Closely:** Pattern emerging")
                            st.write("- Track next few tasks for improvement")
                            st.write("- Provide coaching on time management if needed")
        else:
            st.success("✅ **No high-risk employees detected**")
            st.info("All employees currently have delay counts ≤ 2 (Low or Medium risk)")
    
    except Exception as e:
        st.warning(f"⚠️ Could not load manager insights: {e}")

else:
    st.error("Could not load analytics data.")
