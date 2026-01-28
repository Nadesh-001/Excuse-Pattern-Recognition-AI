import streamlit as st
import datetime
import os

def load_icon(name):
    try:
        with open(f"assets/icons/{name}.svg", "r") as f:
            return f.read()
    except:
        return ""

def render_sidebar():
    # Hide default sidebar nav
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Logo Area
        logo = load_icon("logo")
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="width: 40px; height: 40px;">{logo}</div>
            <h2 style="margin:0; font-size: 20px;">ExcuseAI</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # User Profile
        st.write(f"**{st.session_state.user_name}**")
        st.caption(f"{st.session_state.user_role.capitalize()}")
        st.divider()

        # Custom Navigation
        nav_items = [
            ("Dashboard", "pages/1_Dashboard.py", "dashboard"),
            ("My Tasks", "pages/2_Tasks.py", "tasks"),
            ("Analytics", "pages/3_Analytics.py", "analytics"),
            ("AI Assistant", "pages/4_Chatbot.py", "chatbot"),
            ("Search", "pages/6_Search.py", "search")
        ]

        if st.session_state.user_role == 'admin':
             nav_items.insert(4, ("Admin Panel", "pages/5_Admin_Panel.py", "admin"))

        for label, page, icon_name in nav_items:
            icon_svg = load_icon(icon_name)
            # Use columns for icon + text layout
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown(f'<div style="width: 24px;">{icon_svg}</div>', unsafe_allow_html=True)
            with c2:
                if st.button(label, key=f"nav_{icon_name}", use_container_width=True):
                    st.switch_page(page)
        
        st.divider()
        logout_icon = load_icon("login") # Reusing login icon for logout style
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
