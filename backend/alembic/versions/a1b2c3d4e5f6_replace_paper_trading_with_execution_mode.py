"""Replace paper_trading_enabled with execution_mode

Revision ID: a1b2c3d4e5f6
Revises: ec1b29a333af
Create Date: 2026-07-13 08:06:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "ec1b29a333af"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create the execution_mode enum type
    execution_mode_enum = sa.Enum("BACKTEST", "DEMO", "LIVE", name="execution_mode")
    execution_mode_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add execution_mode column with default DEMO
    op.add_column(
        "instruments",
        sa.Column(
            "execution_mode",
            sa.Enum(name="execution_mode", create_type=False),
            server_default="DEMO",
            nullable=False,
        ),
    )

    # 3. Drop paper_trading_enabled column
    op.drop_column("instruments", "paper_trading_enabled")

    # 4. Update allow_new_positions default to false (safety)
    op.alter_column(
        "instruments",
        "allow_new_positions",
        server_default="false",
        existing_type=sa.Boolean(),
        existing_nullable=False,
    )


def downgrade() -> None:
    # Restore paper_trading_enabled
    op.add_column(
        "instruments",
        sa.Column(
            "paper_trading_enabled",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
    )

    # Drop execution_mode
    op.drop_column("instruments", "execution_mode")

    # Drop the enum type
    sa.Enum(name="execution_mode").drop(op.get_bind(), checkfirst=True)

    # Restore allow_new_positions default
    op.alter_column(
        "instruments",
        "allow_new_positions",
        server_default="true",
        existing_type=sa.Boolean(),
        existing_nullable=False,
    )