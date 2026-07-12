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

import json
from functools import lru_cache
from typing import List

from pydantic import field_validator
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
    GLOBAL_TRADING_MODE: str = "SIMULATION"

    # Database
    # URL format for psycopg3 (psycopg[binary]>=3.2):
    #   postgresql+psycopg://user:password@host:port/dbname
    DATABASE_URL: str = (
        "postgresql+psycopg://ats_user:ats_password@localhost:5432/ats_development"
    )

    # Market Data Provider
    MARKET_DATA_PROVIDER: str = "capital_com"
    
    # Capital.com Config
    CAPITAL_COM_API_URL: str = "https://api-capital.backend-capital.com/api/v1"
    CAPITAL_COM_API_KEY: str = ""
    CAPITAL_COM_USERNAME: str = ""
    CAPITAL_COM_PASSWORD: str = ""

    # Security
    SECRET_KEY: str = "change-this-in-production"

    # CORS — stored as a string (JSON or comma-separated), accessed as list
    # via the `allowed_origins` property.
    # Accepts:
    #   JSON array:  ["http://localhost:5173", "http://localhost:3000"]
    #   CSV:         http://localhost:5173,http://localhost:3000
    #   Empty:       falls back to dev default
    ALLOWED_ORIGINS: str = '["http://localhost:5173"]'

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def normalize_allowed_origins(cls, v):
        """
        Normalize any input format to a JSON string for storage.

        Accepts:
            - Python list (from code) → JSON string
            - JSON array string → validated JSON string
            - Comma-separated string → converted to JSON string
            - Empty string/None → dev default

        This prevents pydantic-settings from trying (and failing) to
        JSON-decode complex types, and gives clear behavior for all
        common .env formats.
        """
        if v is None:
            return '["http://localhost:5173"]'

        if isinstance(v, list):
            return json.dumps(v)

        if isinstance(v, str):
            v = v.strip()
            if not v:
                return '["http://localhost:5173"]'

            # Try JSON parse first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return json.dumps([str(o) for o in parsed])
            except (json.JSONDecodeError, TypeError):
                pass

            # Fall back to comma-separated
            origins = [o.strip() for o in v.split(",") if o.strip()]
            return json.dumps(origins) if origins else '["http://localhost:5173"]'

        return v

    @property
    def allowed_origins(self) -> List[str]:
        """
        Return ALLOWED_ORIGINS as a parsed list of strings.

        This is what middleware and application code should use.
        """
        try:
            parsed = json.loads(self.ALLOWED_ORIGINS)
            if isinstance(parsed, list):
                return [str(o) for o in parsed]
        except (json.JSONDecodeError, TypeError):
            pass
        # Last-resort fallback: split by comma
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

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