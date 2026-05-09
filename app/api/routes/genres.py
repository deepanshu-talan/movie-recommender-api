"""Genre list endpoint."""
from flask import Blueprint, jsonify
from app.services.tmdb_service import tmdb_service
from app.db.movie_db import get_genres as db_get_genres, save_genres, is_stale
from app.services.cache_service import cache_get, cache_set, cache_key, TTL_GENRES

genres_bp = Blueprint("genres", __name__)


@genres_bp.route("/genres", methods=["GET"])
def genres():
    """Get genre ID → name mapping.

    Flow: Redis → SQLite DB → TMDB API → save to DB + Redis.
    """
    # 1. Check Redis
    ck = cache_key("tmdb", "genres")
    cached = cache_get(ck)
    if cached:
        return jsonify({"status": "success", "data": cached, "source": "redis"}), 200

    # 2. Check SQLite DB (if not stale)
    if not is_stale("genres", page=1):
        db_data = db_get_genres()
        if db_data:
            cache_set(ck, db_data, TTL_GENRES)
            return jsonify({"status": "success", "data": db_data, "source": "database"}), 200

    # 3. Fetch from TMDB API
    data = tmdb_service.get_genre_list()
    if data:
        save_genres(data)
        cache_set(ck, data, TTL_GENRES)
        return jsonify({"status": "success", "data": data, "source": "tmdb_api"}), 200

    # 4. Fallback: return stale DB data
    db_data = db_get_genres()
    if db_data:
        return jsonify({"status": "success", "data": db_data, "source": "database_stale"}), 200

    return jsonify({"status": "success", "data": {}, "source": "none"}), 200
