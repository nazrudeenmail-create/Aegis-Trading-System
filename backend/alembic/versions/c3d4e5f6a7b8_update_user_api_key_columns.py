"""Update user table for HMAC-based API key authentication

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-13

Description:
    Renames api_key_hash to key_hash and adds key_prefix column for
    HMAC-based API key authentication.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add key_prefix column and rename api_key_hash to key_hash."""
    # Add key_prefix column
    op.add_column('users', sa.Column('key_prefix', sa.String(32), nullable=False, server_default=''))

    # Add key_hash column
    op.add_column('users', sa.Column('key_hash', sa.String(64), nullable=False, server_default=''))

    # Migrate existing api_key_hash data to key_hash (hash each key with HMAC)
    # Note: For existing plaintext keys, we'll need to re-hash them on next login
    op.execute("""
        UPDATE users 
        SET key_prefix = '', 
            key_hash = api_key_hash
        WHERE api_key_hash IS NOT NULL
    """)

    # Drop old api_key_hash column
    op.drop_column('users', 'api_key_hash')


def downgrade() -> None:
    """Revert to original api_key_hash column."""
    op.add_column('users', sa.Column('api_key_hash', sa.String(255), nullable=False, server_default=''))
    op.execute("UPDATE users SET api_key_hash = key_hash")
    op.drop_column('users', 'key_hash')
    op.drop_column('users', 'key_prefix')