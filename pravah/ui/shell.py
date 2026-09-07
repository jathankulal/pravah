"""
PRAVAH — App Shell
Handles Sidebar navigation and Top Bar controls.
"""

import streamlit as st
from pravah.config import NAV_PAGES, SITES

def render_topbar(page_title: str):
    """Renders the top global controls bar."""
    # We use columns to simulate a top bar
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"### {page_title}")
        
    with col2:
        st.text_input("Global Search", placeholder="Search reports...", label_visibility="collapsed")
        
    with col3:
        site = st.selectbox(
            "Site", 
            options=["All Sites"] + SITES, 
            index=0, 
            label_visibility="collapsed",
            key="global_site_selector"
        )
        if site != st.session_state.selected_site:
            st.session_state.selected_site = site
            st.rerun()

def render_sidebar():
    """Renders the persistent sidebar."""
    with st.sidebar:
        st.markdown("### 🛡️ PRAVAH")
        st.markdown("<p style='font-size: 12px; color: #8b8fa3; margin-top: -10px; margin-bottom: 20px;'>Causal Risk Intelligence</p>", unsafe_allow_html=True)
        
        for page in NAV_PAGES:
            # We use buttons for navigation to control state
            is_active = st.session_state.current_page == page["key"]
            
            # Simple active state styling via markdown if active, else standard button
            if is_active:
                st.markdown(f"""
                <div style="background-color: #7c5cfc; color: white; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; font-weight: 600;">
                    {page['icon']} {page['label']}
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(f"{page['icon']} {page['label']}", key=f"nav_{page['key']}", use_container_width=True):
                    st.session_state.current_page = page["key"]
                    st.session_state.selected_report_id = None # Reset report selection on nav
                    st.rerun()
                    
        st.markdown("---")
        st.markdown("<div style='text-align: center; color: #8b8fa3; font-size: 11px;'>Environment: <span style='background: #2a2d3a; padding: 2px 6px; border-radius: 4px; color: #e8e9ed;'>DEMO</span></div>", unsafe_allow_html=True)

def render_shell():
    """Main routing function."""
    render_sidebar()
    
    page_key = st.session_state.current_page
    site = st.session_state.selected_site
    
    # Import pages dynamically to avoid circular imports
    if page_key == "overview":
        from pravah.ui.pages.overview import render_page
        render_page(site)
    elif page_key == "reports":
        from pravah.ui.pages.reports import render_page
        render_page(site)
    elif page_key == "causal_detail":
        from pravah.ui.pages.causal_detail import render_page
        render_page(site)
    elif page_key == "precursors":
        from pravah.ui.pages.precursors import render_page
        render_page(site)
    elif page_key == "hotspots":
        from pravah.ui.pages.hotspots import render_page
        render_page(site)
    elif page_key == "expert_review":
        from pravah.ui.pages.expert_review import render_page
        render_page(site)
    elif page_key == "lsr":
        from pravah.ui.pages.lsr import render_page
        render_page(site)
    else:
        st.error("Page not found.")
