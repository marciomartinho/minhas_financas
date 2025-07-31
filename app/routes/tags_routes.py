# app/routes/tags_routes.py

from flask import Blueprint, render_template, request
from app.models import db, Lancamento, Categoria
from datetime import datetime, date
from calendar import monthrange
from sqlalchemy import func, extract, and_, or_

# Criar o Blueprint
tags_bp = Blueprint('tags', __name__, url_prefix='/tags')

@tags_bp.route('/visao-geral')
def visao_geral_tags():
    """Página de visão geral por tags"""
    
    # Obter parâmetros da query string
    tag_selecionada = request.args.get('tag', '')
    mes = request.args.get('mes', type=int, default=0)  # 0 = todo período
    ano = request.args.get('ano', type=int, default=date.today().year)
    
    # Buscar todas as tags únicas do sistema
    tags_query = db.session.query(Lancamento.tag).filter(
        Lancamento.tag.isnot(None),
        Lancamento.tag != ''
    ).distinct().order_by(Lancamento.tag)
    
    tags_disponiveis = [tag[0] for tag in tags_query.all()]
    
    # Inicializar variáveis
    receitas = []
    despesas = []
    total_receitas = 0
    total_despesas = 0
    
    # Se uma tag foi selecionada, buscar lançamentos
    if tag_selecionada:
        # Construir query base
        query_base = Lancamento.query.filter(
            Lancamento.tag == tag_selecionada
        )
        
        # Aplicar filtros de data
        if mes > 0:  # Mês específico
            primeiro_dia = date(ano, mes, 1)
            ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
            query_base = query_base.filter(
                Lancamento.data_vencimento >= primeiro_dia,
                Lancamento.data_vencimento <= ultimo_dia
            )
        elif mes == -1:  # Ano inteiro
            primeiro_dia = date(ano, 1, 1)
            ultimo_dia = date(ano, 12, 31)
            query_base = query_base.filter(
                Lancamento.data_vencimento >= primeiro_dia,
                Lancamento.data_vencimento <= ultimo_dia
            )
        # Se mes == 0, não aplica filtro de data (todo período)
        
        # Buscar receitas (apenas tipo = 'receita')
        receitas = query_base.filter(
            Lancamento.tipo == 'receita'
        ).order_by(Lancamento.data_vencimento.desc()).all()
        
        # Buscar despesas (tipo = 'despesa' OU 'cartao_credito')
        despesas = query_base.filter(
            or_(
                Lancamento.tipo == 'despesa',
                Lancamento.tipo == 'cartao_credito'
            )
        ).order_by(Lancamento.data_vencimento.desc()).all()
        
        # Calcular totais
        total_receitas = sum(lancamento.valor for lancamento in receitas)
        total_despesas = sum(lancamento.valor for lancamento in despesas)
    
    # Criar lista de meses para o seletor
    meses = [
        {'numero': 0, 'nome': 'Todo o Período'},
        {'numero': -1, 'nome': 'Ano Inteiro'},
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
    
    # Definir período exibido para o template
    if mes == 0:
        periodo_exibido = "Todo o Período"
    elif mes == -1:
        periodo_exibido = f"Ano {ano}"
    else:
        periodo_exibido = f"{meses[mes + 1]['nome']}/{ano}"
    
    return render_template('tags_visao_geral.html',
                         tags_disponiveis=tags_disponiveis,
                         tag_selecionada=tag_selecionada,
                         receitas=receitas,
                         despesas=despesas,
                         total_receitas=total_receitas,
                         total_despesas=total_despesas,
                         mes_selecionado=mes,
                         ano_selecionado=ano,
                         meses=meses,
                         periodo_exibido=periodo_exibido,
                         today=date.today())

@tags_bp.route('/api/tags')
def listar_tags():
    """API para retornar lista de tags disponíveis (para uso futuro com AJAX)"""
    tags_query = db.session.query(Lancamento.tag).filter(
        Lancamento.tag.isnot(None),
        Lancamento.tag != ''
    ).distinct().order_by(Lancamento.tag)
    
    tags = [{'nome': tag[0]} for tag in tags_query.all()]
    
    return {'tags': tags}