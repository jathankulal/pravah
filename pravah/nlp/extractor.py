"""
PRAVAH — NLP Extractor (Hybrid MVP)
Uses spaCy and domain keyword rules to extract causal nodes.
"""

import spacy
import logging

logger = logging.getLogger(__name__)

# Try to load spaCy model, but gracefully fallback to simple keyword extraction if missing
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy model 'en_core_web_sm' not found. Falling back to keyword rules.")

def extract_causal_nodes(text: str) -> dict:
    """
    Extract Activity, Hazardous Energy, Barrier Failure, and Potential Consequence
    from free text using a hybrid of spaCy (if available) and keyword rules.
    """
    text_lower = text.lower()
    
    # Defaults
    nodes = {
        "activity": "Unknown activity",
        "hazardous_energy": "Unknown",
        "barrier_failure": "Unknown",
        "potential_consequence": "Unknown"
    }
    
    # Basic keyword-based extraction for MVP
    # Activity
    if "scaffold" in text_lower or "height" in text_lower:
        nodes["activity"] = "Work at height"
        nodes["hazardous_energy"] = "Gravitational (height)"
    elif "confined space" in text_lower or "tank entry" in text_lower or "vessel entry" in text_lower:
        nodes["activity"] = "Confined space entry"
    elif "lifting" in text_lower or "crane" in text_lower:
        nodes["activity"] = "Lifting operations"
        nodes["hazardous_energy"] = "Mechanical (struck-by)"
    elif "weld" in text_lower or "grind" in text_lower or "cutting" in text_lower:
        nodes["activity"] = "Hot work"
        nodes["hazardous_energy"] = "Thermal (heat/fire)"
        
    # Energy overrides
    if "h2s" in text_lower or "toxic" in text_lower or "gas test" in text_lower:
        nodes["hazardous_energy"] = "Chemical (toxic/H2S)"
    elif "electrical" in text_lower or "shock" in text_lower or "415v" in text_lower:
        nodes["hazardous_energy"] = "Electrical"
    elif "pressure" in text_lower or "bar " in text_lower:
        nodes["hazardous_energy"] = "Pressure (confined gas)"
        
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
         nodes["potential_consequence"] = "Serious injury / fatality"
         
    return nodes
