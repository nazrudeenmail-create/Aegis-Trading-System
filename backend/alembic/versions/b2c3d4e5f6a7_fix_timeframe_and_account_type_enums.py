"""Fix timeframe and account_type enums

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-13

Description:
    Adds missing D1 value to the timeframe enum and BACKTEST value to the
    account_type enum so Python and PostgreSQL enums stay in sync.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add D1 to timeframe enum and BACKTEST to account_type enum."""
    # Add D1 to timeframe enum
    op.execute("ALTER TYPE timeframe ADD VALUE IF NOT EXISTS 'D1'")

    # Add BACKTEST to account_type enum
    op.execute("ALTER TYPE account_type ADD VALUE IF NOT EXISTS 'BACKTEST'")


def downgrade() -> None:
    """
    PostgreSQL does not support removing values from an ENUM directly.
    To downgrade we would need to recreate the enum, which is destructive.
    For this stabilization migration we leave the values in place.
    """
    pass
