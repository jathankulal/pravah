"""
PRAVAH — Life-Saving Rules Page
"""

import streamlit as st
import json
from pathlib import Path
from pravah.config import COLORS, DATA_DIR

def render_page(site: str):
    st.markdown("<h2>IOGP Life-Saving Rules</h2>", unsafe_allow_html=True)
    
    lsr_path = DATA_DIR / "lsr_rules.json"
    if not lsr_path.exists():
        st.error("LSR rules data not found.")
        return
        
    with open(lsr_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
        
    # Display rules in a grid
    cols = st.columns(3)
    for i, rule in enumerate(rules):
        col = cols[i % 3]
        with col:
            html = f"""
            <div class="pravah-card" style="margin-bottom: 16px; min-height: 120px;">
                <div style="font-size: 24px; margin-bottom: 8px;">{rule['icon']}</div>
                <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px; color: {COLORS['white']};">{rule['rule_name']}</div>
                <div style="font-size: 12px; color: {COLORS['muted']};">{rule['description']}</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
