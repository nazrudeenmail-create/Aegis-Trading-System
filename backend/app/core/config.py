"""Aegis Trading System - Application Configuration"""
import enum
import json
from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BrokerType(str, enum.Enum):
    """Supported broker types."""
    CAPITAL = "capital"


class AccountMode(str, enum.Enum):
    """Account trading mode."""
    DEMO = "demo"
    LIVE = "live"


class Settings(BaseSettings):
    APP_NAME: str = "Aegis Trading System"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Database ──
    DATABASE_URL: str = "postgresql+psycopg://ats_user:ats_password@localhost:5432/ats_development"

    # ── Security ──
    SECRET_KEY: str = "change-this-in-production"

    # ── CORS ──
    ALLOWED_ORIGINS: str = '["http://localhost:5173"]'

    # ── Broker & Account Mode (single source of truth) ──
    BROKER: str = "capital"
    ACCOUNT_MODE: str = "demo"

    # ── Capital.com URLs ──
    CAPITAL_COM_DEMO_URL: str = "https://demo-api-capital.backend-capital.com/api/v1"
    CAPITAL_COM_LIVE_URL: str = "https://api-capital.backend-capital.com/api/v1"

    # ── Capital.com Credentials ──
    CAPITAL_COM_API_KEY: str = ""
    CAPITAL_COM_USERNAME: str = ""
    CAPITAL_COM_PASSWORD: str = ""

    # ── Market Data Settings ──
    INITIAL_HISTORY_CANDLES: int = 1000

    # ── System-Level Safety Switch ──
    SYSTEM_LIVE_TRADING_ENABLED: bool = False

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def normalize_allowed_origins(cls, v):
        if v is None: return '["http://localhost:5173"]'
        if isinstance(v, list): return json.dumps(v)
        if isinstance(v, str):
            v = v.strip()
            if not v: return '["http://localhost:5173"]'
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list): return json.dumps([str(o) for o in parsed])
            except (json.JSONDecodeError, TypeError): pass
            origins = [o.strip() for o in v.split(",") if o.strip()]
            return json.dumps(origins) if origins else '["http://localhost:5173"]'
        return v

    @field_validator("BROKER", mode="before")
    @classmethod
    def normalize_broker(cls, v):
        if v is None: return "capital"
        return str(v).lower().strip()

    @field_validator("ACCOUNT_MODE", mode="before")
    @classmethod
    def normalize_account_mode(cls, v):
        if v is None: return "demo"
        return str(v).lower().strip()

    @property
    def allowed_origins(self) -> List[str]:
        try:
            parsed = json.loads(self.ALLOWED_ORIGINS)
            if isinstance(parsed, list): return [str(o) for o in parsed]
        except (json.JSONDecodeError, TypeError): pass
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def is_demo(self) -> bool:
        """True if ACCOUNT_MODE is 'demo'."""
        return self.ACCOUNT_MODE == AccountMode.DEMO.value

    @property
    def is_live(self) -> bool:
        """True if ACCOUNT_MODE is 'live'."""
        return self.ACCOUNT_MODE == AccountMode.LIVE.value

    @property
    def capital_api_url(self) -> str:
        """Returns the correct Capital.com API URL based on ACCOUNT_MODE.
        
        This is the single source of truth for which endpoint to use.
        No other file should know about demo vs live URLs.
        """
        if self.is_live:
            return self.CAPITAL_COM_LIVE_URL
        return self.CAPITAL_COM_DEMO_URL

    @property
    def broker_display_name(self) -> str:
        """Human-readable broker name for startup banner and API responses."""
        if self.BROKER == BrokerType.CAPITAL.value:
            return "Capital.com"
        return self.BROKER.title()

    @property
    def account_mode_display(self) -> str:
        """Human-readable account mode for startup banner and API responses."""
        return self.ACCOUNT_MODE.title()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()