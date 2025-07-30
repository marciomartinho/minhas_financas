"""Adiciona campo saldo_atual na tabela contas

Revision ID: d1cd60c8c190
Revises: 15f43e02e8f5
Create Date: 2025-07-30 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1cd60c8c190'
down_revision = '15f43e02e8f5'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna com valor padrão temporário
    op.add_column('contas', sa.Column('saldo_atual', sa.Numeric(precision=10, scale=2), nullable=True))
    
    # Atualizar saldo_atual com o valor do saldo_inicial
    op.execute('UPDATE contas SET saldo_atual = COALESCE(saldo_inicial, 0)')
    
    # Tornar a coluna NOT NULL
    op.alter_column('contas', 'saldo_atual',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    nullable=False)


def downgrade():
    op.drop_column('contas', 'saldo_atual')