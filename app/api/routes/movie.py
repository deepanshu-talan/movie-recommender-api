"""Movie detail endpoint."""
from flask import Blueprint, jsonify, abort
from app.services.tmdb_service import tmdb_service
from app.db.movie_db import (
    get_movie as db_get_movie, save_movie as db_save_movie, is_movie_stale,
)
from app.services.cache_service import cache_get, cache_set, cache_key, TTL_MOVIE

movie_bp = Blueprint("movie", __name__)


@movie_bp.route("/movie/<int:movie_id>", methods=["GET"])
def get_movie(movie_id: int):
    """Get detailed movie info by TMDB ID.

    Flow: Redis → SQLite DB → TMDB API → save to DB + Redis.
    """
    if movie_id < 1:
        abort(400, description="Invalid movie ID.")

    # 1. Check Redis (hot cache)
    ck = cache_key("tmdb", "movie", movie_id)
    cached = cache_get(ck)
    if cached:
        return jsonify({"status": "success", "data": cached, "source": "redis"}), 200

    # 2. Check SQLite DB (persistent store)
    movie = db_get_movie(movie_id)
    if movie and not is_movie_stale(movie_id):
        cache_set(ck, movie, TTL_MOVIE)
        return jsonify({"status": "success", "data": movie, "source": "database"}), 200

    # 3. Fetch from TMDB API
    movie = tmdb_service.get_movie_details(movie_id)
    if not movie:
        # 4. Fallback: return stale DB data if API fails
        stale = db_get_movie(movie_id)
        if stale:
            return jsonify({"status": "success", "data": stale, "source": "database_stale"}), 200
        abort(404, description=f"Movie with ID {movie_id} not found.")

    # Save to DB + Redis
    db_save_movie(movie)
    cache_set(ck, movie, TTL_MOVIE)
    return jsonify({"status": "success", "data": movie, "source": "tmdb_api"}), 200
