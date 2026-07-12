"""
Model: InstrumentGroup — Categorization for instruments (e.g., AI Stocks, Commodities)
"""
from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Identity, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

# Many-to-Many association table for Instrument <-> InstrumentGroup
instrument_group_association = Table(
    "instrument_group_association",
    Base.metadata,
    Column("instrument_id", BigInteger, ForeignKey("instruments.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", BigInteger, ForeignKey("instrument_groups.id", ondelete="CASCADE"), primary_key=True),
)

class InstrumentGroup(Base):
    """A logical grouping of instruments for bulk management and analysis."""

    __tablename__ = "instrument_groups"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    instruments: Mapped[list["Instrument"]] = relationship(
        "Instrument", secondary=instrument_group_association, back_populates="groups", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<InstrumentGroup(id={self.id}, name='{self.name}')>"
