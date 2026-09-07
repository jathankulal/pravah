"""
PRAVAH — Expert Review Page
Queue for reviewing and correcting AI outputs.
"""

import streamlit as st
from pravah.database.queries import get_pending_reviews, update_review_status
from pravah.ui.components import render_causal_chain
from pravah.config import COLORS

def render_page(site: str):
    st.markdown("<h2>Expert Review Queue</h2>", unsafe_allow_html=True)
    
    pending = get_pending_reviews(site)
    
    if not pending:
        st.success("No pending reviews!")
        return
        
    col_left, col_right = st.columns([3, 7])
    
    if "review_selected" not in st.session_state:
        st.session_state.review_selected = pending[0]['report_id']
        
    with col_left:
        st.markdown("### Pending")
        for p in pending:
            is_selected = st.session_state.review_selected == p['report_id']
            bg_color = COLORS['bg_card_hover'] if is_selected else COLORS['bg_card']
            
            html = f"""
            <div style="background-color: {bg_color}; border: 1px solid {COLORS['border_card']}; border-radius: 8px; padding: 12px; margin-bottom: 8px; cursor: pointer;">
                <div style="font-weight: 600; color: {COLORS['white']};">{p['report_id']}</div>
                <div style="font-size: 12px; color: {COLORS['muted']};">SIF: {p['sif_potential']} ({p['sif_score']:.2f})</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            if st.button(f"Review {p['report_id']}", key=f"rev_{p['report_id']}"):
                st.session_state.review_selected = p['report_id']
                st.rerun()
                
    with col_right:
        selected_r = next((r for r in pending if r['report_id'] == st.session_state.review_selected), None)
        
        if selected_r:
            st.markdown(f"### Reviewing: {selected_r['report_id']}")
            
            nodes = {
                "activity": selected_r.get("activity_extracted", "Unknown"),
                "hazardous_energy": selected_r.get("hazardous_energy", "Unknown"),
                "barrier_failure": selected_r.get("barrier_failure", "Unknown"),
                "potential_consequence": selected_r.get("potential_consequence", "Unknown"),
            }
            render_causal_chain(nodes)
            
            st.markdown("<br>", unsafe_allow_html=True)
            notes = st.text_area("Review Notes", placeholder="Add any correction notes here...")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("✅ Confirm", use_container_width=True):
                    update_review_status(selected_r['report_id'], "Confirmed", notes=notes)
                    st.success("Confirmed!")
                    st.session_state.review_selected = None
                    st.rerun()
            with c2:
                if st.button("✏️ Correct", use_container_width=True):
                    update_review_status(selected_r['report_id'], "Corrected", notes=notes)
                    st.success("Marked as Corrected!")
                    st.session_state.review_selected = None
                    st.rerun()
            with c3:
                if st.button("⚠️ Escalate", use_container_width=True):
                    update_review_status(selected_r['report_id'], "Escalated", notes=notes)
                    st.success("Escalated!")
                    st.session_state.review_selected = None
                    st.rerun()
