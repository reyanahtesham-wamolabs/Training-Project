"""allow_multiple_replies_per_comment

Revision ID: 6da1769b3ffd
Revises: 1784d81767a7
Create Date: 2026-07-21 21:01:55.724826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6da1769b3ffd'
down_revision: Union[str, Sequence[str], None] = '1784d81767a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    try:
        op.drop_constraint('Comment_parent_comment_id_key', 'Comment', type_='unique')
    except Exception:
        pass


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint('Comment_parent_comment_id_key', 'Comment', ['parent_comment_id'])
