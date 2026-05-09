"""Search endpoint — proxies TMDB search with DB persistence + caching."""
import re

from flask import Blueprint, jsonify, request, abort
from app.services.tmdb_service import tmdb_service
from app.db.movie_db import search_movies as db_search, save_movies, get_default_popular
from app.services.cache_service import cache_get, cache_set, cache_key, TTL_SEARCH
from app.core.security import sanitize_input, limiter

search_bp = Blueprint("search", __name__)


def _normalize_title(value: str) -> str:
    """Normalize a title/query for local-vs-TMDB relevance checks."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (value or "").lower())).strip()


def _has_title_match(query: str, movies: list[dict]) -> bool:
    """Return True when local results actually match the requested title text."""
    query_norm = _normalize_title(query)
    if not query_norm:
        return False

    for movie in movies:
        title_norm = _normalize_title(movie.get("title", ""))
        if title_norm == query_norm or query_norm in title_norm:
            return True
    return False


def _sort_title_matches(query: str, movies: list[dict]) -> list[dict]:
    """Prefer exact title matches, then title-prefix/contains matches."""
    query_norm = _normalize_title(query)

    def score(movie: dict) -> tuple:
        title_norm = _normalize_title(movie.get("title", ""))
        if title_norm == query_norm:
            rank = 0
        elif title_norm.startswith(query_norm):
            rank = 1
        elif query_norm in title_norm:
            rank = 2
        else:
            rank = 3
        return (rank, -float(movie.get("popularity") or 0), -float(movie.get("vote_average") or 0))

    return sorted(movies, key=score)


def _dedupe_movies(movies: list[dict]) -> list[dict]:
    """Remove duplicate movies while preserving result order."""
    seen = set()
    unique = []
    for movie in movies:
        key = _normalize_title(movie.get("title", "")) or movie.get("id")
        if key in seen:
            continue
        seen.add(key)
        unique.append(movie)
    return unique


@search_bp.route("/search", methods=["GET"])
@limiter.limit("60/minute")
def search_movies():
    """Search movies by title query.

    Flow: Redis → SQLite FTS5 → TMDB API → save to DB + Redis.
    """
    query = sanitize_input(request.args.get("q", ""))
    page = request.args.get("page", 1, type=int)

    if not query or len(query) < 2:
        abort(400, description="Query parameter 'q' must be at least 2 characters.")

    if page < 1 or page > 500:
        abort(400, description="Page must be between 1 and 500.")

    # 1. Check Redis (hot cache)
    ck = cache_key("tmdb", "search", query, page)
    cached = cache_get(ck)
    if cached:
        cached_results = cached.get("results", []) if isinstance(cached, dict) else []
        cached_source = cached.get("source") if isinstance(cached, dict) else None
        if cached_source != "database" or _has_title_match(query, cached_results):
            cached["source"] = "redis"
            return jsonify({"status": "success", "data": cached}), 200

    # 2. Check SQLite DB (FTS5 full-text search)
    db_data = db_search(query, page)
    if db_data["results"] and _has_title_match(query, db_data["results"]):
        db_data["results"] = _dedupe_movies(_sort_title_matches(query, db_data["results"]))
        db_data["source"] = "database"
        cache_set(ck, db_data, TTL_SEARCH)
        return jsonify({"status": "success", "data": db_data}), 200

    # 3. Fetch from TMDB API when local results are missing or only loosely similar.
    data = tmdb_service.search_movies(query, page)
    if data["results"]:
        data["results"] = _dedupe_movies(_sort_title_matches(query, data["results"]))
        # Save all fetched movies to DB for future searches
        save_movies(data["results"])
        data["source"] = "tmdb_api"
        cache_set(ck, data, TTL_SEARCH)
        return jsonify({"status": "success", "data": data}), 200

    # 4. Fallback: return empty with source info
    data["source"] = "none"
    return jsonify({"status": "success", "data": data}), 200
