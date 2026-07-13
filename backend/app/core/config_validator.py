"""
ATS Configuration Validator
Ensures the system is properly configured before starting.
"""
import logging
import sys
from app.core.config import get_settings, BrokerType, AccountMode

logger = logging.getLogger(__name__)

def validate_configuration():
    """
    Fails fast if critical configuration is missing.
    Called during application startup.
    """
    settings = get_settings()
    errors = []

    logger.info("Validating system configuration...")

    # 1. Broker Type
    valid_brokers = [b.value for b in BrokerType]
    if settings.BROKER not in valid_brokers:
        errors.append(f"BROKER must be one of {valid_brokers}, got '{settings.BROKER}'")

    # 2. Account Mode
    valid_modes = [m.value for m in AccountMode]
    if settings.ACCOUNT_MODE not in valid_modes:
        errors.append(f"ACCOUNT_MODE must be one of {valid_modes}, got '{settings.ACCOUNT_MODE}'")

    # 3. Capital.com Credentials (required for both demo and live)
    if settings.BROKER == BrokerType.CAPITAL.value:
        if not settings.CAPITAL_COM_API_KEY:
            errors.append("CAPITAL_COM_API_KEY is empty in .env")
        if not settings.CAPITAL_COM_USERNAME:
            errors.append("CAPITAL_COM_USERNAME is empty in .env")
        if not settings.CAPITAL_COM_PASSWORD:
            errors.append("CAPITAL_COM_PASSWORD is empty in .env")

    # 4. Capital.com URLs
    if not settings.CAPITAL_COM_DEMO_URL:
        errors.append("CAPITAL_COM_DEMO_URL is empty in .env")
    if not settings.CAPITAL_COM_LIVE_URL:
        errors.append("CAPITAL_COM_LIVE_URL is empty in .env")

    # 5. Database
    if not settings.DATABASE_URL or "postgresql" not in settings.DATABASE_URL:
        errors.append("DATABASE_URL must be a valid PostgreSQL connection string.")

    # 6. Safety warning: Live mode with debug enabled
    if settings.is_live and settings.DEBUG:
        logger.warning(
            "⚠  WARNING: ACCOUNT_MODE=live with DEBUG=True. "
            "Consider setting DEBUG=False in production."
        )

    if errors:
        logger.critical("CONFIGURATION VALIDATION FAILED:")
        for err in errors:
            logger.critical(f" - {err}")
        logger.critical("Please fix your .env configuration and restart ATS.")
        sys.exit(1)
        
    logger.info("Configuration Validation PASSED.")