"""change to user

Revision ID: b331952aa45c
Revises: 
Create Date: 2026-07-17 23:52:54.140586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b331952aa45c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('OTP', sa.Column('user_name', sa.String(), nullable=False))
    op.add_column('OTP', sa.Column('new_desired_name', sa.String(), nullable=True))
    op.add_column('OTP', sa.Column('new_desired_email', sa.String(), nullable=True))
    op.alter_column('OTP', 'new_desired_password',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # 1. Create the new enum type
    otpaction = postgresql.ENUM(
        'verify_profile', 'change_password', 'change_email', 'change_name',
        name='otpaction'
    )
    otpaction.create(op.get_bind())

    # 2. Convert the column to the new type, mapping old values -> new values
    op.execute("""
        ALTER TABLE "OTP"
        ALTER COLUMN action TYPE otpaction
        USING (
            CASE action::text
                WHEN 'account_verification' THEN 'verify_profile'
                ELSE action::text
            END
        )::otpaction
    """)

    # 3. Drop the old enum type now that nothing references it
    op.execute('DROP TYPE otpactiontype')

    op.drop_column('OTP', 'user_email')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    otpactiontype = postgresql.ENUM(
        'change_password', 'account_verification',
        name='otpactiontype'
    )
    otpactiontype.create(op.get_bind())

    op.add_column('OTP', sa.Column('user_email', sa.String(), nullable=True))

    op.execute("""
        ALTER TABLE "OTP"
        ALTER COLUMN action TYPE otpactiontype
        USING (
            CASE action::text
                WHEN 'verify_profile' THEN 'account_verification'
                WHEN 'change_email' THEN 'account_verification'
                WHEN 'change_name' THEN 'account_verification'
                ELSE action::text
            END
        )::otpactiontype
    """)

    op.execute('DROP TYPE otpaction')

    op.alter_column('OTP', 'new_desired_password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('OTP', 'new_desired_email')
    op.drop_column('OTP', 'new_desired_name')
    op.drop_column('OTP', 'user_name')