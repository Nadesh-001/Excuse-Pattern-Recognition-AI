import streamlit as st
import os
from services.theme_service import get_theme_css

def apply_custom_css():
    """Load and apply CSS from external file with dynamic theme variables"""
    
    # Get current theme
    theme = 'light'
    
    # 1. Inject Theme Variables
    st.markdown(f"<style>{get_theme_css(theme)}</style>", unsafe_allow_html=True)
    
    # 2. Load Main CSS
    css_path = "assets/style.css"

    if not os.path.exists(css_path):
        st.error("❌ CSS file not found: assets/style.css")
        return

    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
