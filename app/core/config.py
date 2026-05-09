"""Application configuration loaded from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    # TMDB
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
    TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN", "")
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/"

    # Redis
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "0") == "1"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ML Artifacts
    ARTIFACTS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "artifacts"
    )

    # Rate Limiting
    RATELIMIT_DEFAULT = "60/minute"
    RATELIMIT_SEARCH = "60/minute"
    RATELIMIT_RECOMMEND = "30/minute"

    # Database (SQLite persistent store)
    DATABASE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "movies.db"
    )

    # Per-category staleness (hours) — how long before DB data is re-fetched
    STALE_TRENDING = int(os.getenv("STALE_TRENDING", "6"))
    STALE_POPULAR = int(os.getenv("STALE_POPULAR", "12"))
    STALE_HIGH_RATED = int(os.getenv("STALE_HIGH_RATED", "168"))      # 7 days
    STALE_MOVIE_DETAIL = int(os.getenv("STALE_MOVIE_DETAIL", "168"))  # 7 days
    STALE_GENRES = int(os.getenv("STALE_GENRES", "720"))              # 30 days
    STALE_SEARCH = int(os.getenv("STALE_SEARCH", "12"))

    # Background scheduler — only one instance should run (leader flag)
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "1") == "1"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

