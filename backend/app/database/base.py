"""
Aegis Trading System — SQLAlchemy Declarative Base

Responsibility:
    - Provide the single DeclarativeBase that all models inherit from.
    - Allow Alembic to auto-discover all models for migration generation.

Usage:
    All database models must import and inherit from Base:

        from app.database.base import Base

        class Candle(Base):
            __tablename__ = "candles"
            ...

Alembic:
    alembic/env.py imports Base.metadata to detect all registered models.
    This means every model file must be imported before Alembic runs.
    See alembic/env.py for the import pattern.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all ATS database models.

    All SQLAlchemy models inherit from this class.
    Alembic uses Base.metadata to auto-generate migration scripts.
    """
    pass
