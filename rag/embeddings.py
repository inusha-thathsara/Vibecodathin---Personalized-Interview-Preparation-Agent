import logging
from typing import List
import config

logger = logging.getLogger(__name__)

try:
    import numpy as np
except ImportError:
    np = None

def get_embedding(text: str) -> List[float]:
    """
    Generate text embedding using Gemini API if key is present.
    If no key or in offline mode, returns empty list.
    """
    key = config.GEMINI_API_KEY
    if not key:
        return []

    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        
        for m in ["models/embedding-001", "embedding-001", "models/text-embedding-004"]:
            try:
                res = genai.embed_content(
                    model=m,
                    content=text,
                    task_type="retrieval_document"
                )
                emb = res.get("embedding", [])
                if emb:
                    return emb
            except Exception:
                continue

        return []
    except Exception as e:
        logger.warning(f"Error calling Gemini embedding API: {e}")
        return []

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two vector representations."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0

    if np is not None:
        a = np.array(v1, dtype=float)
        b = np.array(v2, dtype=float)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    dot = sum(x * y for x, y in zip(v1, v2))
    norm_a = sum(x * x for x in v1) ** 0.5
    norm_b = sum(y * y for y in v2) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
