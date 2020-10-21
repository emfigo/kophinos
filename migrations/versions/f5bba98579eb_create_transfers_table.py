"""create transfers table

Revision ID: f5bba98579eb
Revises: cd7963496868
Create Date: 2020-10-21 13:08:36.563962

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgresql


# revision identifiers, used by Alembic.
revision = 'f5bba98579eb'
down_revision = 'cd7963496868'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'transfers',
        sa.Column('id', postgresql.UUID, nullable=False, primary_key=True),
        sa.Column('sender_user_id', postgresql.UUID, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('receiver_user_id', postgresql.UUID, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('amount_cents', sa.BigInteger, nullable=False),
        sa.Column('currency', sa.String(15), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False, unique=True, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('transfers')
