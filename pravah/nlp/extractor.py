"""
PRAVAH — NLP Extractor (Hybrid MVP)
Uses Hugging Face Transformers for zero-shot classification,
with fallback to domain keyword rules to extract causal nodes.
"""

import spacy
import logging

logger = logging.getLogger(__name__)

# Try to load Transformers model for zero-shot classification
try:
    from transformers import pipeline
    # Initialize zero-shot classification pipeline (lazy loading or global)
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    TRANSFORMERS_AVAILABLE = True
except (ImportError, OSError, Exception) as e:
    TRANSFORMERS_AVAILABLE = False
    logger.warning(f"Transformers pipeline could not be loaded: {e}. Falling back to keyword rules.")

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
    # Activity
    if "scaffold" in text_lower or "height" in text_lower:
        nodes["activity"] = "Work at height"
        nodes["hazardous_energy"] = "Gravitational"
    elif "confined space" in text_lower or "tank entry" in text_lower or "vessel entry" in text_lower:
        nodes["activity"] = "Confined space entry"
    elif "lifting" in text_lower or "crane" in text_lower:
        nodes["activity"] = "Lifting operations"
        nodes["hazardous_energy"] = "Mechanical"
    elif "weld" in text_lower or "grind" in text_lower or "cutting" in text_lower:
        nodes["activity"] = "Hot work"
        nodes["hazardous_energy"] = "Thermal"
        
    # Energy overrides
    if "h2s" in text_lower or "toxic" in text_lower or "gas test" in text_lower:
        nodes["hazardous_energy"] = "Chemical (toxic)"
    elif "electrical" in text_lower or "shock" in text_lower or "415v" in text_lower:
        nodes["hazardous_energy"] = "Electrical"
    elif "pressure" in text_lower or "bar " in text_lower:
        nodes["hazardous_energy"] = "Pressure"
        
    # Barrier Failure
    if "no harness" in text_lower or "no fall arrest" in text_lower:
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

def extract_causal_nodes_with_transformers(text: str) -> dict:
    """
    Uses Hugging Face zero-shot classifier + keyword rules.
    Falls back to keywords if transformers unavailable.
    """
    if not TRANSFORMERS_AVAILABLE:
        logger.info("Using keyword extraction method (Transformers unavailable).")
        return extract_causal_nodes_with_keywords(text)

    activities = ["Work at height", "Confined space entry", "Lifting operations", "Hot work", "Energy isolation"]
    energies = ["Gravitational", "Chemical (toxic)", "Electrical", "Thermal", "Pressure", "Mechanical"]
    barriers = ["Missing fall protection", "Invalid gas test", "Permit non-compliance", "Safety control bypassed", "LOTO failure"]
    consequences = ["Fatality", "Serious injury", "Lost-time injury", "Near miss"]
    
    try:
        # Use zero-shot pipeline for each category
        activity_res = classifier(text, activities)
        energy_res = classifier(text, energies)
        barrier_res = classifier(text, barriers)
        consequence_res = classifier(text, consequences)

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
        logger.info("Using transformer extraction method.")
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
