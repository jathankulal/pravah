"""
PRAVAH — Overview Dashboard
Row 1: KPIs
Row 2: Risk Trend & AI Brief
Row 3: Causal Chain
Row 4: Priority Reports Table
"""

import streamlit as st
import pandas as pd
from pravah.database.queries import get_dashboard_kpis, get_all_reports
from pravah.ui.components import render_badge, render_causal_chain
from pravah.config import COLORS

def render_page(site: str):
    # Top bar via columns
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.markdown(f"<h2>Overview Dashboard</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: {COLORS['muted']};'>Primary risk intelligence for {site}</p>", unsafe_allow_html=True)
    with col_t2:
        # We can put global controls here later if shell.py doesn't handle them well enough
        pass

    # Row 1: KPIs
    kpis = get_dashboard_kpis(site)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reports", kpis["total_reports"])
    with col2:
        st.metric("SIF Potential (High/Crit)", kpis["sif_count"])
    with col3:
        # Note the tooltip requirement from the plan
        st.metric("EW-SIF Density", f"{kpis['ew_sif_density']:.2f}", help="Exposure-Weighted SIF Density = Σ(sif_score × exposure_index) / Σ(exposure_index)")
    with col4:
        st.metric("Recurring Precursors", kpis["precursor_count"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2 & 3: Causal Chain (Featured)
    reports = get_all_reports(site)
    critical_reports = [r for r in reports if r['sif_potential'] in ('Critical', 'High')]
    featured = critical_reports[0] if critical_reports else (reports[0] if reports else None)

    if featured:
        st.markdown("### Highest Priority Causal Chain")
        st.markdown(f"<p style='color: {COLORS['muted']};'>Report {featured['report_id']} — {featured['sif_potential']} Potential</p>", unsafe_allow_html=True)
        
        nodes = {
            "activity": featured.get("activity_extracted", "Unknown"),
            "hazardous_energy": featured.get("hazardous_energy", "Unknown"),
            "barrier_failure": featured.get("barrier_failure", "Unknown"),
            "potential_consequence": featured.get("potential_consequence", "Unknown"),
        }
        render_causal_chain(nodes)
        
        st.markdown("<br>", unsafe_allow_html=True)

    # Row 4: Priority Reports Table
    st.markdown("### Priority Reports")
    
    if reports:
        # Format for dataframe
        df_data = []
        for r in reports[:10]: # Limit to top 10 for overview
            df_data.append({
                "ID": r["report_id"],
                "Date": r["date"],
                "Activity": r.get("activity_extracted", ""),
                "SIF Potential": r.get("sif_potential", ""),
                "Score": float(r.get("sif_score", 0.0)),
                "LSR": r.get("lsr_mapped", ""),
                "Exposure": float(r.get("exposure_index", 0.0)),
                "Review": r.get("review_status", "")
            })
            
        df = pd.DataFrame(df_data)
        
        # Use Streamlit's dataframe with some column config
        st.dataframe(
            df,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score",
                    help="SIF Score",
                    format="%.2f",
                    min_value=0,
                    max_value=1,
                ),
                "Exposure": st.column_config.NumberColumn(
                    "Exposure",
                    help="Exposure Index",
                    format="%.1f",
                )
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No reports found for this site.")
