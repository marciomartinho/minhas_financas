"""Adiciona campo mes_inicial_cartao na tabela lancamentos

Revision ID: e8f9a3b2c4d5
Revises: d1cd60c8c190
Create Date: 2025-07-30 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8f9a3b2c4d5'
down_revision = 'd1cd60c8c190'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna mes_inicial_cartao
    with op.batch_alter_table('lancamentos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mes_inicial_cartao', sa.Date(), nullable=True))


def downgrade():
    # Remover coluna mes_inicial_cartao
    with op.batch_alter_table('lancamentos', schema=None) as batch_op:
        batch_op.drop_column('mes_inicial_cartao')