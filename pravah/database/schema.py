"""
PRAVAH — SQLite Database Schema Definitions
"""

SCHEMA_SQL = """
-- Drop tables if they exist to allow clean seeding
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS precursor_clusters;

-- Precursor Clusters Table
CREATE TABLE precursor_clusters (
    cluster_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    dominant_barrier_failure TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main Reports Table
CREATE TABLE reports (
    report_id TEXT PRIMARY KEY,
    site TEXT NOT NULL,
    report_type TEXT NOT NULL,
    date TEXT NOT NULL,
    reported_by TEXT NOT NULL,
    description TEXT NOT NULL,
    severity_reported TEXT NOT NULL,
    
    -- Exposure Fields
    people_exposed INTEGER NOT NULL DEFAULT 1,
    exposure_frequency TEXT NOT NULL DEFAULT 'Occasional',
    exposure_duration_hrs REAL NOT NULL DEFAULT 1.0,
    exposure_index REAL NOT NULL DEFAULT 1.0,
    
    -- Extracted Causal Nodes
    activity_extracted TEXT,
    hazardous_energy TEXT,
    barrier_failure TEXT,
    potential_consequence TEXT,
    
    -- Derived Risk Intelligence
    sif_potential TEXT,
    sif_score REAL,
    lsr_mapped TEXT,
    precursor_cluster_id TEXT,
    confidence REAL,
    
    -- Status and Arrays
    review_status TEXT DEFAULT 'Pending',
    evidence TEXT, -- JSON array
    
    FOREIGN KEY(precursor_cluster_id) REFERENCES precursor_clusters(cluster_id)
);

-- Reviews Table
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL,
    reviewer_name TEXT NOT NULL,
    action TEXT NOT NULL, -- Confirm, Correct, Escalate, Note
    original_state TEXT, -- JSON
    new_state TEXT, -- JSON
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES reports(report_id)
);

-- Views for Analytics
CREATE VIEW IF NOT EXISTS v_site_stats AS
SELECT 
    site,
    COUNT(*) as total_reports,
    SUM(CASE WHEN sif_potential IN ('Critical', 'High') THEN 1 ELSE 0 END) as sif_count,
    -- Exposure-Weighted SIF Density: Sum(sif_score * exposure_index) / Sum(exposure_index)
    CASE 
        WHEN SUM(exposure_index) > 0 THEN SUM(sif_score * exposure_index) / SUM(exposure_index)
        ELSE 0 
    END as ew_sif_density
FROM reports
GROUP BY site;
"""
