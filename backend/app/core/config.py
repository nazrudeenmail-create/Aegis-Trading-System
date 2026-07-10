"""
Aegis Trading System — Application Configuration

Responsibility:
    - Load all environment variables from the .env file.
    - Validate required settings at application startup.
    - Provide a single source of configuration for the entire application.

Rules:
    - No hardcoded values. All configuration comes from environment variables.
    - Secrets (.env) are never committed to Git.
    - Use get_settings() everywhere — it is cached after the first call.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All fields have defaults for local development.
    Production overrides these via environment variables or Docker secrets.
    """

    # Application identity
    APP_NAME: str = "Aegis Trading System"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"  # development | testing | production
    DEBUG: bool = True

    # Database
    # URL format for psycopg3 (psycopg[binary]>=3.2):
    #   postgresql+psycopg://user:password@host:port/dbname
    DATABASE_URL: str = (
        "postgresql+psycopg://ats_user:ats_password@localhost:5432/ats_development"
    )

    # Security
    SECRET_KEY: str = "change-this-in-production"

    # CORS — list of allowed frontend origins
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.

    The @lru_cache decorator ensures Settings() is only instantiated once.
    This prevents re-reading the .env file on every request.

    Usage:
        from app.core.config import get_settings
        settings = get_settings()

    Returns:
        Settings: Validated application configuration.
    """
    return Settings()
