"""change assignment and assignment roles

Revision ID: 1784d81767a7
Revises: ffe104a000ec
Create Date: 2026-07-20 22:11:23.138124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1784d81767a7'
down_revision: Union[str, Sequence[str], None] = 'ffe104a000ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.execute("""
        CREATE TYPE assignmentrole_new AS ENUM (
            'project_admin',
            'project_member'
        )
    """)

    op.execute("""
        ALTER TABLE "Assignment"
        ALTER COLUMN role
        TYPE assignmentrole_new
        USING role::text::assignmentrole_new
    """)

    op.execute("DROP TYPE assignmentrole")

    op.execute("""
        ALTER TYPE assignmentrole_new
        RENAME TO assignmentrole
    """)


def downgrade():
    op.execute("""
        CREATE TYPE assignmentrole_old AS ENUM (
            'team_lead',
            'manager',
            'developer'
        )
    """)

    op.execute("""
        ALTER TABLE "Assignment"
        ALTER COLUMN role
        TYPE assignmentrole_old
        USING role::text::assignmentrole_old
    """)

    op.execute("DROP TYPE assignmentrole")

    op.execute("""
        ALTER TYPE assignmentrole_old
        RENAME TO assignmentrole
    """)