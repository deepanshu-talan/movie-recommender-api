"""Trending movies endpoint."""
from flask import Blueprint, jsonify, request
from app.services.tmdb_service import tmdb_service
from app.db.movie_db import get_category, get_filtered_movies, save_category, is_stale, get_default_popular
from app.services.cache_service import cache_get, cache_set, cache_key, TTL_TRENDING
from app.core.config import Config

trending_bp = Blueprint("trending", __name__)


def _has_active_preferences(preferences: dict) -> bool:
    return any((preferences.get(key) or "all") != "all" for key in ("industry", "language", "genre"))


@trending_bp.route("/trending", methods=["GET"])
def trending():
    """Get weekly trending movies.

    Flow: Redis → SQLite DB → TMDB API → save to DB + Redis.
    """
    preferences = {
        "industry": request.args.get("industry", "all"),
        "language": request.args.get("language", "all"),
        "genre": request.args.get("genre", "all"),
    }
    pref_key = (preferences["industry"], preferences["language"], preferences["genre"])

    # 1. Check Redis
    ck = cache_key("tmdb", "trending", "week", "v3", *pref_key)
    cached = cache_get(ck)
    if cached:
        return jsonify({"status": "success", "data": cached, "source": "redis"}), 200

    # 2. Check SQLite DB (if not stale)
    if not is_stale("trending", page=1):
        db_data = get_category("trending", page=1, per_page=20, preferences=preferences)
        if db_data["results"]:
            cache_set(ck, db_data["results"], TTL_TRENDING)
            return jsonify({"status": "success", "data": db_data["results"], "source": "database"}), 200

    # 3. For active preferences, TMDB trending cannot be queried by genre or
    # language, so use Discover as a preference-aware trending backup.
    if _has_active_preferences(preferences):
        discovered = tmdb_service.discover_movies(
            page=1,
            sort_by="popularity.desc",
            preferences=preferences,
        )
        if discovered["results"]:
            cache_set(ck, discovered["results"], TTL_TRENDING)
            return jsonify({
                "status": "success",
                "data": discovered["results"],
                "source": "tmdb_discover",
            }), 200

    # 4. Fetch from TMDB API
    data = tmdb_service.get_trending(time_window="week")
    if data:
        save_category("trending", data, page=1, stale_hours=Config.STALE_TRENDING)
        db_data = get_category("trending", page=1, per_page=20, preferences=preferences)
        filtered = db_data["results"] if _has_active_preferences(preferences) else data
        if filtered:
            cache_set(ck, filtered, TTL_TRENDING)
        return jsonify({"status": "success", "data": filtered, "source": "tmdb_api"}), 200

    # 5. Fallback: stale DB data or default popular
    db_data = get_category("trending", page=1, per_page=20, preferences=preferences)
    if db_data["results"]:
        return jsonify({"status": "success", "data": db_data["results"], "source": "database_stale"}), 200

    if _has_active_preferences(preferences):
        fallback_data = get_filtered_movies(preferences=preferences, sort="recent", per_page=20)
        if fallback_data["results"]:
            cache_set(ck, fallback_data["results"], TTL_TRENDING)
            return jsonify({
                "status": "success",
                "data": fallback_data["results"],
                "source": "recent_database",
            }), 200

    fallback = get_default_popular(limit=20)
    if _has_active_preferences(preferences):
        fallback = []
    return jsonify({"status": "success", "data": fallback, "source": "fallback"}), 200
