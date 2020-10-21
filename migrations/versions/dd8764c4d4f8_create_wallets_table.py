"""create wallets table

Revision ID: dd8764c4d4f8
Revises: c3caf0398aa6
Create Date: 2020-10-21 09:47:07.549783

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgresql


# revision identifiers, used by Alembic.
revision = 'dd8764c4d4f8'
down_revision = 'c3caf0398aa6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'wallets',
        sa.Column('id', postgresql.UUID, nullable=False, primary_key=True),
        sa.Column('user_id', postgresql.UUID, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('balance_cents', sa.BigInteger, nullable=False),
        sa.Column('currency', sa.String(15), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False, unique=True, server_default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False, unique=True, server_default=sa.func.now()),
    )

    op.create_unique_constraint('uq_wallets_user_id_currency', 'wallets', ['user_id', 'currency'])

def downgrade():
    op.drop_index('uq_wallets_user_id_currency', 'wallets')
    op.drop_table('wallets')
