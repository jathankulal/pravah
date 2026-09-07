"""
PRAVAH — UI Components
Reusable UI elements like badges, causal chain visualizer.
"""

import streamlit as st
from pravah.config import SIF_COLORS, REVIEW_COLORS, COLORS

def render_badge(text: str, level: str):
    """Renders a styled HTML badge."""
    level_class = level.lower()
    html = f'<span class="badge badge-{level_class}">{text}</span>'
    st.markdown(html, unsafe_allow_html=True)

def render_causal_chain(nodes: dict):
    """Renders the causal chain visualization horizontally."""
    cols = st.columns(4)
    
    mapping = [
        ("Activity", "activity", "node-activity"),
        ("Hazardous Energy", "hazardous_energy", "node-energy"),
        ("Barrier Failure", "barrier_failure", "node-barrier"),
        ("Potential Consequence", "potential_consequence", "node-consequence")
    ]
    
    for i, (title, key, css_class) in enumerate(mapping):
        with cols[i]:
            val = nodes.get(key, "Unknown")
            html = f"""
            <div class="causal-node {css_class}">
                <div class="causal-node-title">{title}</div>
                <div class="causal-node-value">{val}</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            
            # Draw arrow between columns (except last)
            if i < 3:
                st.markdown("""
                    <div style="position: absolute; right: -20px; top: 40%; color: #8b8fa3;">
                        ▶
                    </div>
                """, unsafe_allow_html=True)

def render_sif_gauge(score: float):
    """Simple progress bar style gauge for SIF score."""
    color = COLORS['green']
    if score >= 0.8: color = COLORS['red']
    elif score >= 0.6: color = COLORS['amber']
    elif score >= 0.35: color = COLORS['purple']
    
    pct = int(score * 100)
    html = f"""
    <div style="width: 100%; background-color: #2a2d3a; border-radius: 4px; height: 8px; margin-top: 8px;">
        <div style="width: {pct}%; background-color: {color}; height: 100%; border-radius: 4px;"></div>
    </div>
    <div style="font-size: 11px; color: #8b8fa3; text-align: right; margin-top: 2px;">{score:.2f}</div>
    """
    st.markdown(html, unsafe_allow_html=True)
