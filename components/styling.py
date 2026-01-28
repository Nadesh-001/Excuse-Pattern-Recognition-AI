import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* Global Font */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Main Background */
        .stApp {
            background-color: #0E1117;
            background-image: radial-gradient(circle at 10% 20%, rgba(79, 70, 229, 0.1) 0%, transparent 20%),
                              radial-gradient(circle at 90% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 20%);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(17, 24, 39, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        
        /* Custom Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            letter-spacing: 0.025em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
            filter: brightness(1.1);
        }
        .stButton>button:active {
            transform: translateY(0);
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Inputs */
        .stTextInput>div>div>input, .stSelectbox>div>div>div {
            background-color: rgba(255, 255, 255, 0.03) !important;
            color: #FAFAFA !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            transition: all 0.2s;
        }
        .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus-within {
            border-color: #4F46E5 !important;
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2) !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            padding-bottom: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 48px;
            background-color: transparent;
            border-radius: 8px;
            padding: 0 24px;
            color: #9CA3AF;
            font-weight: 500;
            transition: all 0.2s;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(79, 70, 229, 0.1) !important;
            color: #818CF8 !important;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #FAFAFA !important;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            color: #9CA3AF !important;
        }
        
        /* Form Container - Enhanced */
        [data-testid="stForm"] {
            background: rgba(31, 41, 55, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 2rem;
            backdrop-filter: blur(10px);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0E1117; 
        }
        ::-webkit-scrollbar-thumb {
            background: #374151; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #4B5563; 
        }

        h1, h2, h3 {
            color: #FAFAFA;
            letter-spacing: -0.025em;
        }
        </style>
    """, unsafe_allow_html=True)
