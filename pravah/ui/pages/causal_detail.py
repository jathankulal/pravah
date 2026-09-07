"""
PRAVAH — Causal Analysis / Report Detail
60/40 split view of a specific report.
"""

import streamlit as st
from pravah.database.queries import get_report_by_id, get_all_reports
from pravah.ui.components import render_causal_chain, render_sif_gauge
from pravah.config import COLORS

def render_page(site: str):
    report_id = st.session_state.get("selected_report_id")
    
    if not report_id:
        # If no report selected, just grab the first one for the site
        reports = get_all_reports(site)
        if not reports:
            st.info("No reports available.")
            return
        report_id = reports[0]["report_id"]
        
    report = get_report_by_id(report_id)
    if not report:
        st.error(f"Report {report_id} not found.")
        return
        
    st.markdown(f"<h2>Causal Analysis: {report_id}</h2>", unsafe_allow_html=True)
    
    # 60/40 Split
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.markdown("### Reconstructed Causal Chain")
        nodes = {
            "activity": report.get("activity_extracted", "Unknown"),
            "hazardous_energy": report.get("hazardous_energy", "Unknown"),
            "barrier_failure": report.get("barrier_failure", "Unknown"),
            "potential_consequence": report.get("potential_consequence", "Unknown"),
        }
        render_causal_chain(nodes)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### AI Risk Brief")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**SIF Potential:** {report.get('sif_potential')}")
            render_sif_gauge(report.get("sif_score", 0.0))
        with c2:
            st.markdown(f"**Life-Saving Rule:** {report.get('lsr_mapped')}")
            st.markdown(f"**Confidence:** {report.get('confidence', 0.0):.2f}")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Causal Evidence")
        evidence = report.get("evidence", [])
        if evidence:
            for item in evidence:
                st.markdown(f"- {item}")
        else:
            st.markdown("*No specific evidence extracted.*")
            
    with col_right:
        st.markdown("### Original Report")
        st.markdown(f"<div class='pravah-card'>{report.get('description')}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Metadata")
        st.markdown(f"**Site:** {report.get('site')}")
        st.markdown(f"**Date:** {report.get('date')}")
        st.markdown(f"**Reported By:** {report.get('reported_by')}")
        st.markdown(f"**Severity (Reported):** {report.get('severity_reported')}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Exposure Profile")
        st.markdown(f"**People Exposed:** {report.get('people_exposed')}")
        st.markdown(f"**Frequency:** {report.get('exposure_frequency')}")
        st.markdown(f"**Duration:** {report.get('exposure_duration_hrs')} hrs")
        st.markdown(f"**Exposure Index:** {report.get('exposure_index')}")
