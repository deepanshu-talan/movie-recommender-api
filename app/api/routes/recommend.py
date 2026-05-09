"""Recommendation endpoint."""
from flask import Blueprint, jsonify, request, abort
from app.services.recommendation_service import get_recommendations
from app.core.security import sanitize_input, limiter

recommend_bp = Blueprint("recommend", __name__)


@recommend_bp.route("/recommend", methods=["GET"])
@limiter.limit("30/minute")
def recommend():
    """Get ML-powered movie recommendations.

    Query params:
        movie_id (int): TMDB movie ID (preferred)
        title (str): Movie title (fallback lookup)
        count (int): Number of recommendations (default 10, max 20)
        industry (str): Optional saved cinema preference
        genre (str): Optional saved genre preference
        language (str): Optional saved language preference
    """
    movie_id = request.args.get("movie_id", type=int)
    title = sanitize_input(request.args.get("title", ""))
    count = request.args.get("count", 10, type=int)
    count = max(1, min(count, 20))
    preferences = {
        "industry": sanitize_input(request.args.get("industry", "all")),
        "genre": sanitize_input(request.args.get("genre", "all")),
        "language": sanitize_input(request.args.get("language", "all")),
    }

    if not movie_id and not title:
        abort(400, description="Provide either 'movie_id' or 'title' parameter.")

    result = get_recommendations(
        movie_id=movie_id,
        title=title,
        count=count,
        preferences=preferences,
    )

    return jsonify({
        "status": "success",
        "data": result["recommendations"],
        "meta": {
            "count": len(result["recommendations"]),
            "source": result["source"],
            "cached": result["cached"],
            "query": {"movie_id": movie_id, "title": title, "preferences": preferences},
        }
    }), 200
