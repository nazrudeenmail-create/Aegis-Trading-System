"""
Model: Account — Trading accounts

References:
    04_Database_Design.md — Section 4.9 accounts
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
from app.database.enums import AccountType


class Account(Base):
    """Trading account — supports paper/demo/live and multi-broker from the start."""

    __tablename__ = "accounts"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint(
            "broker_name", "account_number", name="uq_accounts_broker_account_number"
        ),
        Index("ix_accounts_account_type", "account_type"),
        Index("ix_accounts_is_active", "is_active"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    broker_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_number: Mapped[str] = mapped_column(String(100), nullable=False)

    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, name="account_type", create_type=False), nullable=False
    )

    currency: Mapped[str] = mapped_column(String(10), nullable=False)

    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default="0"
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
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
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="account", lazy="selectin"
    )
    positions: Mapped[list["Position"]] = relationship(
        "Position", back_populates="account", lazy="selectin"
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade", back_populates="account", lazy="selectin"
    )
    backtest_run: Mapped[Optional["BacktestRun"]] = relationship(
        "BacktestRun", back_populates="account", lazy="selectin", uselist=False
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Account(id={self.id}, broker='{self.broker_name}', "
            f"type='{self.account_type}')>"
        )
