"""
PRAVAH — Reports Page
High-density report management view.
"""

import streamlit as st
import pandas as pd
from pravah.database.queries import get_all_reports
from pravah.config import COLORS

def render_page(site: str):
    st.markdown("<h2>Reports Database</h2>", unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sif_filter = st.selectbox("SIF Potential", ["All", "Critical", "High", "Medium", "Low"])
    with col2:
        lsr_filter = st.selectbox("Life-Saving Rule", ["All", "Work at Height", "Confined Space", "Energy Isolation", "Lifting Operations", "Hot Work", "Driving", "Line of Fire", "Bypassing Safety Controls", "Work Authorisation"])
    with col3:
        status_filter = st.selectbox("Review Status", ["All", "Pending", "Confirmed", "Corrected", "Escalated"])
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Apply Filters", use_container_width=True):
            pass # Triggers a rerun with new selections
            
    reports = get_all_reports(site)
    
    # Apply filters
    if sif_filter != "All":
        reports = [r for r in reports if r.get('sif_potential') == sif_filter]
    if lsr_filter != "All":
        reports = [r for r in reports if r.get('lsr_mapped') == lsr_filter]
    if status_filter != "All":
        reports = [r for r in reports if r.get('review_status') == status_filter]
        
    st.markdown(f"<p style='color: {COLORS['muted']};'>{len(reports)} reports found</p>", unsafe_allow_html=True)
    
    if reports:
        df_data = []
        for r in reports:
            # Create a shortened description
            desc = r.get("description", "")
            short_desc = desc[:80] + "..." if len(desc) > 80 else desc
            
            df_data.append({
                "ID": r["report_id"],
                "Date": r["date"],
                "Description": short_desc,
                "SIF Potential": r.get("sif_potential", ""),
                "Score": float(r.get("sif_score", 0.0)),
                "Exposure": float(r.get("exposure_index", 0.0)),
                "Review": r.get("review_status", "")
            })
            
        df = pd.DataFrame(df_data)
        
        # Display table
        event = st.dataframe(
            df,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score",
                    format="%.2f",
                    min_value=0,
                    max_value=1,
                )
            },
            hide_index=True,
            use_container_width=True,
            selection_mode="single-row",
            on_select="rerun"
        )
        
        # Handle selection
        if event and len(event.selection.rows) > 0:
            selected_idx = event.selection.rows[0]
            selected_id = df.iloc[selected_idx]["ID"]
            st.session_state.selected_report_id = selected_id
            st.session_state.current_page = "causal_detail"
            st.rerun()
            
    else:
        st.info("No reports match the current filters.")
