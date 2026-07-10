"""
Model: IndicatorValue — Computed indicator values per candle per timeframe

References:
    04_Database_Design.md — Section 4.5 indicator_values
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.enums import IndicatorType, Timeframe


class IndicatorValue(Base):
    """Computed indicator values — one row per indicator per candle per timeframe."""

    __tablename__ = "indicator_values"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "candle_id",
            "indicator_type",
            "timeframe",
            name="uq_indicator_values_instrument_candle_type_tf",
        ),
        Index("ix_indicator_values_instrument_id", "instrument_id"),
        Index("ix_indicator_values_candle_id", "candle_id"),
        Index("ix_indicator_values_indicator_type", "indicator_type"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    instrument_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )
    candle_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("candles.id", ondelete="RESTRICT"), nullable=False
    )

    indicator_type: Mapped[IndicatorType] = mapped_column(
        Enum(IndicatorType, name="indicator_type", create_type=False), nullable=False
    )
    timeframe: Mapped[Timeframe] = mapped_column(
        Enum(Timeframe, name="timeframe", create_type=False), nullable=False
    )

    value: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)

    metadata_json: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Relationships ----------------------------------------------------------
    instrument: Mapped["Instrument"] = relationship(
        "Instrument", back_populates="indicator_values", lazy="selectin"
    )
    candle: Mapped["Candle"] = relationship(
        "Candle", back_populates="indicator_values", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<IndicatorValue(id={self.id}, type='{self.indicator_type}', "
            f"tf='{self.timeframe}')>"
        )
