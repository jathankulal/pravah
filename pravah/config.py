"""
PRAVAH — Centralized Configuration & Constants.
All thresholds, scoring weights, color mappings, and taxonomy references live here.
No logic is duplicated across pages.
"""

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = os.environ.get("DB_PATH", str(DATA_DIR / "pravah.db"))

# ── Network / API ──────────────────────────────────────────────────────────────
API_URL = os.environ.get("PRAVAH_API_URL", "http://127.0.0.1:8000")

# ── Exposure ───────────────────────────────────────────────────────────────────
EXPOSURE_FREQUENCY_WEIGHTS = {
    "Continuous": 1.0,
    "Frequent": 0.75,
    "Occasional": 0.4,
    "Rare": 0.15,
}
EXPOSURE_INDEX_MAX = 10.0  # normalisation ceiling

# ── SIF Scoring ────────────────────────────────────────────────────────────────
SIF_THRESHOLDS = {
    "Critical": 0.80,
    "High": 0.60,
    "Medium": 0.35,
    "Low": 0.0,
}

# Energy-type base hazard severity (0-1)
ENERGY_SEVERITY = {
    "Gravitational (height)": 0.90,
    "Chemical (toxic/H2S)": 0.95,
    "Chemical (flammable)": 0.85,
    "Mechanical (struck-by)": 0.70,
    "Mechanical (caught-in)": 0.75,
    "Electrical": 0.80,
    "Thermal (heat/fire)": 0.80,
    "Pressure (confined gas)": 0.85,
    "Kinetic (vehicle)": 0.75,
    "Radiation": 0.70,
}

# Barrier-failure severity multipliers
BARRIER_FAILURE_MULTIPLIERS = {
    "absent": 1.0,
    "bypassed": 0.95,
    "incomplete": 0.80,
    "degraded": 0.65,
    "present_but_inadequate": 0.50,
}

# Consequence-severity factors
CONSEQUENCE_SEVERITY = {
    "Fatality": 1.0,
    "Serious injury": 0.90,
    "Lost-time injury": 0.60,
    "Medical treatment": 0.40,
    "First aid": 0.20,
    "Near miss": 0.15,
    "No injury": 0.05,
}

# ── LSR Mapping ────────────────────────────────────────────────────────────────
# IOGP Life-Saving Rules (2019 revision)
LIFE_SAVING_RULES = [
    "Bypassing Safety Controls",
    "Confined Space",
    "Driving",
    "Energy Isolation",
    "Hot Work",
    "Line of Fire",
    "Lifting Operations",
    "Work at Height",
    "Work Authorisation",
]

# ── UI Colors ──────────────────────────────────────────────────────────────────
COLORS = {
    "bg_page": "#0f1117",
    "bg_card": "#1a1d29",
    "bg_card_hover": "#22253a",
    "border_card": "#2a2d3a",
    "border_hover": "#3d4158",
    "purple": "#7c5cfc",
    "purple_muted": "#6b4fd4",
    "cyan": "#00d4ff",
    "amber": "#ffb020",
    "red": "#ff4757",
    "green": "#2ed573",
    "muted": "#8b8fa3",
    "text": "#e8e9ed",
    "text_dim": "#a0a3b1",
    "white": "#ffffff",
}

# SIF level → color mapping
SIF_COLORS = {
    "Critical": COLORS["red"],
    "High": COLORS["amber"],
    "Medium": COLORS["purple"],
    "Low": COLORS["green"],
}

# Causal node accent colors
CAUSAL_NODE_COLORS = {
    "activity": COLORS["purple"],
    "hazardous_energy": COLORS["cyan"],
    "barrier_failure": COLORS["amber"],
    "consequence": COLORS["red"],
}

# Review status colors
REVIEW_COLORS = {
    "Pending": COLORS["amber"],
    "Confirmed": COLORS["green"],
    "Corrected": COLORS["cyan"],
    "Escalated": COLORS["red"],
}

# ── Precursor Clustering ──────────────────────────────────────────────────────
SIMILARITY_THRESHOLD = 0.72   # cosine similarity for grouping
MIN_CLUSTER_SIZE = 2          # minimum reports to form a pattern
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence-Transformers model

# ── UI Layout ──────────────────────────────────────────────────────────────────
SIDEBAR_WIDTH_PX = 232
TOPBAR_HEIGHT_PX = 64
CARD_RADIUS_PX = 14
CARD_PADDING_PX = 16
DASHBOARD_GAP_PX = 16
TABLE_ROW_HEIGHT_PX = 46

# ── Navigation Pages ──────────────────────────────────────────────────────────
NAV_PAGES = [
    {"label": "Home", "icon": "🏠", "key": "home"},
    {"label": "Overview", "icon": "📊", "key": "overview"},
    {"label": "Reports", "icon": "📋", "key": "reports"},
    {"label": "Causal Analysis", "icon": "🔗", "key": "causal_detail"},
    {"label": "Precursors", "icon": "🔄", "key": "precursors"},
    {"label": "Hotspots", "icon": "🔥", "key": "hotspots"},
    {"label": "Life-Saving Rules", "icon": "🛡️", "key": "lsr"},
    {"label": "Expert Review", "icon": "✅", "key": "expert_review"},
]

# ── Sites (for sample data & selectors) ───────────────────────────────────────
SITES = [
    "Hazira Processing Plant",
    "Mumbai High Offshore",
    "Duliajan Oil Field",
    "Rajahmundry Asset",
]
