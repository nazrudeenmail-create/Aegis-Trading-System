"""
Model: MarketHoliday — Holiday calendar per exchange

References:
    04_Database_Design.md — Section 4.4 market_holidays
"""
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Identity,
    Index,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MarketHoliday(Base):
    """Holiday calendar per exchange. Overrides market_sessions on specific dates."""

    __tablename__ = "market_holidays"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint(
            "exchange", "holiday_date", name="uq_market_holidays_exchange_date"
        ),
        Index("ix_market_holidays_exchange", "exchange"),
        Index("ix_market_holidays_holiday_date", "holiday_date"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    exchange: Mapped[str] = mapped_column(String(50), nullable=False)

    holiday_date: Mapped[date] = mapped_column(Date, nullable=False)

    name: Mapped[str] = mapped_column(String(200), nullable=False)

    is_full_day: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )

    early_close_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<MarketHoliday(id={self.id}, exchange='{self.exchange}', "
            f"date={self.holiday_date})>"
        )
