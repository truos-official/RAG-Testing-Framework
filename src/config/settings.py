"""
Application configuration management with type validation.
Uses Pydantic for runtime validation and environment variable loading.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings are type-validated at startup.
    Missing required settings will raise validation errors.
    """
    
    # ============================================
    # OpenAI Configuration
    # ============================================
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 1000
    openai_timeout: int = 60
    
    # ============================================
    # Azure AI Search Configuration
    # ============================================
    azure_search_endpoint: str
    azure_search_key: str
    azure_search_index_name: str = "knowledge-base"
    
    # ============================================
    # Azure Storage Configuration
    # ============================================
    azure_storage_connection_string: Optional[str] = None
    azure_storage_container: str = "documents"
    
    # ============================================
    # Azure Content Safety (Optional)
    # ============================================
    azure_content_safety_endpoint: Optional[str] = None
    azure_content_safety_key: Optional[str] = None
    
    # ============================================
    # API Configuration
    # ============================================
    api_host: str = "0.0.0.0"
    api_port: int = 5000
    api_debug: bool = False
    api_version: str = "v1"
    
    # ============================================
    # Logging Configuration
    # ============================================
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    
    # ============================================
    # Application Configuration
    # ============================================
    app_name: str = "RAG Testing Framework"
    app_environment: str = "development"  # development, staging, production
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars


# Global settings instance
settings = Settings()