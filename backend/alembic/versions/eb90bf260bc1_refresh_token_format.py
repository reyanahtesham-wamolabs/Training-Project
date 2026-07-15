"""Refresh token format

Revision ID: eb90bf260bc1
Revises: e5fa29b0e6ce
Create Date: 2026-07-13 04:03:51.927215

"""
from __future__ import annotations
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eb90bf260bc1'
down_revision: Union[str, Sequence[str], None] = 'e5fa29b0e6ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the UUID id column with a server-side default for new inserts.
    op.add_column(
        'RefreshToken',
        sa.Column(
            'id',
            sa.String(),
            nullable=True,
            server_default=sa.text('gen_random_uuid()::text'),
        ),
    )

    # Backfill existing rows with unique UUID values.
    conn = op.get_bind()
    rows = conn.execute(sa.text('SELECT email FROM RefreshToken'))
    for row in rows:
        conn.execute(
            sa.text('UPDATE RefreshToken SET id = :id WHERE email = :email'),
            {'id': str(uuid4()), 'email': row[0]},
        )

    # Replace the old primary key on email with the new id primary key.
    op.drop_constraint('RefreshToken_pkey', 'RefreshToken', type_='primary')
    op.create_primary_key('RefreshToken_pkey', 'RefreshToken', ['id'])
    op.alter_column('RefreshToken', 'id', nullable=False)

def downgrade() -> None:
    """Downgrade schema."""
    # Replace the primary key on id with the original email primary key.
    op.drop_constraint('RefreshToken_pkey', 'RefreshToken', type_='primary')
    op.create_primary_key('RefreshToken_pkey', 'RefreshToken', ['email'])

    # Remove the UUID id column.
    op.drop_column('RefreshToken', 'id')
