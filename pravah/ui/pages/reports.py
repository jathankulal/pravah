"""
PRAVAH — Reports Page
High-density report management view.
"""

import streamlit as st
import pandas as pd
import json
import uuid
import requests
import logging
from pravah.database.queries import get_all_reports, insert_report
from pravah.config import COLORS, API_URL

def call_api_analyze_local(report_text: str):
    """Calls FastAPI /analyze endpoint"""
    try:
        response = requests.post(
            f"{API_URL.rstrip('/')}/analyze",
            json={"text": report_text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Batch API connection failed: {e}")
        return None

def render_page(site: str):
    st.markdown("<h2>Reports Database</h2>", unsafe_allow_html=True)
    
    # --- File Upload Section ---
    st.markdown("### Upload Reports")
    uploaded_file = st.file_uploader("Upload CSV or JSON reports", type=['csv', 'json'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_json(uploaded_file)
                
            st.write("Preview:", df_upload.head(3))
            
            if st.button("Process Uploaded Reports"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                total = len(df_upload)
                
                results = {'Critical/High': 0, 'Medium': 0, 'Low': 0}
                processed_data = []
                
                for idx, row in df_upload.iterrows():
                    status_text.text(f"Processing {idx+1}/{total}...")
                    
                    report_dict = row.to_dict()
                    description = report_dict.get('description', '')
                    
                    if not description:
                        st.warning(f"Row {idx}: Missing description. Skipping.")
                        continue
                        
                    # Call API
                    api_result = call_api_analyze_local(description)
                    if api_result:
                        report_dict['report_id'] = f"REP-{uuid.uuid4().hex[:8].upper()}"
                        
                        causal_nodes = api_result.get('causal_nodes', [])
                        if isinstance(causal_nodes, dict):
                            report_dict['activity_extracted'] = causal_nodes.get('activity')
                            report_dict['hazardous_energy'] = causal_nodes.get('hazardous_energy')
                            report_dict['barrier_failure'] = causal_nodes.get('barrier_failure')
                            report_dict['potential_consequence'] = causal_nodes.get('potential_consequence')
                        elif isinstance(causal_nodes, list) and len(causal_nodes) >= 4:
                            report_dict['activity_extracted'] = causal_nodes[0]
                            report_dict['hazardous_energy'] = causal_nodes[1]
                            report_dict['barrier_failure'] = causal_nodes[2]
                            report_dict['potential_consequence'] = causal_nodes[3]
                            
                        report_dict['sif_potential'] = api_result.get('sif_potential', 'Low')
                        report_dict['sif_score'] = api_result.get('sif_score', 0.0)
                        report_dict['lsr_mapped'] = api_result.get('lsr_mapped', [])
                        report_dict['confidence'] = api_result.get('confidence', 0.0)
                        report_dict['evidence'] = api_result.get('evidence', [])
                        
                        # Store in database
                        insert_report(report_dict)
                        processed_data.append(report_dict)
                        
                        sif = report_dict['sif_potential']
                        if sif in ['Critical', 'High']:
                            results['Critical/High'] += 1
                        elif sif == 'Medium':
                            results['Medium'] += 1
                        else:
                            results['Low'] += 1
                    else:
                        st.error(f"Row {idx}: API call failed. Skipping.")
                        
                    progress_bar.progress((idx + 1) / total)
                    
                status_text.text("Processing complete!")
                st.success(f"Uploaded {len(processed_data)} reports. {results['Critical/High']} High/Critical SIF, {results['Medium']} Medium, {results['Low']} Low")
                
                if processed_data:
                    st.dataframe(pd.DataFrame(processed_data)[['description', 'sif_potential', 'sif_score']])
                
                st.markdown("---")
        except Exception as e:
            logging.error(f"File upload processing error: {e}")
            st.error("Error processing file. Please ensure it is a valid CSV or JSON with a 'description' column.")
            
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
