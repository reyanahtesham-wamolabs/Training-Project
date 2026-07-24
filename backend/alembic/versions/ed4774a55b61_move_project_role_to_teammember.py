"""move_project_role_to_teammember

Revision ID: ed4774a55b61
Revises: 6e67cd5b8de9
Create Date: 2026-07-22 17:45:35.890171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed4774a55b61'
down_revision: Union[str, Sequence[str], None] = '6e67cd5b8de9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add project_role to TeamMember (default to project_member)
    op.add_column('TeamMember', sa.Column('project_role', sa.Enum('project_admin', 'project_member', name='assignmentrole'), server_default='project_member', nullable=False))

    # 2. Migrate existing project_admin roles from Assignment to TeamMember
    op.execute("""
        UPDATE "TeamMember" tm
        SET project_role = 'project_admin'
        FROM "Assignment" a
        JOIN "Task" t ON a.task_id = t.id
        JOIN "Team" team ON team.project_id = t.project_id
        WHERE a.role = 'project_admin' 
          AND a.user_id = tm.user_id 
          AND tm.team_id = team.id
    """)

    # 3. Drop role from Assignment
    op.drop_column('Assignment', 'role')


def downgrade() -> None:
    # 1. Add role back to Assignment (default to project_member)
    op.add_column('Assignment', sa.Column('role', sa.Enum('project_admin', 'project_member', name='assignmentrole'), server_default='project_member', nullable=False))

    # Note: We can't perfectly restore which specific assignment had project_admin vs project_member
    # since that granularity was lost. A reasonable fallback is to make all assignments for a project_admin 
    # take on the project_admin role.
    op.execute("""
        UPDATE "Assignment" a
        SET role = 'project_admin'
        FROM "TeamMember" tm
        JOIN "Team" team ON tm.team_id = team.id
        JOIN "Task" t ON t.project_id = team.project_id
        WHERE tm.project_role = 'project_admin'
          AND a.user_id = tm.user_id
          AND a.task_id = t.id
    """)

    # 2. Drop project_role from TeamMember
    op.drop_column('TeamMember', 'project_role')
