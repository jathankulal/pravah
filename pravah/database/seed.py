"""
PRAVAH — Database Seeder
Loads sample data from JSON into the SQLite database.
"""

import json
import sqlite3
from pathlib import Path
import logging

from pravah.config import DB_PATH
from pravah.database.schema import SCHEMA_SQL

logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def seed_database():
    """Initialise schema and load sample reports."""
    logger.info(f"Seeding database at {DB_PATH}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create schema
    cursor.executescript(SCHEMA_SQL)
    
    # 2. Insert dummy precursor clusters
    clusters = [
        ("PC-001", "Missing Fall Protection", "Recurring pattern of work at height without harness or edge protection.", "No fall arrest harness"),
        ("PC-002", "Confined Space Ventilation", "Repeated failure to maintain or verify ventilation in confined spaces.", "Ventilation interrupted"),
        ("PC-003", "LOTO Non-Compliance", "Failures in applying or verifying lockout/tagout.", "No LOTO applied"),
        ("PC-004", "Lifting Operations Control", "Poor planning or execution of lifts.", "Wrong lifting gear"),
        ("PC-005", "Hot Work Controls", "Failures in hot work permits or fire watches.", "No hot work permit"),
        ("PC-006", "Driving / Transport Safety", "Violations of safe driving rules.", "Speeding")
    ]
    cursor.executemany(
        "INSERT INTO precursor_clusters (cluster_id, name, description, dominant_barrier_failure) VALUES (?, ?, ?, ?)",
        clusters
    )
    
    # 3. Load sample reports
    sample_data_path = Path(__file__).resolve().parent.parent.parent / "data" / "sample_reports.json"
    with open(sample_data_path, 'r', encoding='utf-8') as f:
        reports = json.load(f)
        
    for report in reports:
        evidence_json = json.dumps(report.get("evidence", []))
        cursor.execute(
            """
            INSERT INTO reports (
                report_id, site, report_type, date, reported_by, description, severity_reported,
                people_exposed, exposure_frequency, exposure_duration_hrs, exposure_index,
                activity_extracted, hazardous_energy, barrier_failure, potential_consequence,
                sif_potential, sif_score, lsr_mapped, precursor_cluster_id, confidence,
                review_status, evidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report["report_id"], report["site"], report["report_type"], report["date"],
                report["reported_by"], report["description"], report["severity_reported"],
                report["people_exposed"], report["exposure_frequency"], report["exposure_duration_hrs"],
                report["exposure_index"], report.get("activity_extracted"), report.get("hazardous_energy"),
                report.get("barrier_failure"), report.get("potential_consequence"), report.get("sif_potential"),
                report.get("sif_score"), report.get("lsr_mapped"), report.get("precursor_cluster_id"),
                report.get("confidence"), report.get("review_status", "Pending"), evidence_json
            )
        )
        
    conn.commit()
    conn.close()
    logger.info("Database seeding complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()
