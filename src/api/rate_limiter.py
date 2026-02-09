"""
Rate limiting configuration.

Protects API from abuse and controls costs.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


def get_limiter(app):
    """
    Initialize rate limiter with Flask app.
    
    Limits:
    - Default: 100 requests per hour
    - Query endpoint: 20 requests per minute (expensive)
    - Search endpoint: 60 requests per minute
    - Health check: unlimited
    
    Uses client IP address for tracking.
    """
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per hour"],
        storage_uri="memory://",  # In production, use Redis
        strategy="fixed-window"
    )
    
    logger.info("Rate limiter initialized", extra={
        "default_limit": "100/hour",
        "strategy": "fixed-window"
    })
    
    return limiter