"""Movie video/trailer endpoint."""
from flask import Blueprint, jsonify, abort

from app.services.local_movie_service import get_movie
from app.services.tmdb_service import tmdb_service

videos_bp = Blueprint("videos", __name__)


@videos_bp.route("/movie/<int:movie_id>/videos", methods=["GET"])
def movie_videos(movie_id: int):
    """Get movie videos from TMDB, with a YouTube search fallback."""
    if movie_id < 1:
        abort(400, description="Invalid movie ID.")

    videos = tmdb_service.get_movie_videos(movie_id)
    movie = get_movie(movie_id) or {}
    fallback_query = movie.get("title", f"movie {movie_id}")

    return jsonify({
        "status": "success",
        "data": {
            "results": videos,
            "fallback_url": f"https://www.youtube.com/results?search_query={fallback_query.replace(' ', '+')}+official+trailer",
        },
    }), 200
