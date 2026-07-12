"""
ATS Configuration Validator
Ensures the system is properly configured before starting Stage 0 of Validation.
"""
import logging
import sys
from app.core.config import get_settings
from app.core.state import global_state

logger = logging.getLogger(__name__)

def validate_configuration():
    """
    Fails fast if critical configuration is missing.
    Used during Phase 13.5 Stage 0.
    """
    settings = get_settings()
    errors = []

    logger.info("Validating system configuration (Stage 0)...")

    # 1. Trading Mode
    if global_state.global_trading_mode != "BROKER_DEMO":
        errors.append(f"Global trading mode is '{global_state.global_trading_mode}', expected 'BROKER_DEMO' for Phase 13.5 validation.")

    # 2. Capital.com Credentials
    if settings.MARKET_DATA_PROVIDER == "capital_com":
        if not settings.CAPITAL_COM_API_KEY:
            errors.append("CAPITAL_COM_API_KEY is empty in .env")
        if not settings.CAPITAL_COM_USERNAME:
            errors.append("CAPITAL_COM_USERNAME is empty in .env")
        if not settings.CAPITAL_COM_PASSWORD:
            errors.append("CAPITAL_COM_PASSWORD is empty in .env")

    # 3. Database
    if not settings.DATABASE_URL or "postgresql" not in settings.DATABASE_URL:
        errors.append("DATABASE_URL must be a valid PostgreSQL connection string.")

    if errors:
        logger.critical("CONFIGURATION VALIDATION FAILED:")
        for err in errors:
            logger.critical(f" - {err}")
        logger.critical("Please fix your .env configuration and restart ATS.")
        sys.exit(1)
        
    logger.info("Configuration Validation PASSED.")
