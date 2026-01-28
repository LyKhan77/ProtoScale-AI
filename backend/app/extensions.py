"""Flask extensions initialization."""
import redis
from app.config import get_config


_redis_client = None


def get_redis():
    """Get Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        config = get_config()
        _redis_client = redis.from_url(config.REDIS_URL, decode_responses=True)
    return _redis_client


def init_redis(app):
    """Initialize Redis with Flask app context."""
    global _redis_client
    _redis_client = redis.from_url(app.config["REDIS_URL"], decode_responses=True)
    return _redis_client
