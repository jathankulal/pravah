"""
PRAVAH — Deterministic Life-Saving Rule (LSR) Mapper
Maps extracted hazard and barrier combinations to standard IOGP rules.
"""

from pravah.config import LIFE_SAVING_RULES

# Simple mapping rules for MVP
MAPPING_RULES = {
    "Gravitational (height)": "Work at Height",
    "Chemical (toxic/H2S)": "Confined Space",
    "Electrical": "Energy Isolation",
    "Pressure (confined gas)": "Energy Isolation",
    "Thermal (heat/fire)": "Hot Work",
    "Kinetic (vehicle)": "Driving",
    "Mechanical (struck-by)": "Line of Fire",
    "Mechanical (caught-in)": "Line of Fire",
}

# Override based on specific activity or barrier keywords
OVERRIDE_RULES = {
    "confined space": "Confined Space",
    "lifting": "Lifting Operations",
    "crane": "Lifting Operations",
    "bypassed": "Bypassing Safety Controls",
    "overridden": "Bypassing Safety Controls",
    "permit": "Work Authorisation",
}

def map_to_lsr(activity: str, energy_type: str, barrier_failure: str) -> str:
    """
    Determine the most applicable Life-Saving Rule based on context.
    """
    combined_text = f"{activity} {energy_type} {barrier_failure}".lower()
    
    # 1. Check overrides first (highest specificity)
    for kw, rule in OVERRIDE_RULES.items():
        if kw in combined_text:
            return rule
            
    # 2. Check energy mapping
    if energy_type in MAPPING_RULES:
        return MAPPING_RULES[energy_type]
        
    # Default if no match
    return "Work Authorisation"
