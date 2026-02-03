import streamlit as st
from services.permission_service import has_permission, Permissions

def render_sidebar(active_page="Dashboard"):
    """
    Render a modern sidebar with permission-based navigation.
    
    Args:
        active_page: The currently active page name
    """
    
    # Sidebar button styling
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] button {
        background: none;
        border: none;
        text-align: left;
        padding: 10px 16px;
        font-size: 14px;
        font-weight: 500;
        color: #334155;
        border-radius: 8px;
        width: 100%;
        margin: 2px 0;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background-color: #f1f5f9;
    }
    
    section[data-testid="stSidebar"] button:focus {
        outline: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        # App Title
        st.markdown('<div class="sidebar-title">🤖 EPR AI</div>', unsafe_allow_html=True)
        
        # --- ACCOUNT BOX ---
        user_name = st.session_state.get('user_name', 'Guest User')
        user_role = st.session_state.get('user_role', 'employee')
        
        # Role badge styling
        role_display = user_role.capitalize()
        role_class = f"role-{user_role.lower()}"
        
        st.markdown(f"""
        <div class="account-box">
            <div class="account-name">{user_name}</div>
            <div class="account-role">
                <span class="role-badge {role_class}">{role_display}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # OVERVIEW Section
        st.markdown('<div class="sidebar-section">OVERVIEW</div>', unsafe_allow_html=True)
        
        # Dashboard - everyone has access
        if has_permission(Permissions.VIEW_DASHBOARD):
            if st.button("📈 Dashboard", key="nav_dashboard", use_container_width=True):
                st.switch_page("pages/1_Dashboard.py")
        
        # Tasks - everyone has access
        if has_permission(Permissions.VIEW_TASKS):
            if st.button("✅ Tasks", key="nav_tasks", use_container_width=True):
                st.switch_page("pages/2_Tasks.py")
        
        # Analytics - managers and admins only
        if has_permission(Permissions.VIEW_ANALYTICS):
            if st.button("📊 Analytics", key="nav_analytics", use_container_width=True):
                st.switch_page("pages/3_Analytics.py")
        
        # AI Section
        st.markdown('<div class="sidebar-section">AI</div>', unsafe_allow_html=True)
        
        if has_permission(Permissions.USE_CHATBOT):
            if st.button("🤖 Chatbot", key="nav_chatbot", use_container_width=True):
                st.switch_page("pages/4_Chatbot.py")
        
        # MANAGEMENT Section - only for managers and admins
        if has_permission(Permissions.MANAGE_EMPLOYEES):
            st.markdown('<div class="sidebar-section">MANAGEMENT</div>', unsafe_allow_html=True)
            
            if st.button("👥 Employee Profiles", key="nav_profiles", use_container_width=True):
                st.switch_page("pages/7_Employee_Profiles.py")
        
        # SYSTEM Section - only for admins
        if has_permission(Permissions.ADMIN_PANEL):
            st.markdown('<div class="sidebar-section">SYSTEM</div>', unsafe_allow_html=True)
            
            if st.button("🔍 Search", key="nav_search", use_container_width=True):
                st.switch_page("pages/6_Search.py")
            
            if st.button("⚙️ Admin Panel", key="nav_admin", use_container_width=True):
                st.switch_page("pages/5_Admin_Panel.py")
            
            # Audit Logs - admin only
            if has_permission(Permissions.VIEW_AUDIT_LOGS):
                if st.button("📜 Audit Logs", key="nav_audit", use_container_width=True):
                    st.switch_page("pages/9_Audit_Logs.py")
        
        # --- ACCOUNT OPTIONS ---
        st.markdown("---")
        
        # Profile - everyone can edit their own profile
        if has_permission(Permissions.EDIT_PROFILE):
            if st.button("👤 Profile", key="nav_profile", use_container_width=True):
                st.switch_page("pages/8_Profile.py")
        
        # Logout Button
        if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
            # Import audit service to log logout
            from services.audit_service import log_action, AuditActions
            
            # Log logout
            log_action(AuditActions.USER_LOGOUT, f"User logged out")
            
            # Clear session
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Redirect to Landing Page
            st.switch_page("app.py")



