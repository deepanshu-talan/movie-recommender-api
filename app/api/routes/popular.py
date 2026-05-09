"""Popular movies endpoint."""
from flask import Blueprint, jsonify, request
from app.services.tmdb_service import tmdb_service
from app.db.movie_db import get_category, save_category, is_stale, get_default_popular
from app.services.cache_service import cache_get, cache_set, cache_key, TTL_POPULAR
from app.core.config import Config

popular_bp = Blueprint("popular", __name__)


def _has_active_preferences(preferences: dict) -> bool:
    return any((preferences.get(key) or "all") != "all" for key in ("industry", "language", "genre"))


@popular_bp.route("/popular", methods=["GET"])
def popular():
    """Get popular movies with pagination.

    Flow: Redis → SQLite DB → TMDB API → save to DB + Redis.
    """
    page = request.args.get("page", 1, type=int)
    page = max(1, min(page, 500))
    preferences = {
        "industry": request.args.get("industry", "all"),
        "language": request.args.get("language", "all"),
        "genre": request.args.get("genre", "all"),
    }
    pref_key = (preferences["industry"], preferences["language"], preferences["genre"])

    # 1. Check Redis
    ck = cache_key("tmdb", "popular", "v2", page, *pref_key)
    cached = cache_get(ck)
    if cached:
        cached["source"] = "redis"
        return jsonify({"status": "success", "data": cached}), 200

    # 2. Check SQLite DB (if not stale for this page)
    if not is_stale("popular", page=page):
        db_data = get_category("popular", page=page, per_page=20, preferences=preferences)
        if db_data["results"]:
            db_data["source"] = "database"
            cache_set(ck, db_data, TTL_POPULAR)
            return jsonify({"status": "success", "data": db_data}), 200

    # 3. Fetch from TMDB API
    data = tmdb_service.discover_movies(page=page, sort_by="popularity.desc", preferences=preferences)
    if data["results"]:
        save_category("popular", data["results"], page=page,
                      stale_hours=Config.STALE_POPULAR)
        data["source"] = "tmdb_api"
        cache_set(ck, data, TTL_POPULAR)
        return jsonify({"status": "success", "data": data}), 200

    # 4. Fallback: stale DB data or default popular
    db_data = get_category("popular", page=page, per_page=20, preferences=preferences)
    if db_data["results"]:
        db_data["source"] = "database_stale"
        return jsonify({"status": "success", "data": db_data}), 200

    fallback = get_default_popular(limit=20)
    if _has_active_preferences(preferences):
        fallback = []
    return jsonify({
        "status": "success",
        "data": {"results": fallback, "total_pages": 1, "total_results": len(fallback), "page": 1},
        "source": "fallback",
    }), 200
