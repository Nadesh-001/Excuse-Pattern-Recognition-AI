import streamlit as st

def apply_custom_css():
    # Get user role for theming (FIXED: using 'role' key consistently)
    user_role = st.session_state.get('role', 'employee')
    
    # Define Role-Based Color Palettes (Light Theme Only)
    themes = {
        'admin': {
            'primary': '#f97316',      # Orange 500
            'primary_dark': '#c2410c', # Orange 700
            'accent': '#fbbf24',       # Amber 400
            'bg_gradient': 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)', # Orange Light
            'btn_gradient': 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
            'border': '#fdba74'        # Orange 300
        },
        'manager': {
            'primary': '#8b5cf6',      # Violet 500
            'primary_dark': '#6d28d9', # Violet 700
            'accent': '#a78bfa',       # Violet 400
            'bg_gradient': 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%)', # Violet Light
            'btn_gradient': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
            'border': '#c4b5fd'        # Violet 300
        },
        'employee': {
            'primary': '#3b82f6',      # Blue 500
            'primary_dark': '#1d4ed8', # Blue 700
            'accent': '#60a5fa',       # Blue 400
            'bg_gradient': 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)', # Blue Light
            'btn_gradient': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
            'border': '#93c5fd'        # Blue 300
        }
    }
    
    # Select theme based on role, default to employee
    theme = themes.get(user_role, themes['employee'])
    
    css = """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #1e293b;
            background-color: #f8fafc;
        }}

        .stApp {{
            background-color: #f8fafc;
        }}
        /* Removed margin-top: -80px hack - using header visibility instead */

        /* SIDEBAR STYLING */
        section[data-testid="stSidebar"] {{
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
        }}

        .sidebar-title {{
            font-size: 20px;
            font-weight: 700;
            color: {primary};
            padding: 12px 16px;
            margin-bottom: 8px;
        }}

        .sidebar-section {{
            font-size: 11px;
            font-weight: 700;
            color: #94a3b8;
            padding: 16px 16px 6px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .sidebar-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 16px;
            margin: 4px 10px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            text-decoration: none;
        }}

        .sidebar-item:hover {{
            background-color: #f1f5f9;
        }}

        .sidebar-active {{
            background-color: {primary}15;
            border-left: 3px solid {primary};
        }}

        .sidebar-item i {{
            width: 18px;
            text-align: center;
        }}

        /* ACCOUNT BOX STYLING */
        .account-box {{
            padding: 12px;
            margin: 10px 10px 20px 10px;
            border-radius: 10px;
            background-color: #f8fafc;
            border: 1px solid #e5e7eb;
        }}

        .account-name {{
            font-weight: 600;
            font-size: 14px;
            color: #0f172a;
        }}

        .account-role {{
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
        }}

        .role-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .role-admin {{
            background-color: #fee2e2;
            color: #b91c1c;
        }}

        .role-manager {{
            background-color: #ddd6fe;
            color: #6d28d9;
        }}

        .role-employee {{
            background-color: #dcfce7;
            color: #166534;
        }}

        [data-testid="stSidebar"] {{
            background-color: #ffffff;
            border-right: none;
            box-shadow: 4px 0 24px rgba(0,0,0,0.02);
            padding-top: 2rem;
        }}

        h1, h2, h3 {{
            color: #0f172a;
            font-weight: 800;
            letter-spacing: -0.03em;
        }}

        p {{
            color: #64748b;
            line-height: 1.6;
        }}

        .dashboard-card {{
            background: #ffffff;
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
            border: 1px solid #f1f5f9;
            height: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .dashboard-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 20px 40px -12px rgba(0,0,0,0.1);
        }}

        .welcome-card {{
            background: {btn_gradient};
            border-radius: 20px;
            padding: 32px;
            color: white;
            box-shadow: 0 20px 40px -12px {primary}50;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }}

        .welcome-card h1 {{ color: white !important; }}
        .welcome-card p {{ color: rgba(255,255,255,0.9) !important; }}

        .task-row {{
            display: flex;
            align-items: center;
            padding: 16px;
            background: #ffffff;
            border-bottom: 1px solid #f1f5f9;
            transition: background 0.2s;
        }}

        .task-row:last-child {{ border-bottom: none; }}
        .task-row:hover {{ background: #f8fafc; }}

        .task-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            margin-right: 16px;
            flex-shrink: 0;
        }}

        .metric-value {{
            font-size: 2rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.1;
        }}

        .metric-label {{
            font-size: 0.85rem;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }}

        .stProgress > div > div > div > div {{
            background-image: {btn_gradient};
        }}

        .stButton > button {{
            background: #ffffff;
            color: {primary_dark};
            border: 2px solid #f1f5f9;
            box-shadow: none;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.5rem 1.2rem;
        }}

        .stButton > button:hover {{
            background: #f8fafc;
            border-color: {primary};
            color: {primary};
            transform: translateY(-1px);
        }}
           
        button[kind="primary"] {{
            background: {btn_gradient} !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 10px 20px -5px {primary}60 !important;
        }}

        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
            background-color: #ffffff;
            border: 2px solid #f1f5f9;
            border-radius: 12px;
            box-shadow: none;
        }}
        
        .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {{
            border-color: {primary};
            box-shadow: 0 0 0 4px {primary}10;
        }}
        
        /* HIDE STREAMLIT ELEMENTS */
        #MainMenu {{visibility: hidden;}}
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        [data-testid="stToolbar"] {{ visibility: hidden; }}

        /* LANDING PAGE SPECIFIC */
        .landing-wrapper {{
            height: 90vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}

        .landing-content {{ text-align: center; max-width: 900px; }}
        .app-logo {{ width: 220px; margin-bottom: 28px; }}

        .landing-title {{
            font-size: 3.2rem;
            font-weight: 800;
            color: #000000;
            letter-spacing: -0.04em;
            margin-bottom: 12px;
            text-shadow: 0px 1px 0px #d1d5db, 0px 2px 0px #cbd5e1, 0px 3px 0px #cbd5e1, 0px 6px 14px rgba(0,0,0,0.18);
        }}

        .app-quote {{
            margin-top: 14px;
            font-size: 1.1rem;
            font-weight: 600;
            color: #000000;
            line-height: 1.7;
            text-shadow: 0px 1px 2px rgba(0,0,0,0.15);
        }}

        .start-btn {{
            margin-top: 48px;
            display: inline-block;
            padding: 16px 48px;
            font-size: 1.05rem;
            font-weight: 800;
            color: #ffffff;
            background: #000000;
            border-radius: 16px;
            text-decoration: none;
            box-shadow: 0px 12px 28px rgba(0,0,0,0.35);
        }}

        .start-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0px 18px 36px rgba(0,0,0,0.45);
        }}

        /* LOGIN PAGE */
        .login-header {{ text-align: center; margin-bottom: 32px; }}

        .app-title {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}

        .app-subtitle {{
            color: #64748b;
            font-size: 1.1rem;
            font-weight: 400;
            letter-spacing: 0.01em;
        }}

        .login-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 24px;
            padding: 48px 40px;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.05);
            margin-bottom: 24px;
        }}

        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-top: 40px;
        }}

        .feature-item {{
            text-align: center;
            padding: 20px;
            background: #f8fafc;
            border: 1px solid #f1f5f9;
            border-radius: 16px;
            transition: all 0.3s ease;
        }}

        .feature-item:hover {{
            transform: translateY(-4px);
            border-color: {primary};
            box-shadow: 0 10px 20px -5px {primary}10;
            background: #ffffff;
        }}

        .feature-icon {{ font-size: 2rem; margin-bottom: 8px; }}
        .feature-text {{ color: #475569; font-size: 0.875rem; font-weight: 600; }}

        .demo-box {{
            background: #f0f9ff;
            border: 1px dashed #3b82f6;
            border-radius: 12px;
            padding: 20px;
            margin-top: 24px;
        }}

        .demo-title {{
            color: #0369a1;
            font-weight: 700;
            font-size: 0.875rem;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .demo-credential {{
            color: #334155;
            font-size: 0.9rem;
            font-family: 'Courier New', monospace;
            margin: 6px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .stForm {{ border: none !important; padding: 0 !important; }}
        </style>
    """.format(
        primary=theme['primary'],
        primary_dark=theme['primary_dark'],
        btn_gradient=theme['btn_gradient']
    )
    
    st.markdown(css, unsafe_allow_html=True)
