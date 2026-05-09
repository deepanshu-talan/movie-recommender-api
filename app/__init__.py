"""Flask application factory."""
import time
from flask import Flask, jsonify, request, g

from app.core.config import Config
from app.core.logging_config import setup_logging, get_logger
from app.core.security import setup_security


def create_app(config_class=Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Setup logging
    setup_logging(app.config.get("LOG_LEVEL", "INFO"))
    logger = get_logger("app")

    # Setup security (CORS, rate limiting)
    setup_security(app)

    # Request timing middleware
    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request(response):
        latency = round((time.time() - g.get("start_time", time.time())) * 1000, 2)
        logger.info(
            "request_completed",
            method=request.method,
            path=request.path,
            status=response.status_code,
            latency_ms=latency,
        )
        return response

    # Register blueprints
    from app.api import register_blueprints
    register_blueprints(app)

    # Load ML model at startup
    with app.app_context():
        try:
            from app.ml.model_loader import load_model
            if load_model(app):
                logger.info("ml_model_loaded", status="success")
            else:
                logger.warning("ml_model_not_loaded", status="artifacts_missing")
        except Exception as e:
            logger.warning("ml_model_load_failed", error=str(e))

        # Initialize SQLite database (creates tables on first run)
        try:
            from app.db.movie_db import init_db
            init_db()
            logger.info("database_ready")
        except Exception as e:
            logger.error("database_init_failed", error=str(e))

        # Start background scheduler (pre-warms trending/popular)
        try:
            from app.services.scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.warning("scheduler_start_failed", error=str(e))

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"status": "error", "message": str(e.description)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"status": "error", "message": "Rate limit exceeded. Try again later."}), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.error("internal_server_error", error=str(e))
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app
