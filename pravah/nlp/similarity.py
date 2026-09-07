"""
PRAVAH — NLP Similarity & Clustering
Uses scikit-learn for cosine similarity and clustering of reports to find recurring precursors.
"""

import logging
from pravah.config import SIMILARITY_THRESHOLD, MIN_CLUSTER_SIZE
from pravah.nlp.embedder import get_embedding, get_embeddings_batch

logger = logging.getLogger(__name__)

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import AgglomerativeClustering
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed. Clustering will be disabled.")

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts."""
    if not SKLEARN_AVAILABLE:
        return 0.0
        
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    
    if emb1 is None or emb2 is None:
        return 0.0
        
    # Reshape for sklearn
    sim = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))
    return float(sim[0][0])

def cluster_reports(reports: list) -> dict:
    """
    Given a list of reports (dicts with 'report_id' and 'description'),
    cluster them based on semantic similarity of their descriptions.
    Returns a dict mapping report_id -> cluster_id.
    """
    if not SKLEARN_AVAILABLE or not reports:
        return {}
        
    descriptions = [r.get('description', '') for r in reports]
    ids = [r.get('report_id') for r in reports]
    
    embeddings = get_embeddings_batch(descriptions)
    if embeddings is None:
        return {}
        
    # Use Agglomerative Clustering with distance threshold
    # distance = 1 - similarity
    distance_threshold = 1.0 - SIMILARITY_THRESHOLD
    
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric='cosine',
        linkage='average'
    )
    
    labels = clustering.fit_predict(embeddings)
    
    # Format output
    result = {}
    for i, label in enumerate(labels):
        # Create a generic cluster ID, e.g., "Cluster-0"
        result[ids[i]] = f"Cluster-{label}"
        
    # Filter out clusters that are too small
    from collections import Counter
    counts = Counter(result.values())
    
    final_result = {}
    for r_id, c_id in result.items():
        if counts[c_id] >= MIN_CLUSTER_SIZE:
            final_result[r_id] = c_id
            
    return final_result
