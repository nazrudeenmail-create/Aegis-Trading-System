"""
Model: SystemLog — Structured application logging

References:
    04_Database_Design.md — Section 4.14 system_logs
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Identity,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.enums import LogLevel


class SystemLog(Base):
    """Application log entry — for system events, errors, and operational diagnostics."""

    __tablename__ = "system_logs"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        Index("ix_system_logs_level", "level"),
        Index("ix_system_logs_module", "module"),
        Index("ix_system_logs_created_at", "created_at"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel, name="log_level", create_type=False), nullable=False
    )

    module: Mapped[str] = mapped_column(String(100), nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)

    metadata_json: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<SystemLog(id={self.id}, level='{self.level}', "
            f"module='{self.module}')>"
        )
