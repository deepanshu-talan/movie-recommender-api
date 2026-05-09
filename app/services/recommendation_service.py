"""Recommendation service — orchestrates ML engine + TMDB fallback."""
from app.ml.model_loader import find_movie_index, get_similarity_matrix, get_movie_index
from app.ml.similarity import get_similar_movies
from app.services.tmdb_service import tmdb_service
from app.services.cache_service import cache_get, cache_set, cache_key, TTL_RECOMMEND
from app.core.logging_config import get_logger

logger = get_logger("recommendation_service")

INDUSTRY_LANGUAGES = {
    "hollywood": "en",
    "bollywood": "hi",
    "korean": "ko",
    "japanese": "ja",
}

GENRE_IDS = {
    28: "action",
    12: "adventure",
    16: "animation",
    35: "comedy",
    80: "crime",
    99: "documentary",
    18: "drama",
    10751: "family",
    14: "fantasy",
    36: "history",
    27: "horror",
    10402: "music",
    9648: "mystery",
    10749: "romance",
    878: "science fiction",
    53: "thriller",
    10770: "tv movie",
    10752: "war",
    37: "western",
}


def _normalize_preferences(preferences: dict | None) -> dict:
    prefs = preferences or {}
    return {
        "industry": (prefs.get("industry") or "all").lower(),
        "genre": (prefs.get("genre") or "all").lower(),
        "language": (prefs.get("language") or "all").lower(),
    }


def _genre_names(movie: dict) -> set[str]:
    names = set()
    for genre in movie.get("genres") or []:
        if isinstance(genre, dict):
            value = genre.get("name") or genre.get("id")
        else:
            value = genre

        if isinstance(value, int):
            name = GENRE_IDS.get(value)
        elif isinstance(value, str) and value.isdigit():
            name = GENRE_IDS.get(int(value))
        else:
            name = str(value).lower() if value is not None else ""

        if name:
            names.add(str(name).lower())
    return names


def _matches_preferences(movie: dict, preferences: dict) -> bool:
    original_language = (movie.get("original_language") or "").lower()
    industry = preferences["industry"]
    language = preferences["language"]
    genre = preferences["genre"]

    industry_language = INDUSTRY_LANGUAGES.get(industry)
    if industry_language and original_language != industry_language:
        return False
    if not industry_language and language != "all" and original_language != language:
        return False
    if genre != "all" and genre not in _genre_names(movie):
        return False
    return True


def _apply_preferences(movies: list[dict], preferences: dict) -> list[dict]:
    if preferences == {"industry": "all", "genre": "all", "language": "all"}:
        return movies
    return [movie for movie in movies if _matches_preferences(movie, preferences)]


def get_recommendations(
    movie_id: int = None,
    title: str = None,
    count: int = 10,
    preferences: dict | None = None,
) -> dict:
    """Get movie recommendations using ML engine with TMDB fallback.

    Priority:
    1. Check Redis cache
    2. Use precomputed similarity matrix (if movie is in dataset)
    3. Fall back to TMDB's /recommendations endpoint
    """
    preferences = _normalize_preferences(preferences)

    # Build cache key. Preferences are part of identity so saved choices do not
    # reuse older, unfiltered recommendation results.
    query = str(movie_id) if movie_id else title
    ck = cache_key(
        "recommend",
        query,
        count,
        preferences["industry"],
        preferences["genre"],
        preferences["language"],
    )

    # Check cache
    cached = cache_get(ck)
    if cached:
        return {"recommendations": cached, "source": "cache", "cached": True}

    # Try ML engine
    sim_matrix = get_similarity_matrix()
    movie_list = get_movie_index()

    if sim_matrix is not None and movie_list:
        # Find movie in our index
        lookup = f"id:{movie_id}" if movie_id else title
        idx = find_movie_index(lookup) if lookup else None

        if idx is not None:
            candidate_count = min(len(movie_list), max(count * 5, count))
            candidates = get_similar_movies(idx, sim_matrix, movie_list, candidate_count)
            results = _apply_preferences(candidates, preferences)[:count]
            cache_set(ck, results, TTL_RECOMMEND)
            logger.info(
                "recommendations_served",
                source="ml_engine",
                movie=query,
                count=len(results),
                preferences=preferences,
            )
            return {"recommendations": results, "source": "ml_engine", "cached": False}

    # Fallback: TMDB recommendations
    if movie_id:
        results = tmdb_service.get_recommendations(movie_id)
        if results:
            # Add synthetic similarity scores
            filtered = _apply_preferences(results, preferences)
            for i, movie in enumerate(filtered[:count]):
                movie["similarity"] = round(1.0 - (i * 0.03), 4)
                movie["match_percentage"] = round(movie["similarity"] * 100, 1)
            results = filtered[:count]
            cache_set(ck, results, TTL_RECOMMEND)
            logger.info(
                "recommendations_served",
                source="tmdb_fallback",
                movie_id=movie_id,
                count=len(results),
                preferences=preferences,
            )
            return {"recommendations": results, "source": "tmdb_fallback", "cached": False}

    logger.warning("no_recommendations_found", query=query)
    return {"recommendations": [], "source": "none", "cached": False}
