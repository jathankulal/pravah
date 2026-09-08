"""
PRAVAH — Database Data Access Layer
Centralizes all SQLite queries and data retrieval for the UI.
"""

import sqlite3
import json
from pravah.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_reports(site=None):
    """Retrieve reports, optionally filtered by site."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM reports"
    params = []
    
    if site and site != "All Sites":
        query += " WHERE site = ?"
        params.append(site)
        
    query += " ORDER BY date DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to dict and parse JSON arrays
    result = []
    for row in rows:
        r_dict = dict(row)
        r_dict["evidence"] = json.loads(r_dict.get("evidence", "[]"))
        result.append(r_dict)
    return result

def get_report_by_id(report_id):
    """Retrieve a single report by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        r_dict = dict(row)
        r_dict["evidence"] = json.loads(r_dict.get("evidence", "[]"))
        return r_dict
    return None

def get_dashboard_kpis(site=None):
    """Calculate the 4 main KPIs for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause = "WHERE site = ?" if site and site != "All Sites" else ""
    params = [site] if site and site != "All Sites" else []
    
    # Total reports
    cursor.execute(f"SELECT COUNT(*) FROM reports {where_clause}", params)
    total_reports = cursor.fetchone()[0]
    
    # SIF count
    cursor.execute(f"SELECT COUNT(*) FROM reports {where_clause} " + 
                   ("AND " if where_clause else "WHERE ") + 
                   "sif_potential IN ('Critical', 'High')", params)
    sif_count = cursor.fetchone()[0]
    
    # Precursors count
    cursor.execute(f"SELECT COUNT(DISTINCT precursor_cluster_id) FROM reports {where_clause} " +
                   ("AND " if where_clause else "WHERE ") + "precursor_cluster_id IS NOT NULL", params)
    precursor_count = cursor.fetchone()[0]
    
    # EW-SIF Density
    ew_sif = get_ew_sif_density(site)
    
    conn.close()
    return {
        "total_reports": total_reports,
        "sif_count": sif_count,
        "ew_sif_density": ew_sif,
        "precursor_count": precursor_count
    }

def get_ew_sif_density(site=None):
    """Calculate Exposure-Weighted SIF Density."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause = "WHERE site = ?" if site and site != "All Sites" else ""
    params = [site] if site and site != "All Sites" else []
    
    query = f"""
        SELECT 
            SUM(sif_score * exposure_index) / SUM(exposure_index) as ew_density
        FROM reports 
        {where_clause}
        HAVING SUM(exposure_index) > 0
    """
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] is not None:
        return float(row[0])
    return 0.0

def get_site_hotspots():
    """Get aggregated risk stats per site."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            site,
            total_reports,
            sif_count,
            ROUND(ew_sif_density, 2) as ew_sif_density
        FROM v_site_stats
        ORDER BY ew_sif_density DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
    
def get_precursor_clusters(site=None):
    """Retrieve precursor clusters with their report counts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause = "WHERE r.site = ?" if site and site != "All Sites" else ""
    params = [site] if site and site != "All Sites" else []
    
    query = f"""
        SELECT 
            c.cluster_id,
            c.name,
            c.dominant_barrier_failure,
            COUNT(r.report_id) as report_count
        FROM precursor_clusters c
        JOIN reports r ON c.cluster_id = r.precursor_cluster_id
        {where_clause}
        GROUP BY c.cluster_id, c.name, c.dominant_barrier_failure
        ORDER BY report_count DESC
    """
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_pending_reviews(site=None):
    """Get reports requiring expert review."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM reports WHERE review_status = 'Pending'"
    params = []
    
    if site and site != "All Sites":
        query += " AND site = ?"
        params.append(site)
        
    query += " ORDER BY sif_score DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        r_dict = dict(row)
        r_dict["evidence"] = json.loads(r_dict.get("evidence", "[]"))
        result.append(r_dict)
    return result

def update_review_status(report_id, new_status, reviewer_name="Expert User", notes=""):
    """Update report review status and log the action."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current state
    cursor.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,))
    original = dict(cursor.fetchone() or {})
    
    # Update report
    cursor.execute("UPDATE reports SET review_status = ? WHERE report_id = ?", (new_status, report_id))
    
    # Log review
    cursor.execute("""
        INSERT INTO reviews (report_id, reviewer_name, action, original_state, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (report_id, reviewer_name, new_status, json.dumps(original), notes))
    
    conn.commit()
    conn.close()
    return True

def insert_report(report_data: dict):
    """Insert a new report into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO reports (
            report_id, site, report_type, date, reported_by, description, 
            severity_reported, people_exposed, exposure_frequency, 
            exposure_duration_hrs, exposure_index, activity_extracted, 
            hazardous_energy, barrier_failure, potential_consequence, 
            sif_potential, sif_score, lsr_mapped, confidence, review_status, evidence
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """
    
    # Calculate exposure index if missing
    exposure_index = report_data.get('exposure_index')
    if exposure_index is None:
        freq_map = {'Rare': 1, 'Occasional': 2, 'Frequent': 3, 'Continuous': 4}
        freq_val = freq_map.get(report_data.get('exposure_frequency', 'Occasional'), 2)
        people = float(report_data.get('people_exposed', 1))
        duration = float(report_data.get('exposure_duration_hrs', 1.0))
        exposure_index = people * freq_val * duration
        
    params = (
        report_data.get('report_id', str(hash(report_data.get('description', '')))),
        report_data.get('site', 'Unknown Site'),
        report_data.get('report_type', 'Incident'),
        report_data.get('date', '2026-01-01'),
        report_data.get('reported_by', 'System Upload'),
        report_data.get('description', ''),
        report_data.get('severity_reported', 'Low'),
        report_data.get('people_exposed', 1),
        report_data.get('exposure_frequency', 'Occasional'),
        report_data.get('exposure_duration_hrs', 1.0),
        exposure_index,
        report_data.get('activity_extracted', ''),
        report_data.get('hazardous_energy', ''),
        report_data.get('barrier_failure', ''),
        report_data.get('potential_consequence', ''),
        report_data.get('sif_potential', 'Low'),
        report_data.get('sif_score', 0.0),
        json.dumps(report_data.get('lsr_mapped', [])), # Store as JSON string or string
        report_data.get('confidence', 0.0),
        report_data.get('review_status', 'Pending'),
        json.dumps(report_data.get('evidence', []))
    )
    
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return True
