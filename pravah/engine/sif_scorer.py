"""
PRAVAH — Deterministic SIF Scorer
Calculates Serious Injury and Fatality (SIF) potential using deterministic rules.
"""

from pravah.config import (
    ENERGY_SEVERITY, 
    BARRIER_FAILURE_MULTIPLIERS, 
    CONSEQUENCE_SEVERITY,
    SIF_THRESHOLDS
)

def calculate_sif_potential(energy_type: str, barrier_failure: str, consequence: str) -> dict:
    """
    Calculate SIF score and potential based on extracted nodes.
    Returns dict with score, potential level, and evidence.
    """
    evidence = []
    
    # 1. Base Energy Score
    base_score = ENERGY_SEVERITY.get(energy_type, 0.5)
    evidence.append(f"Hazardous Energy: {energy_type} (Base: {base_score:.2f})")
    
    # 2. Barrier Multiplier
    # Map raw text to a multiplier category
    bf_lower = barrier_failure.lower() if barrier_failure else ""
    if not bf_lower or "absent" in bf_lower or "missing" in bf_lower or "no " in bf_lower:
        multiplier = BARRIER_FAILURE_MULTIPLIERS["absent"]
        cat = "absent"
    elif "bypass" in bf_lower or "overridden" in bf_lower:
        multiplier = BARRIER_FAILURE_MULTIPLIERS["bypassed"]
        cat = "bypassed"
    elif "incomplete" in bf_lower or "partial" in bf_lower:
        multiplier = BARRIER_FAILURE_MULTIPLIERS["incomplete"]
        cat = "incomplete"
    else:
        multiplier = BARRIER_FAILURE_MULTIPLIERS["degraded"]
        cat = "degraded"
        
    evidence.append(f"Barrier Failure: {cat} (Multiplier: {multiplier:.2f})")
    
    # 3. Consequence Weight
    cons_lower = consequence.lower() if consequence else ""
    
    _fatality_kws = ("fatal", "death", "died", "killed")
    _serious_kws = (
        "serious injury", "severe injury", "permanent injury",
        "hospitali", "fracture", "severe burn", "flash fire",
        "explosion", "collapse", "unconscious", "serious exposure",
        "crushing", "burn", "amputation"
    )
    _lti_kws = (
        "lost-time", "lost time", "lti", "struck-by", "caught-in",
        "laceration", "injury"
    )
    
    if any(kw in cons_lower for kw in _fatality_kws):
        cons_weight = CONSEQUENCE_SEVERITY["Fatality"]
        cat = "Fatality"
    elif any(kw in cons_lower for kw in _serious_kws):
        cons_weight = CONSEQUENCE_SEVERITY["Serious injury"]
        cat = "Serious injury"
    elif any(kw in cons_lower for kw in _lti_kws):
        cons_weight = CONSEQUENCE_SEVERITY["Lost-time injury"]
        cat = "Lost-time injury"
    else:
        cons_weight = CONSEQUENCE_SEVERITY["Near miss"]
        cat = "Near miss/Other"
        
    evidence.append(f"Potential Consequence: {cat} (Weight: {cons_weight:.2f})")
    
    # 4. Final Calculation
    raw_score = base_score * multiplier * cons_weight
    
    # Cap at 1.0
    final_score = min(1.0, raw_score)
    
    # 5. Determine Level
    level = "Low"
    if final_score >= SIF_THRESHOLDS["Critical"]:
        level = "Critical"
    elif final_score >= SIF_THRESHOLDS["High"]:
        level = "High"
    elif final_score >= SIF_THRESHOLDS["Medium"]:
        level = "Medium"
        
    return {
        "score": round(final_score, 2),
        "level": level,
        "evidence": evidence
    }
