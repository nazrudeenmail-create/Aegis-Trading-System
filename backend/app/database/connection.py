"""
Aegis Trading System — Database Connection

Responsibility:
    - Create the SQLAlchemy engine using the configured DATABASE_URL.
    - Provide a session factory (SessionLocal) for creating database sessions.
    - Provide the get_db() dependency for FastAPI route injection.

Architecture rule:
    No module accesses the database directly.
    All database access goes through:

        Component → Repository → SessionLocal → PostgreSQL

Usage in FastAPI routes (Phase 9):
    from app.database.connection import get_db
    from sqlalchemy.orm import Session

    @router.get("/trades")
    def get_trades(db: Session = Depends(get_db)):
        ...

Driver:
    psycopg3 (psycopg[binary]>=3.2)
    URL prefix: postgresql+psycopg://
"""

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# SQLAlchemy engine
# pool_pre_ping=True — verifies connections before use (handles dropped connections)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,  # Logs all SQL statements in DEBUG mode
)

# Session factory — each request gets its own session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    FastAPI dependency that provides a database session per request.

    The session is opened at the start of the request and
    automatically closed when the request finishes — even if an error occurs.

    Usage:
        from fastapi import Depends
        from app.database.connection import get_db

        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...

    Yields:
        Session: Active SQLAlchemy database session.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_database_connection() -> bool:
    """
    Test that the database is reachable.

    Used during startup to confirm the connection is working.

    Returns:
        bool: True if connection is healthy, False otherwise.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully.")
        return True
    except Exception as exc:
        logger.error("Database connection failed: %s", exc)
        return False
