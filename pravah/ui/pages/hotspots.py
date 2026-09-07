"""
PRAVAH — Hotspots Page
Risk matrix/heatmap and EW-SIF density by site.
"""

import streamlit as st
import pandas as pd
from pravah.database.queries import get_site_hotspots
from pravah.config import COLORS
import plotly.express as px

def render_page(site: str):
    st.markdown("<h2>Risk Hotspots</h2>", unsafe_allow_html=True)
    
    hotspots = get_site_hotspots()
    
    if not hotspots:
        st.info("No hotspot data available.")
        return
        
    df = pd.DataFrame(hotspots)
    
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.markdown("### Exposure-Weighted SIF Density by Site")
        
        # Simple bar chart using Plotly
        fig = px.bar(
            df, 
            x='site', 
            y='ew_sif_density',
            color='ew_sif_density',
            color_continuous_scale=[COLORS['green'], COLORS['amber'], COLORS['red']],
            labels={'site': 'Site', 'ew_sif_density': 'EW-SIF Density'}
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=COLORS['text'],
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    with col_right:
        st.markdown("### Site Rankings")
        st.dataframe(
            df,
            column_config={
                "ew_sif_density": st.column_config.ProgressColumn(
                    "EW-SIF Density",
                    format="%.2f",
                    min_value=0,
                    max_value=10, # Assuming max exposure * max SIF = 10
                )
            },
            hide_index=True,
            use_container_width=True
        )
