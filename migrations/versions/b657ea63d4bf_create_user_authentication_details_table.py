"""create user authentication details table

Revision ID: b657ea63d4bf
Revises: 9c53a81e51d6
Create Date: 2020-10-19 16:36:54.094595

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgresql

# revision identifiers, used by Alembic.
revision = 'b657ea63d4bf'
down_revision = '9c53a81e51d6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_authentication_details',
        sa.Column('id', postgresql.UUID, nullable=False, primary_key=True),
        sa.Column('user_id', postgresql.UUID, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('password', sa.String(500), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False, unique=True, server_default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False, unique=True, server_default=sa.func.now()),
    )

    op.create_unique_constraint('uq_user_authentication_details_email_password', 'user_authentication_details', ['email', 'password'])
    op.create_index('ik_user_authentication_details_email', 'user_authentication_details', ['email'])


def downgrade():
    op.drop_index('uq_user_authentication_details_email_password', 'user_authentication_details')
    op.drop_table('user_authentication_details')
