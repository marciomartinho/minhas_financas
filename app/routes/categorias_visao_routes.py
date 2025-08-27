# app/routes/categorias_visao_routes.py

from flask import Blueprint, render_template, request
from app.models import db, Lancamento, Categoria, Subcategoria
from datetime import datetime, date
from calendar import monthrange
from sqlalchemy import func, extract, and_, or_

# Criar o Blueprint
categorias_visao_bp = Blueprint('categorias_visao', __name__, url_prefix='/categorias-visao')

@categorias_visao_bp.route('/visao-geral')
def visao_geral_categorias():
    """Página de visão geral por categorias e subcategorias"""
    
    # Obter parâmetros da query string
    categoria_id = request.args.get('categoria_id', type=int)
    subcategoria_id = request.args.get('subcategoria_id', type=int)
    mes = request.args.get('mes', type=int, default=0)  # 0 = todo período
    ano = request.args.get('ano', type=int, default=date.today().year)
    tipo_filtro = request.args.get('tipo', default='todos')  # todos, receitas, despesas
    
    # Buscar todas as categorias do sistema
    categorias = Categoria.query.order_by(Categoria.nome).all()
    
    # Buscar subcategorias se uma categoria foi selecionada
    subcategorias = []
    if categoria_id:
        subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).order_by(Subcategoria.nome).all()
    
    # Inicializar variáveis
    lancamentos = []
    total_receitas = 0
    total_despesas = 0
    resumo_por_tipo = {}
    categoria_selecionada = None
    subcategoria_selecionada = None
    
    # Se uma categoria foi selecionada
    if categoria_id:
        categoria_selecionada = Categoria.query.get(categoria_id)
        
        # Construir query base
        query_base = Lancamento.query.filter(
            Lancamento.categoria_id == categoria_id
        )
        
        # Se uma subcategoria foi selecionada
        if subcategoria_id:
            subcategoria_selecionada = Subcategoria.query.get(subcategoria_id)
            query_base = query_base.filter(
                Lancamento.subcategoria_id == subcategoria_id
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
        
        # Aplicar filtro de tipo
        if tipo_filtro == 'receitas':
            query_base = query_base.filter(Lancamento.tipo == 'receita')
        elif tipo_filtro == 'despesas':
            query_base = query_base.filter(
                or_(
                    Lancamento.tipo == 'despesa',
                    Lancamento.tipo == 'cartao_credito'
                )
            )
        
        # Buscar lançamentos
        lancamentos = query_base.order_by(Lancamento.data_vencimento.desc()).all()
        
        # Calcular totais separados
        receitas = [l for l in lancamentos if l.tipo == 'receita']
        despesas = [l for l in lancamentos if l.tipo in ['despesa', 'cartao_credito']]
        
        total_receitas = sum(l.valor for l in receitas)
        total_despesas = sum(l.valor for l in despesas)
        
        # Criar resumo por tipo (receita/despesa) e por subcategoria se aplicável
        if not subcategoria_id and subcategorias:
            # Resumo por subcategorias
            for subcategoria in subcategorias:
                sub_lancamentos = [l for l in lancamentos if l.subcategoria_id == subcategoria.id]
                if sub_lancamentos:
                    resumo_por_tipo[subcategoria.nome] = {
                        'id': subcategoria.id,
                        'nome': subcategoria.nome,
                        'total': sum(l.valor for l in sub_lancamentos),
                        'quantidade': len(sub_lancamentos),
                        'receitas': sum(l.valor for l in sub_lancamentos if l.tipo == 'receita'),
                        'despesas': sum(l.valor for l in sub_lancamentos if l.tipo in ['despesa', 'cartao_credito'])
                    }
            
            # Adicionar lançamentos sem subcategoria
            sem_subcategoria = [l for l in lancamentos if l.subcategoria_id is None]
            if sem_subcategoria:
                resumo_por_tipo['Sem Subcategoria'] = {
                    'id': None,
                    'nome': 'Sem Subcategoria',
                    'total': sum(l.valor for l in sem_subcategoria),
                    'quantidade': len(sem_subcategoria),
                    'receitas': sum(l.valor for l in sem_subcategoria if l.tipo == 'receita'),
                    'despesas': sum(l.valor for l in sem_subcategoria if l.tipo in ['despesa', 'cartao_credito'])
                }
    
    # Se não há categoria selecionada, mostrar resumo geral de categorias
    elif not categoria_id:
        # Construir query base para resumo geral
        query_base = Lancamento.query
        
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
        
        # Aplicar filtro de tipo
        if tipo_filtro == 'receitas':
            query_base = query_base.filter(Lancamento.tipo == 'receita')
        elif tipo_filtro == 'despesas':
            query_base = query_base.filter(
                or_(
                    Lancamento.tipo == 'despesa',
                    Lancamento.tipo == 'cartao_credito'
                )
            )
        
        # Buscar resumo agrupado por categoria
        for categoria in categorias:
            cat_lancamentos = query_base.filter(Lancamento.categoria_id == categoria.id).all()
            if cat_lancamentos:
                resumo_por_tipo[categoria.nome] = {
                    'id': categoria.id,
                    'nome': categoria.nome,
                    'cor': categoria.cor,
                    'total': sum(l.valor for l in cat_lancamentos),
                    'quantidade': len(cat_lancamentos),
                    'receitas': sum(l.valor for l in cat_lancamentos if l.tipo == 'receita'),
                    'despesas': sum(l.valor for l in cat_lancamentos if l.tipo in ['despesa', 'cartao_credito'])
                }
        
        # Calcular totais gerais
        todos_lancamentos = query_base.all()
        total_receitas = sum(l.valor for l in todos_lancamentos if l.tipo == 'receita')
        total_despesas = sum(l.valor for l in todos_lancamentos if l.tipo in ['despesa', 'cartao_credito'])
    
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
    
    return render_template('categorias_visao_geral.html',
                         categorias=categorias,
                         subcategorias=subcategorias,
                         categoria_id=categoria_id,
                         subcategoria_id=subcategoria_id,
                         categoria_selecionada=categoria_selecionada,
                         subcategoria_selecionada=subcategoria_selecionada,
                         lancamentos=lancamentos,
                         total_receitas=total_receitas,
                         total_despesas=total_despesas,
                         resumo_por_tipo=resumo_por_tipo,
                         mes_selecionado=mes,
                         ano_selecionado=ano,
                         tipo_filtro=tipo_filtro,
                         meses=meses,
                         periodo_exibido=periodo_exibido,
                         today=date.today())

@categorias_visao_bp.route('/api/subcategorias/<int:categoria_id>')
def listar_subcategorias(categoria_id):
    """API para retornar lista de subcategorias de uma categoria (para uso futuro com AJAX)"""
    subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).order_by(Subcategoria.nome).all()
    
    return {
        'subcategorias': [
            {'id': s.id, 'nome': s.nome} 
            for s in subcategorias
        ]
    }