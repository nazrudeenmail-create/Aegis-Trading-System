"""
Aegis Trading System — Logging Configuration

Responsibility:
    - Configure Python's standard logging system for the entire application.
    - Provide consistent log formatting across all modules.
    - Control log level based on the DEBUG setting.

Usage:
    Call setup_logging() once at application startup (in main.py).
    All modules get their own logger via:

        import logging
        logger = logging.getLogger(__name__)

    Log level:
        - DEBUG=True  → logs DEBUG and above
        - DEBUG=False → logs INFO and above

Log format:
    2026-07-10 00:00:00,000 | INFO     | app.main | ATS backend starting
"""

import logging
import sys

from app.core.config import get_settings


def setup_logging() -> None:
    """
    Configure application-wide logging.

    Called once during application startup before any other initialization.
    Sets up a single console handler with consistent formatting.
    """
    settings = get_settings()

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,  # Override any existing handlers (e.g. from uvicorn)
    )

    # Reduce noise from third-party libraries in production
    if not settings.DEBUG:
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.getLogger(__name__).debug(
        "Logging initialized | level=%s",
        logging.getLevelName(log_level),
    )
