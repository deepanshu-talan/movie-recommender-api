"""Cosine similarity lookup from precomputed matrix."""
import numpy as np


def get_similar_movies(
    movie_index: int,
    similarity_matrix: np.ndarray,
    movie_list: list,
    count: int = 10,
    exclude_self: bool = True,
) -> list:
    """Get top-N similar movies for a given movie index.

    Args:
        movie_index: Row index in the similarity matrix.
        similarity_matrix: Precomputed cosine similarity matrix.
        movie_list: List of movie metadata dicts (same order as matrix).
        count: Number of recommendations to return.
        exclude_self: Whether to exclude the queried movie.

    Returns:
        List of dicts with movie metadata + similarity score.
    """
    if movie_index < 0 or movie_index >= len(movie_list):
        return []

    # Get similarity scores for this movie
    sim_scores = list(enumerate(similarity_matrix[movie_index]))

    # Sort by similarity descending
    sim_scores.sort(key=lambda x: x[1], reverse=True)

    # Skip self (index 0 if sorted) and take top N
    start = 1 if exclude_self else 0
    top_scores = sim_scores[start : start + count]

    results = []
    for idx, score in top_scores:
        movie = movie_list[idx].copy()
        movie["similarity"] = round(float(score), 4)
        movie["match_percentage"] = round(float(score) * 100, 1)
        results.append(movie)

    return results


def hybrid_score(similarity: float, popularity: float, vote_avg: float) -> float:
    """Compute hybrid ranking score.

    Weights: 70% content similarity + 15% popularity + 15% rating.
    """
    norm_pop = min(popularity / 100.0, 1.0)
    norm_rating = vote_avg / 10.0
    return 0.70 * similarity + 0.15 * norm_pop + 0.15 * norm_rating
