"""
Model: Candle — 1-minute OHLCV market data

References:
    04_Database_Design.md — Section 4.2 candles
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Candle(Base):
    """OHLCV candle — stores 1-minute data; higher timeframes generated in-memory."""

    __tablename__ = "candles"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint(
            "instrument_id", "timestamp", name="uq_candles_instrument_timestamp"
        ),
        Index("ix_candles_instrument_id", "instrument_id"),
        Index("ix_candles_instrument_timestamp", "instrument_id", "timestamp"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    instrument_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    open: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)

    volume: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default="0"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Relationships ----------------------------------------------------------
    instrument: Mapped["Instrument"] = relationship(
        "Instrument", back_populates="candles", lazy="selectin"
    )
    indicator_values: Mapped[list["IndicatorValue"]] = relationship(
        "IndicatorValue", back_populates="candle", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Candle(id={self.id}, instrument_id={self.instrument_id}, "
            f"timestamp={self.timestamp})>"
        )
