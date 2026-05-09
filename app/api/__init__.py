"""Blueprint registration."""
from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all API route blueprints."""
    from app.api.routes.health import health_bp
    from app.api.routes.search import search_bp
    from app.api.routes.movie import movie_bp
    from app.api.routes.recommend import recommend_bp
    from app.api.routes.trending import trending_bp
    from app.api.routes.popular import popular_bp
    from app.api.routes.genres import genres_bp
    from app.api.routes.high_rated import high_rated_bp
    from app.api.routes.videos import videos_bp

    prefix = "/api/v1"
    app.register_blueprint(health_bp, url_prefix=prefix)
    app.register_blueprint(search_bp, url_prefix=prefix)
    app.register_blueprint(movie_bp, url_prefix=prefix)
    app.register_blueprint(recommend_bp, url_prefix=prefix)
    app.register_blueprint(trending_bp, url_prefix=prefix)
    app.register_blueprint(popular_bp, url_prefix=prefix)
    app.register_blueprint(genres_bp, url_prefix=prefix)
    app.register_blueprint(high_rated_bp, url_prefix=prefix)
    app.register_blueprint(videos_bp, url_prefix=prefix)
