"""
Minimal configuration module for AI Receptionist Voice Pipeline.

Loads configuration from environment variables for:
- FastAPI application
- Twilio telephony
- Gemini AI
"""

from typing import Optional
import logging

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseSettings
    SettingsConfigDict = None

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    
    Minimal configuration for voice pipeline only.
    """
    
    # Application Environment
    app_env: str = "production"
    debug: bool = False
    
    # Twilio Configuration
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    
    # Gemini Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Logging
    log_level: str = "INFO"
    
    if SettingsConfigDict:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            env_prefix="",
            case_sensitive=False,
            extra="ignore"
        )
    else:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False
            extra = "ignore"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() in ["local", "development", "dev"]


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance.
    
    Returns:
        Settings instance loaded from environment
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        logger.info(f"Settings loaded for environment: {_settings.app_env}")
    return _settings


def reset_settings() -> None:
    """Reset settings instance (mainly for testing)."""
    global _settings
    _settings = None
