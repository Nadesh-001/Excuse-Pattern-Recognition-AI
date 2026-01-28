import streamlit as st
from utils.helpers import init_session_state, login_user, signup_user
from components.styling import apply_custom_css

# Page Config
st.set_page_config(
    page_title="Excuse Pattern AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session
init_session_state()

# Redirect if already logged in
if st.session_state.get('logged_in', False):
    st.switch_page("pages/1_Dashboard.py")

# Apply CSS
apply_custom_css()

def main():
    st.markdown("<br><br>", unsafe_allow_html=True) # Spacer

    # Center the login form
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1>🤖 Excuse Pattern AI</h1>
            <p style="color: #888;">Intelligent Delay Analysis & Workforce Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if email and password:
                        success, msg = login_user(email, password)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please fill all fields")

        with tab2:
            with st.form("signup_form"):
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                role_choice = st.selectbox("Role", ["employee", "manager"]) 
                st.markdown("<br>", unsafe_allow_html=True)
                
                signup_submit = st.form_submit_button("Sign Up", use_container_width=True)
                
                if signup_submit:
                    if new_name and new_email and new_password:
                        success, msg = signup_user(new_name, new_email, new_password, role_choice)
                        if success:
                            st.success(f"{msg}. Please login.")
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please fill in all fields.")

if __name__ == "__main__":
    main()
