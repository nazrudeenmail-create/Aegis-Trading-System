"""
Model: Trade — Completed execution records (fills)

References:
    04_Database_Design.md — Section 4.12 trades
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
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.enums import Direction, TradeType


class Trade(Base):
    """Execution record — each trade represents a fill within a position."""

    __tablename__ = "trades"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        Index("ix_trades_account_id", "account_id"),
        Index("ix_trades_position_id", "position_id"),
        Index("ix_trades_order_id", "order_id"),
        Index("ix_trades_instrument_id", "instrument_id"),
        Index("ix_trades_executed_at", "executed_at"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    position_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("positions.id", ondelete="RESTRICT"), nullable=False
    )
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False
    )
    instrument_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )

    direction: Mapped[Direction] = mapped_column(
        Enum(Direction, name="direction", create_type=False), nullable=False
    )
    trade_type: Mapped[TradeType] = mapped_column(
        Enum(TradeType, name="trade_type", create_type=False), nullable=False
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)

    pnl: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    commission: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True, server_default="0"
    )
    slippage: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8), nullable=True)

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Relationships ----------------------------------------------------------
    position: Mapped["Position"] = relationship(
        "Position", back_populates="trades", lazy="selectin"
    )
    order: Mapped["Order"] = relationship(
        "Order", back_populates="trades", lazy="selectin"
    )
    instrument: Mapped["Instrument"] = relationship(
        "Instrument", lazy="selectin"
    )
    account: Mapped["Account"] = relationship(
        "Account", back_populates="trades", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Trade(id={self.id}, position_id={self.position_id}, "
            f"type='{self.trade_type}', price={self.price})>"
        )
