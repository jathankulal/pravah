"""
PRAVAH — NLP Extractor (Hybrid MVP)
Uses Hugging Face Transformers for zero-shot classification,
with fallback to domain keyword rules to extract causal nodes.
"""

import spacy
import logging

logger = logging.getLogger(__name__)

# Check if the transformers package is installed (do NOT load any model here)
try:
    import transformers  # noqa: F401 — presence check only
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers package not installed. Zero-shot classification disabled; using keyword rules.")

# Module-level classifier cache — populated on first use by get_zero_shot_classifier()
classifier = None

# Try to load spaCy model, but gracefully fallback to simple keyword extraction if missing
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    SPACY_AVAILABLE = False
    logger.info("spaCy model 'en_core_web_sm' not found.")

def extract_causal_nodes_with_keywords(text: str) -> dict:
    """
    Fallback method: Extract nodes using basic keyword rules.
    """
    text_lower = text.lower()
    
    # Defaults
    nodes = {
        "activity": "Unknown activity",
        "hazardous_energy": "Unknown",
        "barrier_failure": "Unknown",
        "potential_consequence": "Unknown",
        "confidence_scores": {
            "activity": 0.5,
            "hazardous_energy": 0.5,
            "barrier_failure": 0.5,
            "potential_consequence": 0.5
        }
    }
    
    # Basic keyword-based extraction for MVP
    # Activity + initial energy assignment
    if "scaffold" in text_lower or "height" in text_lower:
        nodes["activity"] = "Work at height"
        nodes["hazardous_energy"] = "Gravitational (height)"
    elif "confined space" in text_lower or "tank entry" in text_lower or "vessel entry" in text_lower:
        nodes["activity"] = "Confined space entry"
    elif "lifting" in text_lower or "crane" in text_lower:
        nodes["activity"] = "Lifting operations"
        # Default struck-by for lifting; caught-in if entanglement evidence is present
        if any(kw in text_lower for kw in ("entangle", "caught", "caught-in", "pinch", "crush", "nip")):
            nodes["hazardous_energy"] = "Mechanical (caught-in)"
        else:
            nodes["hazardous_energy"] = "Mechanical (struck-by)"
    elif "weld" in text_lower or "grind" in text_lower or "cutting" in text_lower:
        nodes["activity"] = "Hot work"
        nodes["hazardous_energy"] = "Thermal (heat/fire)"

    # Energy overrides — evaluated after activity block so they always take precedence
    if "h2s" in text_lower or "toxic" in text_lower or "gas test" in text_lower:
        nodes["hazardous_energy"] = "Chemical (toxic/H2S)"
    elif "electrical" in text_lower or "shock" in text_lower or "415v" in text_lower:
        nodes["hazardous_energy"] = "Electrical"
    elif "pressure" in text_lower or "bar " in text_lower:
        nodes["hazardous_energy"] = "Pressure (confined gas)"
    elif any(kw in text_lower for kw in ("entangle", "caught-in", "pinch point", "pinch-point", "crushing")):
        # Standalone caught-in detection (not inside a lifting block)
        nodes["hazardous_energy"] = "Mechanical (caught-in)"
        
    # Barrier Failure
    _fall_protection_absent = (
        "no harness" in text_lower
        or "no fall arrest" in text_lower
        or "without a harness" in text_lower
        or "without fall protection" in text_lower
        or "without harness" in text_lower
        or "no ppe" in text_lower
        or "no safety harness" in text_lower
        or "without safety harness" in text_lower
    )
    if _fall_protection_absent:
        nodes["barrier_failure"] = "Missing fall protection"
    elif "gas test" in text_lower and ("old" in text_lower or "expired" in text_lower):
        nodes["barrier_failure"] = "Invalid gas test"
    elif "permit" in text_lower and ("no " in text_lower or "expired" in text_lower or "missing" in text_lower):
        nodes["barrier_failure"] = "Permit non-compliance"
    elif "bypassed" in text_lower or "overridden" in text_lower:
        nodes["barrier_failure"] = "Safety control bypassed"
    elif "lockout" in text_lower or "loto" in text_lower:
        nodes["barrier_failure"] = "LOTO failure"
        
    # Consequence
    if "fatal" in text_lower or "death" in text_lower:
        nodes["potential_consequence"] = "Fatality"
    elif "injury" in text_lower or "burn" in text_lower or "laceration" in text_lower:
        nodes["potential_consequence"] = "Serious injury"
    elif "drop" in text_lower or "fall" in text_lower:
         nodes["potential_consequence"] = "Lost-time injury"
         
    return nodes

def get_zero_shot_classifier():
    """
    Returns the zero-shot classification pipeline, initializing it on first call.
    The 1.63 GB facebook/bart-large-mnli model is only loaded when this function
    is actually invoked — never at import time.

    Returns None if the model cannot be loaded, so callers can fall back gracefully.
    """
    global classifier
    if classifier is not None:
        return classifier
    try:
        from transformers import pipeline
        logger.info("Lazy-loading zero-shot classifier (facebook/bart-large-mnli)...")
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        logger.info("Zero-shot classifier loaded successfully.")
        return classifier
    except Exception as e:
        logger.warning(f"Failed to load transformer model: {e}. Will use keyword fallback.")
        return None


def extract_causal_nodes_with_transformers(text: str) -> dict:
    """
    Uses Hugging Face zero-shot classifier + keyword rules.
    Falls back to keywords if transformers package is unavailable or model
    fails to load at runtime.
    """
    if not TRANSFORMERS_AVAILABLE:
        logger.info("Using keyword extraction (Transformers package not installed).")
        return extract_causal_nodes_with_keywords(text)

    clf = get_zero_shot_classifier()
    if clf is None:
        logger.info("Using keyword extraction (classifier unavailable at runtime).")
        return extract_causal_nodes_with_keywords(text)

    activities = ["Work at height", "Confined space entry", "Lifting operations", "Hot work", "Energy isolation"]
    energies = [
        "Gravitational (height)",
        "Chemical (toxic/H2S)",
        "Chemical (flammable)",
        "Mechanical (struck-by)",
        "Mechanical (caught-in)",
        "Electrical",
        "Thermal (heat/fire)",
        "Pressure (confined gas)",
        "Kinetic (vehicle)",
    ]
    barriers = ["Missing fall protection", "Invalid gas test", "Permit non-compliance", "Safety control bypassed", "LOTO failure"]
    consequences = ["Fatality", "Serious injury", "Lost-time injury", "Near miss"]

    try:
        # Use zero-shot pipeline for each causal category
        activity_res = clf(text, activities)
        energy_res = clf(text, energies)
        barrier_res = clf(text, barriers)
        consequence_res = clf(text, consequences)

        # Extract top predictions
        nodes = {
            "activity": activity_res['labels'][0] if activity_res['scores'][0] > 0.1 else "Unknown activity",
            "hazardous_energy": energy_res['labels'][0] if energy_res['scores'][0] > 0.1 else "Unknown",
            "barrier_failure": barrier_res['labels'][0] if barrier_res['scores'][0] > 0.1 else "Unknown",
            "potential_consequence": consequence_res['labels'][0] if consequence_res['scores'][0] > 0.1 else "Unknown",
            "confidence_scores": {
                "activity": float(activity_res['scores'][0]),
                "hazardous_energy": float(energy_res['scores'][0]),
                "barrier_failure": float(barrier_res['scores'][0]),
                "potential_consequence": float(consequence_res['scores'][0]),
            }
        }
        logger.info("Transformer extraction completed successfully.")
        return nodes
    except Exception as e:
        logger.warning(f"Transformer extraction failed: {e}. Falling back to keywords.")
        return extract_causal_nodes_with_keywords(text)

def extract_causal_nodes(text: str) -> dict:
    """
    Extract Activity, Hazardous Energy, Barrier Failure, and Potential Consequence
    from free text. Uses transformers as primary, falls back to keyword rules.
    """
    return extract_causal_nodes_with_transformers(text)
