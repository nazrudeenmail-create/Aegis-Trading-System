"""
Model: Instrument — Tradable instruments (the root entity)

References:
    04_Database_Design.md — Section 4.1 instruments
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Identity,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.enums import AssetClass


class Instrument(Base):
    """Tradable instrument — root entity referenced by nearly every other table."""

    __tablename__ = "instruments"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint("symbol", name="uq_instruments_symbol"),
        Index("ix_instruments_asset_class", "asset_class"),
        Index("ix_instruments_exchange", "exchange"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    asset_class: Mapped[AssetClass] = mapped_column(
        Enum(AssetClass, name="asset_class", create_type=False), nullable=False
    )

    exchange: Mapped[str] = mapped_column(String(50), nullable=False)

    tick_size: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    contract_size: Mapped[Decimal] = mapped_column(
        Numeric(18, 8), nullable=False, server_default="1.0"
    )

    currency: Mapped[str] = mapped_column(String(10), nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # -- Relationships ----------------------------------------------------------
    candles: Mapped[list["Candle"]] = relationship(
        "Candle", back_populates="instrument", lazy="selectin"
    )
    indicator_values: Mapped[list["IndicatorValue"]] = relationship(
        "IndicatorValue", back_populates="instrument", lazy="selectin"
    )
    market_analyses: Mapped[list["MarketAnalysis"]] = relationship(
        "MarketAnalysis", back_populates="instrument", lazy="selectin"
    )
    signals: Mapped[list["Signal"]] = relationship(
        "Signal", back_populates="instrument", lazy="selectin"
    )
    positions: Mapped[list["Position"]] = relationship(
        "Position", back_populates="instrument", lazy="selectin"
    )
    decision_logs: Mapped[list["DecisionLog"]] = relationship(
        "DecisionLog", back_populates="instrument", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"<Instrument(id={self.id}, symbol='{self.symbol}')>"
