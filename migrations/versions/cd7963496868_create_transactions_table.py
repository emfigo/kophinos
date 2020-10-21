"""create transactions table

Revision ID: cd7963496868
Revises: dd8764c4d4f8
Create Date: 2020-10-21 12:23:15.440053

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgresql


# revision identifiers, used by Alembic.
revision = 'cd7963496868'
down_revision = 'dd8764c4d4f8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID, nullable=False, primary_key=True),
        sa.Column('wallet_id', postgresql.UUID, sa.ForeignKey('wallets.id'), nullable=False),
        sa.Column('amount_cents', sa.BigInteger, nullable=False),
        sa.Column('type', sa.String(10), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False, unique=True, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('transactions')
