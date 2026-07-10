"""
Model: MarketSession — Regular trading hours per exchange per day of week

References:
    04_Database_Design.md — Section 4.3 market_sessions
"""
from datetime import datetime, time

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Identity,
    Index,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MarketSession(Base):
    """Defines regular trading hours per exchange per day of week (0=Sunday … 6=Saturday)."""

    __tablename__ = "market_sessions"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint(
            "exchange", "day_of_week", name="uq_market_sessions_exchange_day"
        ),
        Index("ix_market_sessions_exchange", "exchange"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    exchange: Mapped[str] = mapped_column(String(50), nullable=False)

    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)

    timezone: Mapped[str] = mapped_column(String(50), nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<MarketSession(id={self.id}, exchange='{self.exchange}', "
            f"day={self.day_of_week})>"
        )
