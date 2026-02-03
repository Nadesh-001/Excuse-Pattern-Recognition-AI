import streamlit as st

def login_session(user):
    st.session_state.logged_in = True
    st.session_state.role = user['role']  # FIXED: using 'role' key consistently
    st.session_state.user_id = user['id']
    st.session_state.user_name = user['full_name']
    st.session_state.user_email = user['email']

def logout_session():
    st.session_state.clear()
    st.rerun()

def require_auth():
    if not st.session_state.get('logged_in'):
        st.warning("Please login first")
        st.stop()

def require_role(allowed_roles):
    require_auth()
    if st.session_state.role not in allowed_roles:
        st.error("Access Denied")
        st.stop()
