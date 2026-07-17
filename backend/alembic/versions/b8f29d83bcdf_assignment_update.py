"""Assignment Update

Revision ID: b8f29d83bcdf
Revises: 32e65e9a6e86
Create Date: 2026-07-16 00:50:20.930587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8f29d83bcdf'
down_revision: Union[str, Sequence[str], None] = '32e65e9a6e86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    assignment_roles = postgresql.ENUM(
        "team_lead",
        "manager",
        "developer",
        name="assignmentrole",
        create_type=False,  # don't let create_table auto-create it
    )
    assignment_roles.create(op.get_bind(), checkfirst=True)  # create only if missing

    op.create_table(
        "Assignment",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("task_id", sa.String(), nullable=False),
        sa.Column("role", assignment_roles, nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["Project.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["Task.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["User.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("Assignment")
    postgresql.ENUM(name="assignmentrole").drop(op.get_bind(), checkfirst=True)