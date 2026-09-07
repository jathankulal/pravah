"""
PRAVAH — Causal Engine Orchestrator
Processes a free-text report through extraction, scoring, and mapping.
"""

from pravah.nlp.extractor import extract_causal_nodes
from pravah.engine.sif_scorer import calculate_sif_potential
from pravah.engine.lsr_mapper import map_to_lsr

def process_report(text: str) -> dict:
    """
    End-to-end processing of a safety report.
    Returns a dictionary with all causal nodes, SIF score, LSR mapping, and evidence.
    """
    # 1. Extract Nodes
    nodes = extract_causal_nodes(text)
    
    # 2. Calculate SIF Potential
    sif_result = calculate_sif_potential(
        energy_type=nodes["hazardous_energy"],
        barrier_failure=nodes["barrier_failure"],
        consequence=nodes["potential_consequence"]
    )
    
    # 3. Map to Life-Saving Rule
    lsr = map_to_lsr(
        activity=nodes["activity"],
        energy_type=nodes["hazardous_energy"],
        barrier_failure=nodes["barrier_failure"]
    )
    
    # 4. Compile Result
    # Simple confidence estimation based on how many nodes were successfully extracted (not "Unknown")
    unknowns = sum(1 for v in nodes.values() if "unknown" in str(v).lower())
    confidence = max(0.5, 1.0 - (unknowns * 0.15))
    
    return {
        "causal_nodes": nodes,
        "sif_potential": sif_result["level"],
        "sif_score": sif_result["score"],
        "lsr_mapped": lsr,
        "confidence": round(confidence, 2),
        "evidence": sif_result["evidence"]
    }
