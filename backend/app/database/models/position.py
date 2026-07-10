"""
Model: Position — Open and closed position tracking

References:
    04_Database_Design.md — Section 4.11 positions
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
from app.database.enums import Direction, PositionStatus


class Position(Base):
    """Position tracking — aggregate of one or more trades over its lifecycle."""

    __tablename__ = "positions"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        Index("ix_positions_account_id", "account_id"),
        Index("ix_positions_instrument_id", "instrument_id"),
        Index("ix_positions_status", "status"),
        Index("ix_positions_opened_at", "opened_at"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    instrument_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )

    direction: Mapped[Direction] = mapped_column(
        Enum(Direction, name="direction", create_type=False), nullable=False
    )

    status: Mapped[PositionStatus] = mapped_column(
        Enum(PositionStatus, name="position_status", create_type=False),
        nullable=False,
        server_default="OPEN",
    )

    entry_price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    remaining_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)

    stop_loss: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8), nullable=True)
    take_profit: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8), nullable=True)

    unrealized_pnl: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    realized_pnl: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )

    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
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
    instrument: Mapped["Instrument"] = relationship(
        "Instrument", back_populates="positions", lazy="selectin"
    )
    account: Mapped["Account"] = relationship(
        "Account", back_populates="positions", lazy="selectin"
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade", back_populates="position", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Position(id={self.id}, instrument_id={self.instrument_id}, "
            f"direction='{self.direction}', status='{self.status}')>"
        )
