"""create users table

Revision ID: 9c53a81e51d6
Revises:
Create Date: 2020-10-19 11:39:07.635678

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgresql

# revision identifiers, used by Alembic.
revision = '9c53a81e51d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID, nullable=False, primary_key=True),
        sa.Column('first_name', sa.String(20), nullable=False),
        sa.Column('last_name', sa.String(20), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False, unique=True, server_default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False, unique=True, server_default=sa.func.now()),
    )

    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_index('ik_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('ik_users_email', 'users')
    op.drop_index('uq_users_email', 'users')
    op.drop_table('users')
