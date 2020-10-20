"""add token to user authentication details

Revision ID: c3caf0398aa6
Revises: b657ea63d4bf
Create Date: 2020-10-20 18:02:33.400940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3caf0398aa6'
down_revision = 'b657ea63d4bf'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user_authentication_details', sa.Column('token', sa.String(250), unique=True))
    op.create_index('ik_user_authentication_details_token', 'user_authentication_details', ['token'])


def downgrade():
    op.drop_table('ik_user_authentication_details_token')
    op.drop_column('user_authentication_details', 'token')
