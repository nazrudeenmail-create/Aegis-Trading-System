"""
Model: RiskCheck — Pre-trade risk validation records

References:
    04_Database_Design.md — Section 4.8 risk_checks
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.enums import RiskCheckType


class RiskCheck(Base):
    """Pre-trade risk validation — one signal can have multiple risk checks."""

    __tablename__ = "risk_checks"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        Index("ix_risk_checks_signal_id", "signal_id"),
        Index("ix_risk_checks_check_type", "check_type"),
        Index("ix_risk_checks_passed", "passed"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    signal_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("signals.id", ondelete="RESTRICT"), nullable=False
    )

    check_type: Mapped[RiskCheckType] = mapped_column(
        Enum(RiskCheckType, name="risk_check_type", create_type=False), nullable=False
    )

    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)

    check_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8), nullable=True)
    threshold_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 8), nullable=True
    )

    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Relationships ----------------------------------------------------------
    signal: Mapped["Signal"] = relationship(
        "Signal", back_populates="risk_checks", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<RiskCheck(id={self.id}, signal_id={self.signal_id}, "
            f"check='{self.check_type}', passed={self.passed})>"
        )
