"""
Enterprise RAG Testing Framework - Main Application

Production-ready Flask application with:
- Service layer architecture
- Structured logging
- Configuration management
- Azure AI Search integration
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from flask import Flask
from src.config.settings import settings
from src.utils.logging import setup_logging, get_logger
from src.api.routes import register_routes

# Setup logging
setup_logging()
logger = get_logger(__name__)


def create_app():
    """Application factory pattern."""
    
    app = Flask(__name__)
    
    # Register routes
    register_routes(app)
    
    logger.info("Application initialized", extra={
        "app_name": settings.app_name,
        "environment": settings.app_environment,
        "log_level": settings.log_level
    })
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    logger.info("Starting Flask application", extra={
        "host": settings.api_host,
        "port": settings.api_port,
        "debug": settings.api_debug
    })
    
    app.run(
        host=settings.api_host,
        port=settings.api_port,
        debug=settings.api_debug
    )