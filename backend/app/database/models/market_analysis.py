"""
Model: MarketAnalysis — Multi-timeframe analysis snapshots

References:
    04_Database_Design.md — Section 4.6 market_analysis
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
from app.database.enums import MarketBias, Timeframe, TrendHealth


class MarketAnalysis(Base):
    """Multi-timeframe analysis snapshot — one row per instrument per timeframe per analysis."""

    __tablename__ = "market_analysis"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "timeframe",
            "analysis_timestamp",
            name="uq_market_analysis_instrument_tf_timestamp",
        ),
        Index("ix_market_analysis_instrument_id", "instrument_id"),
        Index(
            "ix_market_analysis_instrument_tf_timestamp",
            "instrument_id",
            "timeframe",
            "analysis_timestamp",
        ),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    instrument_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )

    timeframe: Mapped[Timeframe] = mapped_column(
        Enum(Timeframe, name="timeframe", create_type=False), nullable=False
    )

    analysis_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    bias: Mapped[MarketBias] = mapped_column(
        Enum(MarketBias, name="market_bias", create_type=False), nullable=False
    )
    trend_health: Mapped[TrendHealth] = mapped_column(
        Enum(TrendHealth, name="trend_health", create_type=False), nullable=False
    )

    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    metadata_json: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Relationships ----------------------------------------------------------
    instrument: Mapped["Instrument"] = relationship(
        "Instrument", back_populates="market_analyses", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<MarketAnalysis(id={self.id}, instrument_id={self.instrument_id}, "
            f"bias='{self.bias}')>"
        )
