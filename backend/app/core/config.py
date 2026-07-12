"""Aegis Trading System - Application Configuration"""
import json
from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Aegis Trading System"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    GLOBAL_TRADING_MODE: str = "BROKER_DEMO"

    DATABASE_URL: str = "postgresql+psycopg://ats_user:ats_password@localhost:5432/ats_development"
    MARKET_DATA_PROVIDER: str = "capital_com"
    CAPITAL_COM_API_URL: str = "https://api-capital.backend-capital.com/api/v1"
    CAPITAL_COM_API_KEY: str = ""
    CAPITAL_COM_USERNAME: str = ""
    CAPITAL_COM_PASSWORD: str = ""
    SECRET_KEY: str = "change-this-in-production"
    ALLOWED_ORIGINS: str = '["http://localhost:5173"]'
    INITIAL_HISTORY_CANDLES: int = 1000

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

    @property
    def allowed_origins(self) -> List[str]:
        try:
            parsed = json.loads(self.ALLOWED_ORIGINS)
            if isinstance(parsed, list): return [str(o) for o in parsed]
        except (json.JSONDecodeError, TypeError): pass
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

@lru_cache
def get_settings() -> Settings:
    return Settings()