"""Health check endpoint."""
from flask import Blueprint, jsonify
from app.ml.model_loader import get_model_state
from app.db.movie_db import get_db_stats

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Return application health status."""
    model = get_model_state()
    try:
        db = get_db_stats()
    except Exception:
        db = {"status": "error"}
    return jsonify({
        "status": "healthy",
        "model": model,
        "database": db,
    }), 200
