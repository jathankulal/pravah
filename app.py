"""
PRAVAH — Streamlit Entry Point
"""

import streamlit as st
import logging
from pravah.ui.shell import render_shell
from pravah.ui.styles import inject_custom_css
from pravah.database.seed import seed_database
from pathlib import Path
from pravah.config import DB_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)

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

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "overview"

if "selected_site" not in st.session_state:
    st.session_state.selected_site = "All Sites"

if "selected_report_id" not in st.session_state:
    st.session_state.selected_report_id = None

# Render global shell (sidebar + topbar logic handled within pages)
render_shell()
