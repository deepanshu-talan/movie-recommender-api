"""Redis client connection pool."""
import redis
from app.core.config import Config
from app.core.logging_config import get_logger

logger = get_logger("redis")

_redis_client = None
_redis_disabled = False


def get_redis() -> redis.Redis | None:
    """Get or create a Redis connection. Returns None if unavailable."""
    global _redis_client, _redis_disabled
    if not Config.CACHE_ENABLED or _redis_disabled or not Config.REDIS_URL:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        _redis_client = redis.from_url(
            Config.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.25,
            socket_timeout=0.25,
        )
        _redis_client.ping()
        logger.info("redis_connected", url=Config.REDIS_URL)
        return _redis_client
    except (redis.ConnectionError, redis.TimeoutError) as e:
        logger.warning("redis_unavailable", error=str(e))
        _redis_client = None
        _redis_disabled = True
        return None
