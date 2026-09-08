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
from pravah.config import DB_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)

def call_api_analyze(report_text: str):
    """Calls FastAPI /analyze endpoint"""
    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json={"text": report_text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

# Page configuration
st.set_page_config(
    page_title="PRAVAH | Causal Risk Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
inject_custom_css()

# Initialize DB on first run
if not Path(DB_PATH).exists():
    with st.spinner("Initializing Database..."):
        seed_database()

st.info("Make sure FastAPI is running on localhost:8000")

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "overview"

if "selected_site" not in st.session_state:
    st.session_state.selected_site = "All Sites"

if "selected_report_id" not in st.session_state:
    st.session_state.selected_report_id = None

# Render global shell (sidebar + topbar logic handled within pages)
render_shell()
