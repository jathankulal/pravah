"""
PRAVAH — Text Embedder
Uses Sentence-Transformers to create embeddings for semantic similarity.
"""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Semantic similarity will be disabled.")

@lru_cache(maxsize=1)
def get_model():
    """Load the model once and cache it."""
    if not ST_AVAILABLE:
        return None
    logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    return SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    """Return embedding vector for a given text."""
    model = get_model()
    if model is None:
        return None
    return model.encode(text)

def get_embeddings_batch(texts: list):
    """Return embedding vectors for a list of texts."""
    model = get_model()
    if model is None:
        return None
    return model.encode(texts)
