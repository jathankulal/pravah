"""
PRAVAH — Precursors Page
Displays recurring precursor patterns.
"""

import streamlit as st
import pandas as pd
from pravah.database.queries import get_precursor_clusters, get_all_reports
from pravah.config import COLORS

def render_page(site: str):
    st.markdown("<h2>Recurring Precursors</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {COLORS['muted']};'>Semantic clusters of repeated barrier failures</p>", unsafe_allow_html=True)
    
    clusters = get_precursor_clusters(site)
    
    if not clusters:
        st.info("No recurring precursor patterns identified yet.")
        return
        
    # Top metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Active Patterns", len(clusters))
    with c2:
        st.metric("Total Reports in Patterns", sum(c['report_count'] for c in clusters))
    with c3:
        pass
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Left: Patterns, Right: Details
    col_left, col_right = st.columns([4, 6])
    
    if "selected_cluster" not in st.session_state:
        st.session_state.selected_cluster = clusters[0]['cluster_id']
        
    with col_left:
        st.markdown("### Ranked Patterns")
        for c in clusters:
            is_selected = st.session_state.selected_cluster == c['cluster_id']
            
            # Use columns to make a clickable row
            bg_color = COLORS['bg_card_hover'] if is_selected else COLORS['bg_card']
            border_color = COLORS['purple'] if is_selected else COLORS['border_card']
            
            html = f"""
            <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 12px; margin-bottom: 8px; cursor: pointer;">
                <div style="font-weight: 600; color: {COLORS['white']};">{c['name']}</div>
                <div style="font-size: 12px; color: {COLORS['muted']};">{c['report_count']} reports</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            if st.button(f"View {c['cluster_id']}", key=f"btn_{c['cluster_id']}"):
                st.session_state.selected_cluster = c['cluster_id']
                st.rerun()
                
    with col_right:
        selected_c = next((c for c in clusters if c['cluster_id'] == st.session_state.selected_cluster), None)
        if selected_c:
            st.markdown(f"### {selected_c['name']}")
            st.markdown(f"**Dominant Barrier Failure:** {selected_c['dominant_barrier_failure']}")
            
            st.markdown("#### Linked Reports")
            reports = get_all_reports(site)
            cluster_reports = [r for r in reports if r.get('precursor_cluster_id') == selected_c['cluster_id']]
            
            if cluster_reports:
                df_data = []
                for r in cluster_reports:
                    df_data.append({
                        "ID": r["report_id"],
                        "Date": r["date"],
                        "Activity": r.get("activity_extracted", ""),
                        "SIF": r.get("sif_potential", "")
                    })
                st.dataframe(pd.DataFrame(df_data), hide_index=True, use_container_width=True)
