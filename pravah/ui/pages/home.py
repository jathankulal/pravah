"""
PRAVAH — Home Page
"""

import streamlit as st
from pravah.config import COLORS

def render_page(site: str):
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hero Section
    col1, col2 = st.columns([6, 4])
    
    with col1:
        st.markdown(f"<h1 style='font-size: 42px; font-weight: 800; line-height: 1.2; margin-bottom: 20px;'>TURN SAFETY REPORTS INTO<br><span style='color: {COLORS['purple']};'>EARLY SIF RISK INTELLIGENCE</span></h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 18px; color: {COLORS['text_dim']}; line-height: 1.6; max-width: 600px; margin-bottom: 30px;'>PRAVAH analyzes safety reports to identify hazardous energy, barrier failures, potential consequences, and recurring SIF precursors before they become serious incidents.</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 13px; font-weight: 700; letter-spacing: 2px; color: {COLORS['muted']}; margin-bottom: 40px;'>WORKER SAFETY IS THE PRIORITY.</p>", unsafe_allow_html=True)
        
        b1, b2, b3 = st.columns([2, 2, 3])
        
        def go_reports():
            st.session_state.current_page = "reports"
            
        def go_dashboard():
            st.session_state.current_page = "overview"
            
        with b1:
            st.button("Analyze a Report →", on_click=go_reports, type="primary", use_container_width=True)
        with b2:
            st.button("Explore Dashboard →", on_click=go_dashboard, use_container_width=True)
            
    with col2:
        # Core Pravah Visual
        st.markdown(f"""
        <div style='background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border_card']}; border-radius: 16px; padding: 30px; margin-top: 10px;'>
            <div style='text-align: center;'>
                <div style='background-color: {COLORS['bg_page']}; border: 1px solid {COLORS['purple']}; padding: 12px; border-radius: 8px; font-weight: 600; color: {COLORS['white']}; letter-spacing: 1px;'>Activity</div>
                <div style='color: {COLORS['muted']}; font-size: 20px; margin: 8px 0;'>↓</div>
                <div style='background-color: {COLORS['bg_page']}; border: 1px solid {COLORS['cyan']}; padding: 12px; border-radius: 8px; font-weight: 600; color: {COLORS['white']}; letter-spacing: 1px;'>Hazardous Energy</div>
                <div style='color: {COLORS['muted']}; font-size: 20px; margin: 8px 0;'>↓</div>
                <div style='background-color: {COLORS['bg_page']}; border: 1px solid {COLORS['amber']}; padding: 12px; border-radius: 8px; font-weight: 600; color: {COLORS['white']}; letter-spacing: 1px;'>Barrier Failure</div>
                <div style='color: {COLORS['muted']}; font-size: 20px; margin: 8px 0;'>↓</div>
                <div style='background-color: {COLORS['bg_page']}; border: 1px solid {COLORS['red']}; padding: 12px; border-radius: 8px; font-weight: 600; color: {COLORS['white']}; letter-spacing: 1px;'>Potential Consequence</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br><hr style='border-color: #2a2d3a;'><br>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 40px; letter-spacing: 2px;'>HOW PRAVAH WORKS</h3>", unsafe_allow_html=True)
    
    s1, s2, s3 = st.columns(3)
    
    with s1:
        st.markdown(f"""
        <div style='padding: 20px; border-left: 2px solid {COLORS['purple']};'>
            <h4 style='color: {COLORS['purple']}; margin-bottom: 8px; font-size: 14px; letter-spacing: 1px;'>01 — ANALYZE</h4>
            <p style='color: {COLORS['text_dim']}; font-size: 15px;'>Read and structure safety reports.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with s2:
        st.markdown(f"""
        <div style='padding: 20px; border-left: 2px solid {COLORS['cyan']};'>
            <h4 style='color: {COLORS['cyan']}; margin-bottom: 8px; font-size: 14px; letter-spacing: 1px;'>02 — IDENTIFY</h4>
            <p style='color: {COLORS['text_dim']}; font-size: 15px;'>Detect hazardous energy, barrier failures, and SIF precursor patterns.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with s3:
        st.markdown(f"""
        <div style='padding: 20px; border-left: 2px solid {COLORS['red']};'>
            <h4 style='color: {COLORS['red']}; margin-bottom: 8px; font-size: 14px; letter-spacing: 1px;'>03 — PREDICT</h4>
            <p style='color: {COLORS['text_dim']}; font-size: 15px;'>Assess SIF potential and highlight emerging risk.</p>
        </div>
        """, unsafe_allow_html=True)
