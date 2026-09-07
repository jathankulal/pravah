"""
PRAVAH — UI Styles
Injects custom CSS to achieve the dark enterprise dashboard aesthetic.
"""

import streamlit as st
from pravah.config import COLORS, SIDEBAR_WIDTH_PX, TOPBAR_HEIGHT_PX

def inject_custom_css():
    """Inject global CSS overrides for Streamlit."""
    css = f"""
    <style>
    /* Global Backgrounds */
    .stApp {{
        background-color: {COLORS['bg_page']};
        color: {COLORS['text']};
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['bg_card']};
        border-right: 1px solid {COLORS['border_card']};
        min-width: {SIDEBAR_WIDTH_PX}px !important;
        max-width: {SIDEBAR_WIDTH_PX}px !important;
    }}
    
    /* Top Bar spacing */
    .block-container {{
        padding-top: {TOPBAR_HEIGHT_PX}px !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1440px !important;
    }}
    
    /* Cards */
    div[data-testid="stMetric"], .pravah-card {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border_card']};
        border-radius: 14px;
        padding: 16px;
        transition: border-color 0.2s ease, background-color 0.2s ease;
    }}
    div[data-testid="stMetric"]:hover, .pravah-card:hover {{
        border-color: {COLORS['border_hover']};
        background-color: {COLORS['bg_card_hover']};
    }}
    
    /* Typography Overrides */
    h1, h2, h3, h4, h5, h6, .stMarkdown p {{
        font-family: 'Inter', 'Geist', 'Plus Jakarta Sans', sans-serif !important;
    }}
    
    /* Metric Labels */
    [data-testid="stMetricLabel"] {{
        color: {COLORS['muted']} !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {COLORS['white']} !important;
        font-weight: 600 !important;
        font-size: 28px !important;
    }}
    
    /* Dataframes/Tables */
    [data-testid="stDataFrame"] {{
        background-color: {COLORS['bg_card']};
        border-radius: 14px;
        border: 1px solid {COLORS['border_card']};
        padding: 8px;
    }}
    
    /* Hide default Streamlit header */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    
    /* Badges */
    .badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        line-height: 1.5;
    }}
    .badge-critical {{ background-color: rgba(255, 71, 87, 0.2); color: {COLORS['red']}; border: 1px solid rgba(255, 71, 87, 0.4); }}
    .badge-high {{ background-color: rgba(255, 176, 32, 0.2); color: {COLORS['amber']}; border: 1px solid rgba(255, 176, 32, 0.4); }}
    .badge-medium {{ background-color: rgba(124, 92, 252, 0.2); color: {COLORS['purple']}; border: 1px solid rgba(124, 92, 252, 0.4); }}
    .badge-low {{ background-color: rgba(46, 213, 115, 0.2); color: {COLORS['green']}; border: 1px solid rgba(46, 213, 115, 0.4); }}
    
    /* Causal Node */
    .causal-node {{
        border: 1px solid {COLORS['border_card']};
        background-color: {COLORS['bg_card']};
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        position: relative;
    }}
    .causal-node-title {{
        font-size: 11px;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}
    .causal-node-value {{
        font-size: 14px;
        color: {COLORS['white']};
    }}
    .node-activity .causal-node-title {{ color: {COLORS['purple']}; }}
    .node-energy .causal-node-title {{ color: {COLORS['cyan']}; }}
    .node-barrier .causal-node-title {{ color: {COLORS['amber']}; }}
    .node-consequence .causal-node-title {{ color: {COLORS['red']}; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
