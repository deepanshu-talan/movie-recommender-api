"""Cache service — Redis abstraction with TTL-aware get/set."""
import json
from app.db.redis_client import get_redis
from app.core.logging_config import get_logger

logger = get_logger("cache_service")

# TTL constants (seconds)
TTL_SEARCH = 900        # 15 minutes
TTL_MOVIE = 86400       # 24 hours
TTL_TRENDING = 3600     # 1 hour
TTL_POPULAR = 21600     # 6 hours
TTL_GENRES = 604800     # 7 days
TTL_RECOMMEND = 3600    # 1 hour


def cache_get(key: str) -> dict | list | None:
    """Get a cached value by key. Returns None on miss or error."""
    r = get_redis()
    if not r:
        return None
    try:
        data = r.get(key)
        if data:
            logger.debug("cache_hit", key=key)
            return json.loads(data)
        return None
    except Exception as e:
        logger.warning("cache_get_error", key=key, error=str(e))
        return None


def cache_set(key: str, value, ttl: int = TTL_MOVIE) -> None:
    """Set a cached value with TTL."""
    r = get_redis()
    if not r:
        return
    try:
        r.setex(key, ttl, json.dumps(value))
        logger.debug("cache_set", key=key, ttl=ttl)
    except Exception as e:
        logger.warning("cache_set_error", key=key, error=str(e))


def cache_key(prefix: str, *parts) -> str:
    """Build a cache key from prefix and parts."""
    safe_parts = [str(p).lower().strip().replace(" ", "_") for p in parts]
    return f"{prefix}:{':'.join(safe_parts)}"
