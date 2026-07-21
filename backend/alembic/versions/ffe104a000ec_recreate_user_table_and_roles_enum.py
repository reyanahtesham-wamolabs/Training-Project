"""recreate user table and roles enum

Revision ID: ffe104a000ec
Revises: 8357c8a0b8b8
Create Date: 2026-07-20 20:16:43.157482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffe104a000ec'
down_revision: Union[str, Sequence[str], None] = '8357c8a0b8b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create the new enum
    op.execute("""
        CREATE TYPE roles_new AS ENUM (
            'admin',
            'manager',
            'member'
        )
    """)

    # Convert the column to the new enum
    op.execute("""
        ALTER TABLE "User"
        ALTER COLUMN role
        TYPE roles_new
        USING role::text::roles_new
    """)

    # Remove the old enum
    op.execute("DROP TYPE roles")

    # Rename the new enum
    op.execute("""
        ALTER TYPE roles_new
        RENAME TO roles
    """)


def downgrade():
    op.execute("""
        CREATE TYPE roles_old AS ENUM (
            'admin',
            'Admin',
            'manager',
            'member',
            'Member'
        )
    """)

    op.execute("""
        ALTER TABLE "User"
        ALTER COLUMN role
        TYPE roles_old
        USING role::text::roles_old
    """)

    op.execute("DROP TYPE roles")

    op.execute("""
        ALTER TYPE roles_old
        RENAME TO roles
    """)