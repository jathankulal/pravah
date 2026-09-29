"""
PRAVAH — Streamlit Entry Point
"""

import streamlit as st
import logging
import requests
from pravah.ui.shell import render_shell
from pravah.ui.styles import inject_custom_css
from pravah.database.seed import seed_database
from pathlib import Path
from pravah.config import DB_PATH, API_URL

# Configure logging
logging.basicConfig(level=logging.INFO)

def call_api_analyze(report_text: str):
    """Calls FastAPI /analyze endpoint"""
    try:
        response = requests.post(
            f"{API_URL.rstrip('/')}/analyze",
            json={"text": report_text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API Error: {e}")
        st.error("Failed to connect to the PRAVAH backend. Please ensure the API is running or try again later.")
        return None

# Page configuration
st.set_page_config(
    page_title="PRAVAH | Causal Risk Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize splash state
if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = False

# Splash Screen Rendering
if not st.session_state.splash_shown:
    # Inject minimal CSS to center the splash and hide sidebar/header
    st.markdown("""
    <style>
        .stApp {
            background-color: #0f1117;
            color: #e8e9ed;
        }
        [data-testid="stSidebar"] {display: none;}
        header[data-testid="stHeader"] {display: none;}
        .block-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_img1, col_img2, col_img3 = st.columns([2, 1, 2])
    with col_img2:
        try:
            st.image("assets/pravah_logo.png")
        except Exception:
            pass

    st.markdown("<h2 style='text-align: center; letter-spacing: 4px; color: #ffffff; margin-top: 16px; margin-bottom: 0px; font-weight: 400;'>PRAVAH</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b8fa3; font-size: 16px; letter-spacing: 2px; margin-top: 0px; margin-bottom: 40px;'>Causal Risk Intelligence</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; color: #7c5cfc; font-size: 13px; font-weight: 700; letter-spacing: 2px; margin-bottom: 40px;'>WORKER SAFETY IS THE PRIORITY.</p>", unsafe_allow_html=True)
    
    def enter_app():
        st.session_state.splash_shown = True
        
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        st.button("ENTER PRAVAH", on_click=enter_app, use_container_width=True, type="primary")
        
    st.stop()

# --- Main Application Execution Begins Here ---

# Inject CSS
inject_custom_css()

# Initialize DB on first run
if not Path(DB_PATH).exists():
    with st.spinner("Initializing Database..."):
        seed_database()

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

if "selected_site" not in st.session_state:
    st.session_state.selected_site = "All Sites"

if "selected_report_id" not in st.session_state:
    st.session_state.selected_report_id = None

# Render global shell (sidebar + topbar logic handled within pages)
render_shell()
