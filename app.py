import streamlit as st
import base64
import os
from services.auth_service import authenticate_user, register_user
from utils.session import login_session
from components.styling import apply_custom_css

# Page Config
st.set_page_config(
    page_title="Excuse Pattern AI - Login",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state if not exists
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Redirect if already logged in
if st.session_state.logged_in:
    st.switch_page("pages/1_Dashboard.py")

# Apply CSS
apply_custom_css()

def get_base64(path):
    """Safely encode image to base64 with file existence check"""
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

from services.theme_service import get_logo_path

def landing_page():
    # Dynamic logo based on theme
    theme = 'light'
    logo_path = get_logo_path(theme)
    logo = get_base64(logo_path)
    
    # Use emoji fallback if logo doesn't exist
    if logo:
        logo_html = f'<img src="data:image/png;base64,{logo}" class="app-logo"/>'
    else:
        logo_html = '<div class="app-logo" style="font-size: 80px;">🤖</div>'
    
    html_content = f"""
    <div class="landing-wrapper">
        <div class="landing-content">
            {logo_html}
            <div class="landing-title">
                EXCUSE PATTERN RECOGNITION AI
            </div>
            <div class="app-quote">
                Turning excuses into insights.<br>
                AI-driven accountability for time and tasks.
            </div>
            <a href="?page=login" class="start-btn">
                START
            </a>
        </div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)


from repository.users_repo import count_admins
from services.auth_service import register_user

def login_page():
    # Spacer
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Center container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header
        st.markdown("""
        <div class="login-header">
            <div class="app-logo">🤖</div>
            <h1 class="app-title">Excuse Pattern AI</h1>
            <p class="app-subtitle">Intelligent Delay Analysis & Workforce Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login Card
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # 🟢 CHECK SYSTEM STATUS
        admin_count = count_admins()
        
        if admin_count == 0:
            # === ONE-TIME ADMIN SETUP ===
            st.warning("⚠️ System Not Initialized. Please create the Global Admin account.")
            
            with st.form("admin_setup_form"):
                st.markdown("### 🛠️ One-Time Admin Setup")
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Email Address")
                new_pass = st.text_input("Password", type="password")
                org_name = st.text_input("Organization Name", value="My Organization")
                
                # Hidden Role
                st.info("Role: Global Administrator (Fixed)")
                
                if st.form_submit_button("Initialize System"):
                    if new_name and new_email and new_pass and org_name:
                        success, msg = register_user(new_name, new_email, new_pass, role='admin', org_name=org_name)
                        if success:
                            st.success("✅ System Initialized! Please login.")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("All fields are required.")
        
        else:
            # === NORMAL OPERATION ===
            tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
            with tab1:
                with st.form("login_form"):
                    st.markdown("#### Welcome Back!")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    email = st.text_input("📧 Email Address", placeholder="your.email@company.com")
                    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    submit = st.form_submit_button("🚀 Login", use_container_width=True)
                    
                    if submit:
                        if email and password:
                            try:
                                with st.spinner("Verifying credentials..."):
                                    user = authenticate_user(email, password)
                                
                                if user:
                                    login_session(user)
                                    st.success(f"✅ Welcome back, {user['full_name']}!")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid email or password")
                            except ValueError as ve:
                                 st.error(f"❌ {ve}")
                            except Exception as e:
                                 st.error("❌ Login failed. Please try again.")
                        else:
                            st.warning("⚠️ Please fill all fields")
            
            with tab2:
                st.markdown("#### Create New Account")
                with st.form("signup_form"):
                    s_name = st.text_input("Full Name")
                    s_email = st.text_input("Email Address")
                    s_pass = st.text_input("Password", type="password")
                    s_org = st.text_input("Organization", placeholder="Enter your organization name")
                    s_role = st.selectbox("Role", ["employee", "manager"])
                    
                    if st.form_submit_button("Create Account"):
                        if s_name and s_email and s_pass and s_org:
                            # Register as Employee/Manager
                            success, msg = register_user(s_name, s_email, s_pass, role=s_role, org_name=s_org)
                            if success:
                                st.success("✅ Account created! Please login.")
                            else:
                                st.error(msg)
                        else:
                            st.warning("All fields are required")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Features - Vertical Layout
        st.markdown("""
        <div class="feature-vertical">
            <div class="feature-item">
                <div class="feature-icon">🤖</div>
                <div class="feature-text">AI-Powered Analysis</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📊</div>
                <div class="feature-text">Real-Time Analytics</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🔒</div>
                <div class="feature-text">Secure & Private</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
            <p>Powered by Advanced AI • Built with ❤️ for Better Workforce Management</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Routing Logic - Using newer st.query_params API
    if hasattr(st, 'query_params') and hasattr(st.query_params, '__contains__'):
        # Streamlit >= 1.30.0 with new query_params
        page = st.query_params.get("page", "landing")
    else:
        # Fallback for older versions (use dict-like access)
        page = "landing"
    
    if page == "landing":
        landing_page()
    elif page == "login":
        login_page()
    else:
        landing_page()

if __name__ == "__main__":
    main()
