# app/routes/main_routes.py

from flask import Blueprint, render_template, request
from app.models import db, Conta, Lancamento
from datetime import datetime, date
from calendar import monthrange
from sqlalchemy import func

# A forma mais simples de criar um Blueprint, sem caminhos.
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # Obter mês/ano da query string ou usar o atual
    mes = request.args.get('mes', type=int, default=date.today().month)
    ano = request.args.get('ano', type=int, default=date.today().year)
    
    # Calcular primeiro e último dia do mês
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
    
    # Buscar saldos das contas
    contas_corrente = Conta.query.filter_by(tipo_conta='Corrente').all()
    contas_investimento = Conta.query.filter_by(tipo_conta='Investimento').all()
    
    # Calcular totais usando saldo_atual (sempre recalcular para pegar mudanças)
    total_corrente = db.session.query(func.sum(Conta.saldo_atual)).filter(Conta.tipo_conta == 'Corrente').scalar() or 0
    total_investimento = db.session.query(func.sum(Conta.saldo_atual)).filter(Conta.tipo_conta == 'Investimento').scalar() or 0
    
    # Buscar lançamentos do mês
    # Para receitas: incluir receitas normais e transferências de entrada
    receitas = Lancamento.query.filter(
        db.or_(
            db.and_(
                Lancamento.tipo == 'receita',
                Lancamento.data_vencimento >= primeiro_dia,
                Lancamento.data_vencimento <= ultimo_dia
            ),
            db.and_(
                Lancamento.tipo == 'transferencia',
                Lancamento.conta_destino_id.isnot(None),  # Transferências de entrada têm conta_destino_id
                Lancamento.conta_destino_id < Lancamento.conta_id,  # Para evitar duplicatas
                Lancamento.data_vencimento >= primeiro_dia,
                Lancamento.data_vencimento <= ultimo_dia
            )
        )
    ).order_by(Lancamento.data_vencimento).all()
    
    # Para despesas: incluir despesas normais e transferências de saída
    despesas = Lancamento.query.filter(
        db.or_(
            db.and_(
                Lancamento.tipo == 'despesa',
                Lancamento.data_vencimento >= primeiro_dia,
                Lancamento.data_vencimento <= ultimo_dia
            ),
            db.and_(
                Lancamento.tipo == 'transferencia',
                Lancamento.conta_destino_id.isnot(None),  # Transferências de saída têm conta_destino_id
                Lancamento.conta_id < Lancamento.conta_destino_id,  # Para evitar duplicatas
                Lancamento.data_vencimento >= primeiro_dia,
                Lancamento.data_vencimento <= ultimo_dia
            )
        )
    ).order_by(Lancamento.data_vencimento).all()
    
    # Calcular totais de receitas e despesas
    total_receitas = sum(lancamento.valor for lancamento in receitas)
    total_despesas = sum(lancamento.valor for lancamento in despesas)
    
    # Criar lista de meses para o seletor
    meses = [
        {'numero': 1, 'nome': 'Janeiro'},
        {'numero': 2, 'nome': 'Fevereiro'},
        {'numero': 3, 'nome': 'Março'},
        {'numero': 4, 'nome': 'Abril'},
        {'numero': 5, 'nome': 'Maio'},
        {'numero': 6, 'nome': 'Junho'},
        {'numero': 7, 'nome': 'Julho'},
        {'numero': 8, 'nome': 'Agosto'},
        {'numero': 9, 'nome': 'Setembro'},
        {'numero': 10, 'nome': 'Outubro'},
        {'numero': 11, 'nome': 'Novembro'},
        {'numero': 12, 'nome': 'Dezembro'}
    ]
    
    return render_template('home.html',
                         contas_corrente=contas_corrente,
                         contas_investimento=contas_investimento,
                         total_corrente=total_corrente,
                         total_investimento=total_investimento,
                         receitas=receitas,
                         despesas=despesas,
                         total_receitas=total_receitas,
                         total_despesas=total_despesas,
                         mes_selecionado=mes,
                         ano_selecionado=ano,
                         meses=meses,
                         today=date.today())