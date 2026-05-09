"""ML model loader — loads precomputed artifacts at startup."""
import os
import json
import joblib
from flask import Flask
from app.core.config import Config
from app.core.logging_config import get_logger

logger = get_logger("model_loader")

# Module-level state (loaded once at startup)
_vectorizer = None
_tfidf_matrix = None
_similarity_matrix = None
_movie_index = None
_title_to_idx = None


def load_model(app: Flask = None) -> bool:
    """Load all ML artifacts from disk into memory.

    Called once during app startup. Returns True if loaded successfully.
    """
    global _vectorizer, _tfidf_matrix, _similarity_matrix, _movie_index, _title_to_idx

    artifacts_dir = Config.ARTIFACTS_DIR

    vectorizer_path = os.path.join(artifacts_dir, "tfidf_vectorizer.joblib")
    matrix_path = os.path.join(artifacts_dir, "tfidf_matrix.joblib")
    sim_path = os.path.join(artifacts_dir, "cosine_sim_matrix.joblib")
    index_path = os.path.join(artifacts_dir, "movie_index.json")

    if not os.path.exists(sim_path) or not os.path.exists(index_path):
        logger.warning("ml_artifacts_missing", path=artifacts_dir)
        return False

    _vectorizer = joblib.load(vectorizer_path)
    _tfidf_matrix = joblib.load(matrix_path)
    _similarity_matrix = joblib.load(sim_path)

    with open(index_path, "r", encoding="utf-8") as f:
        _movie_index = json.load(f)

    # Build title lookup (lowercase title → index)
    _title_to_idx = {}
    for i, movie in enumerate(_movie_index):
        title_lower = movie.get("title", "").lower().strip()
        _title_to_idx[title_lower] = i
        # Also index by TMDB ID
        tmdb_id = movie.get("id")
        if tmdb_id:
            _title_to_idx[f"id:{tmdb_id}"] = i

    logger.info(
        "ml_artifacts_loaded",
        movies=len(_movie_index),
        matrix_shape=str(_similarity_matrix.shape),
    )
    return True


def get_model_state() -> dict:
    """Return current model state for health checks."""
    return {
        "loaded": _similarity_matrix is not None,
        "movie_count": len(_movie_index) if _movie_index else 0,
    }


def get_similarity_matrix():
    return _similarity_matrix


def get_movie_index():
    return _movie_index


def get_title_to_idx():
    return _title_to_idx


def find_movie_index(query: str) -> int | None:
    """Find a movie's index by title or TMDB ID.

    Args:
        query: Movie title (case-insensitive) or "id:12345" format.

    Returns:
        Index in the movie list, or None if not found.
    """
    if _title_to_idx is None:
        return None

    # Try exact match first
    idx = _title_to_idx.get(query.lower().strip())
    if idx is not None:
        return idx

    # Try TMDB ID format
    if query.isdigit():
        idx = _title_to_idx.get(f"id:{query}")
        if idx is not None:
            return idx

    # Fuzzy: find closest title containing the query
    query_lower = query.lower().strip()
    for title, idx in _title_to_idx.items():
        if not title.startswith("id:") and query_lower in title:
            return idx

    return None
