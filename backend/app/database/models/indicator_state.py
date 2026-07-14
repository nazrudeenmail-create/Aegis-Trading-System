"""
Model: IndicatorState — Caches the latest value of an indicator to prevent full history scans.

References:
    Phase 4.5 - Indicator State Cache
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class IndicatorState(Base):
    """Stores the absolute latest calculated state for an indicator (e.g. Daily EMA200)."""

    __tablename__ = "indicator_state"

    __table_args__ = (
        UniqueConstraint(
            "instrument_id", "timeframe", "indicator_name",
            name="uq_indicator_state_instrument_tf_name"
        ),
        Index("ix_indicator_state_instrument_id", "instrument_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    instrument_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False
    )
    
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    indicator_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    value: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    candle_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(20), server_default="1.0", nullable=False)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    instrument: Mapped["Instrument"] = relationship(
        "Instrument", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<IndicatorState(instrument_id={self.instrument_id}, "
            f"tf='{self.timeframe}', ind='{self.indicator_name}', val={self.value})>"
        )
