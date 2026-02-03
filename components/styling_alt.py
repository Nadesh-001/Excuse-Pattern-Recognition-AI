import streamlit as st
import streamlit.components.v1 as components

def apply_custom_css():
    # Get user role for theming (FIXED: using 'role' key consistently)
    user_role = st.session_state.get('role', 'employee')
    
    # Define Role-Based Color Palettes (Light Theme Only)
    themes = {
        'admin': {
            'primary': '#f97316',
            'primary_dark': '#ea580c',
            'btn_gradient': 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)'
        },
        'manager': {
            'primary': '#8b5cf6',
            'primary_dark': '#7c3aed',
            'btn_gradient': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)'
        },
        'employee': {
            'primary': '#3b82f6',
            'primary_dark': '#1d4ed8',
            'btn_gradient': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
        }
    }
    
    # Select theme based on role, default to employee
    theme = themes.get(user_role, themes['employee'])
    
    # Build CSS - using components.html as alternative injection method
    css_html = """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #1e293b;
            background-color: #f8fafc;
        }

        .stApp {
            background-color: #f8fafc;
        }

        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
            box-shadow: 4px 0 24px rgba(0,0,0,0.02);
            padding-top: 2rem;
        }

        .sidebar-title {
            font-size: 20px;
            font-weight: 700;
            color: THEME_PRIMARY;
            padding: 12px 16px;
            margin-bottom: 8px;
        }

        .sidebar-active {
            background-color: THEME_PRIMARY15;
            border-left: 3px solid THEME_PRIMARY;
        }

        .welcome-card {
            background: THEME_BTN_GRADIENT;
            border-radius: 20px;
            padding: 32px;
            color: white;
            box-shadow: 0 20px 40px -12px THEME_PRIMARY50;
            margin-bottom: 24px;
        }

        .stButton > button {
            background: #ffffff;
            color: THEME_PRIMARY_DARK;
            border: 2px solid #f1f5f9;
            border-radius: 12px;
            font-weight: 700;
        }

        .stButton > button:hover {
            border-color: THEME_PRIMARY;
            color: THEME_PRIMARY;
        }

        button[kind="primary"] {
            background: THEME_BTN_GRADIENT !important;
            color: white !important;
            border: none !important;
        }

        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """.replace('THEME_PRIMARY', theme['primary']).replace('THEME_PRIMARY_DARK', theme['primary_dark']).replace('THEME_BTN_GRADIENT', theme['btn_gradient'])
    
    # Try using components.html instead of st.markdown
    components.html(css_html, height=0)
