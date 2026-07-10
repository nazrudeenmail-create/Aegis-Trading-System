"""
Model: Setting — Key-value system configuration stored in the database

References:
    04_Database_Design.md — Section 4.13 settings
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
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.enums import SettingValueType


class Setting(Base):
    """Key-value configuration — for settings changeable at runtime without restart."""

    __tablename__ = "settings"

    # -- Constraints & Indexes --------------------------------------------------
    __table_args__ = (
        UniqueConstraint("key", name="uq_settings_key"),
        Index("ix_settings_category", "category"),
    )

    # -- Columns ----------------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)

    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    value_type: Mapped[SettingValueType] = mapped_column(
        Enum(SettingValueType, name="setting_value_type", create_type=False),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    category: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # -- Repr -------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"<Setting(id={self.id}, key='{self.key}')>"
