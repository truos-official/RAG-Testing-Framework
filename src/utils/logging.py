"""
Structured logging configuration for the application.

Provides JSON-formatted logs with request context for production,
and human-readable logs for development.
"""

import logging
import sys
from pythonjsonlogger import jsonlogger
from src.config.settings import settings


def setup_logging():
    """
    Configure application logging.
    
    - Development: Human-readable format
    - Production: JSON format for log aggregation
    
    Returns:
        logging.Logger: Configured root logger
    """
    
    # Get root logger
    logger = logging.getLogger()
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set log level from config
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Choose formatter based on environment
    if settings.log_format == "json":
        # JSON formatter for production
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            rename_fields={
                'levelname': 'level',
                'asctime': 'timestamp'
            }
        )
    else:
        # Human-readable formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('azure').setLevel(logging.WARNING)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Module name (usually __name__)
    
    Returns:
        logging.Logger: Module-specific logger
    
    Example:
        logger = get_logger(__name__)
        logger.info("Processing request", extra={"user_id": 123})
    """
    return logging.getLogger(name)