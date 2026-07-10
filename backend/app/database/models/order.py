"""
Model: Order — Trade orders submitted to the broker

References:
    04_Database_Design.md — Section 4.10 orders
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
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.enums import Direction, OrderStatus, OrderType


class Order(Base):
    """Order lifecycle — submitted to the broker after a signal passes risk checks."""

    __tablename__ = "orders"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint("client_order_id", name="uq_orders_client_order_id"),
        Index("ix_orders_account_id", "account_id"),
        Index("ix_orders_signal_id", "signal_id"),
        Index("ix_orders_instrument_id", "instrument_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_broker_order_id", "broker_order_id"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    signal_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("signals.id", ondelete="RESTRICT"),
        nullable=True,
    )
    instrument_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )

    client_order_id: Mapped[str] = mapped_column(String(50), nullable=False)
    broker_order_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    direction: Mapped[Direction] = mapped_column(
        Enum(Direction, name="direction", create_type=False), nullable=False
    )
    order_type: Mapped[OrderType] = mapped_column(
        Enum(OrderType, name="order_type", create_type=False), nullable=False
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8), nullable=True)
    stop_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8), nullable=True)

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status", create_type=False),
        nullable=False,
        server_default="PENDING",
    )

    filled_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8), nullable=True)
    filled_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 8), nullable=True
    )

    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    filled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    broker_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    signal: Mapped[Optional["Signal"]] = relationship(
        "Signal", back_populates="orders", lazy="selectin"
    )
    instrument: Mapped["Instrument"] = relationship(
        "Instrument", lazy="selectin"
    )
    account: Mapped["Account"] = relationship(
        "Account", back_populates="orders", lazy="selectin"
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade", back_populates="order", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, client_id='{self.client_order_id}', "
            f"status='{self.status}')>"
        )
