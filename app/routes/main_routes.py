# app/routes/main_routes.py

from flask import Blueprint, render_template, request
from app.models import db, Conta, Lancamento, Cartao, Categoria
from datetime import datetime, date
from calendar import monthrange
from sqlalchemy import func, extract, and_
from collections import defaultdict

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
    # Para receitas: apenas tipo = 'receita'
    receitas = Lancamento.query.filter(
        Lancamento.tipo == 'receita',
        Lancamento.data_vencimento >= primeiro_dia,
        Lancamento.data_vencimento <= ultimo_dia
    ).order_by(Lancamento.data_vencimento).all()
    
    # Para despesas: apenas tipo = 'despesa'
    despesas_query = Lancamento.query.filter(
        Lancamento.tipo == 'despesa',
        Lancamento.data_vencimento >= primeiro_dia,
        Lancamento.data_vencimento <= ultimo_dia
    ).order_by(Lancamento.data_vencimento).all()
    
    # Processar faturas de cartão
    cartoes = Cartao.query.filter_by(ativo=True).all()
    faturas_cartao = []
    
    for cartao in cartoes:
        # Calcular a data de vencimento do cartão no mês atual
        try:
            data_vencimento_cartao = date(ano, mes, cartao.dia_vencimento)
        except ValueError:
            # Se o dia não existir no mês (ex: 31 de fevereiro), usar o último dia do mês
            data_vencimento_cartao = ultimo_dia
        
        # Buscar despesas do cartão que devem aparecer neste mês
        despesas_cartao = Lancamento.query.filter(
            Lancamento.tipo == 'cartao_credito',
            Lancamento.cartao_id == cartao.id,
            extract('year', Lancamento.mes_inicial_cartao) == ano,
            extract('month', Lancamento.mes_inicial_cartao) == mes
        ).all()
        
        if despesas_cartao:
            # Calcular total da fatura
            total_fatura = sum(despesa.valor for despesa in despesas_cartao)
            
            # Criar um lançamento virtual para a fatura
            fatura = type('Lancamento', (), {
                'id': f'fatura_{cartao.id}_{ano}_{mes}',
                'descricao': f'Fatura {cartao.nome}',
                'valor': total_fatura,
                'tipo': 'fatura_cartao',
                'conta_id': cartao.conta_id,
                'conta': cartao.conta,
                'cartao_id': cartao.id,
                'cartao': cartao,
                'categoria': type('Categoria', (), {'nome': 'Cartão de Crédito', 'cor': '#6f42c1', 'icone': 'credit_card'}),
                'subcategoria': None,
                'data_vencimento': data_vencimento_cartao,
                'data_pagamento': None,
                'status': 'pendente',
                'recorrencia': 'unica',
                'tag': 'Fatura',
                'despesas_cartao': despesas_cartao
            })
            
            # Verificar se a fatura já foi paga (buscar um lançamento de pagamento)
            pagamento_fatura = Lancamento.query.filter(
                Lancamento.tipo == 'despesa',
                Lancamento.descricao.like(f'%Pagamento Fatura {cartao.nome}%'),
                Lancamento.data_vencimento >= primeiro_dia,
                Lancamento.data_vencimento <= ultimo_dia
            ).first()
            
            if pagamento_fatura and pagamento_fatura.status == 'pago':
                fatura.status = 'pago'
                fatura.data_pagamento = pagamento_fatura.data_pagamento
            
            faturas_cartao.append(fatura)
    
    # Combinar despesas normais com faturas de cartão
    despesas = despesas_query + faturas_cartao
    # Ordenar por data de vencimento
    despesas.sort(key=lambda x: x.data_vencimento)
    
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

@main_bp.route('/extrato-cartao')
def extrato_cartao():
    # Obter mês/ano e cartão da query string
    mes = request.args.get('mes', type=int, default=date.today().month)
    ano = request.args.get('ano', type=int, default=date.today().year)
    cartao_id = request.args.get('cartao_id', type=int)
    
    # Buscar todos os cartões ativos
    cartoes = Cartao.query.filter_by(ativo=True).order_by(Cartao.nome).all()
    
    # Se não foi selecionado um cartão, pegar o primeiro
    if not cartao_id and cartoes:
        cartao_id = cartoes[0].id
    
    cartao_selecionado = None
    despesas = []
    total_fatura = 0
    data_vencimento = None
    fatura_paga = False
    
    if cartao_id:
        cartao_selecionado = Cartao.query.get(cartao_id)
        
        if cartao_selecionado:
            # Calcular a data de vencimento do cartão no mês selecionado
            try:
                data_vencimento = date(ano, mes, cartao_selecionado.dia_vencimento)
            except ValueError:
                # Se o dia não existir no mês, usar o último dia
                ultimo_dia = monthrange(ano, mes)[1]
                data_vencimento = date(ano, mes, ultimo_dia)
            
            # Buscar despesas do cartão para o mês selecionado
            despesas = Lancamento.query.filter(
                Lancamento.tipo == 'cartao_credito',
                Lancamento.cartao_id == cartao_id,
                extract('year', Lancamento.mes_inicial_cartao) == ano,
                extract('month', Lancamento.mes_inicial_cartao) == mes
            ).order_by(Lancamento.data_vencimento).all()
            
            # Calcular total da fatura
            total_fatura = sum(despesa.valor for despesa in despesas)
            
            # Verificar se a fatura foi paga
            primeiro_dia = date(ano, mes, 1)
            ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
            
            pagamento_fatura = Lancamento.query.filter(
                Lancamento.tipo == 'despesa',
                Lancamento.descricao.like(f'%Pagamento Fatura {cartao_selecionado.nome}%'),
                Lancamento.data_vencimento >= primeiro_dia,
                Lancamento.data_vencimento <= ultimo_dia
            ).first()
            
            if pagamento_fatura and pagamento_fatura.status == 'pago':
                fatura_paga = True
    
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
    
    return render_template('extrato_cartao.html',
                         cartoes=cartoes,
                         cartao_selecionado=cartao_selecionado,
                         despesas=despesas,
                         total_fatura=total_fatura,
                         data_vencimento=data_vencimento,
                         fatura_paga=fatura_paga,
                         mes_selecionado=mes,
                         ano_selecionado=ano,
                         meses=meses,
                         today=date.today())