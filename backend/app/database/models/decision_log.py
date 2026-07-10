"""
Model: DecisionLog — Complete audit trail of every trading decision

References:
    04_Database_Design.md — Section 4.15 decision_logs
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
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.enums import DecisionOutcome, DecisionType


class DecisionLog(Base):
    """Audit trail — every trading decision, whether it resulted in a trade or not."""

    __tablename__ = "decision_logs"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        Index("ix_decision_logs_signal_id", "signal_id"),
        Index("ix_decision_logs_instrument_id", "instrument_id"),
        Index("ix_decision_logs_decision_type", "decision_type"),
        Index("ix_decision_logs_created_at", "created_at"),
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

    decision_type: Mapped[DecisionType] = mapped_column(
        Enum(DecisionType, name="decision_type", create_type=False), nullable=False
    )

    decision_context: Mapped[dict] = mapped_column(JSONB, nullable=False)

    reason: Mapped[str] = mapped_column(Text, nullable=False)

    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    engine_version: Mapped[str] = mapped_column(String(20), nullable=False)

    outcome: Mapped[DecisionOutcome] = mapped_column(
        Enum(DecisionOutcome, name="decision_outcome", create_type=False),
        nullable=False,
        server_default="PENDING",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Relationships ----------------------------------------------------------
    signal: Mapped[Optional["Signal"]] = relationship(
        "Signal", back_populates="decision_logs", lazy="selectin"
    )
    instrument: Mapped["Instrument"] = relationship(
        "Instrument", back_populates="decision_logs", lazy="selectin"
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<DecisionLog(id={self.id}, instrument_id={self.instrument_id}, "
            f"type='{self.decision_type}', outcome='{self.outcome}')>"
        )
