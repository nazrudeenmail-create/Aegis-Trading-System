"""
Model: BacktestRun — Metadata and summary statistics for a backtest execution.

References:
    Phase 7 — Backtesting & Strategy Intelligence
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class BacktestRun(Base):
    """Metadata and performance summary for a specific backtest execution.
    
    This is tightly coupled (1-to-1) with an Account of type BACKTEST.
    """

    __tablename__ = "backtest_runs"

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    account_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("accounts.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Strategy Info
    strategy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    strategy_version: Mapped[str] = mapped_column(String(20), nullable=False)

    # Configuration Metadata
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    # Performance Statistics (Populated upon completion)
    total_trades: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    win_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    profit_factor: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    expectancy: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    max_drawdown: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    final_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)

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
    account: Mapped["Account"] = relationship(
        "Account", back_populates="backtest_run", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<BacktestRun(id={self.id}, account_id={self.account_id}, "
            f"strategy='{self.strategy_name} {self.strategy_version}')>"
        )
