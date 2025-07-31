# app/routes/metas_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Meta, MetaHistorico, Categoria, Lancamento
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from sqlalchemy import func, extract, and_, or_

# Criar o Blueprint
metas_bp = Blueprint('metas', __name__, url_prefix='/metas')

# Substituir toda a função listar_metas() em app/routes/metas_routes.py

@metas_bp.route('/')
def listar_metas():
    """Página principal de metas orçamentárias"""
    # Obter mês/ano da query string ou usar o atual
    mes = request.args.get('mes', type=int, default=date.today().month)
    ano = request.args.get('ano', type=int, default=date.today().year)
    
    # Criar data de referência
    mes_referencia = date(ano, mes, 1)
    
    # Buscar todas as metas ativas
    metas_ativas = Meta.query.filter_by(ativa=True).order_by(Meta.nome).all()
    
    # Buscar categorias para o modal de nova meta
    categorias = Categoria.query.filter_by(ativa=True).order_by(Categoria.nome).all()
    
    # Buscar tags únicas do sistema
    tags_query = db.session.query(Lancamento.tag).filter(
        Lancamento.tag.isnot(None),
        Lancamento.tag != ''
    ).distinct().order_by(Lancamento.tag)
    tags_disponiveis = [tag[0] for tag in tags_query.all()]
    
    # Calcular progresso de cada meta para o mês selecionado
    metas_com_progresso = []
    
    for meta in metas_ativas:
        # Verificar se a meta já estava ativa no período selecionado
        if meta.data_inicio <= mes_referencia:
            progresso = calcular_progresso_meta(meta, mes_referencia)
            metas_com_progresso.append({
                'meta': meta,
                'progresso': progresso
            })
    
    # Estatísticas gerais para o mês selecionado
    total_metas = len(metas_com_progresso)
    metas_cumpridas = sum(1 for m in metas_com_progresso if m['progresso']['percentual'] <= 100)
    
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
    
    return render_template('metas.html',
                         metas=metas_com_progresso,
                         categorias=categorias,
                         tags_disponiveis=tags_disponiveis,
                         total_metas=total_metas,
                         metas_cumpridas=metas_cumpridas,
                         mes_selecionado=mes,  # ESTA LINHA ESTAVA FALTANDO
                         ano_selecionado=ano,  # ESTA LINHA ESTAVA FALTANDO
                         mes_referencia=mes_referencia,
                         meses=meses,
                         today=date.today())

@metas_bp.route('/nova', methods=['POST'])
def criar_meta():
    """Criar nova meta orçamentária"""
    try:
        # Capturar dados do formulário
        tipo = request.form.get('tipo')
        valor_limite = Decimal(request.form.get('valor_limite', '0'))
        periodo = request.form.get('periodo')
        data_inicio = datetime.strptime(request.form.get('data_inicio'), '%Y-%m-%d').date()
        
        # Configurações extras
        alertar_percentual = int(request.form.get('alertar_percentual', 80))
        renovar_automaticamente = request.form.get('renovar_automaticamente') == 'on'
        incluir_cartao = request.form.get('incluir_cartao') == 'on'
        
        # Validar valor
        if valor_limite <= 0:
            flash('O valor limite deve ser maior que zero!', 'error')
            return redirect(url_for('metas.listar_metas'))
        
        # Criar meta baseada no tipo
        if tipo == 'categoria':
            categoria_id = int(request.form.get('categoria_id'))
            categoria = Categoria.query.get(categoria_id)
            
            if not categoria:
                flash('Categoria inválida!', 'error')
                return redirect(url_for('metas.listar_metas'))
            
            # Verificar se já existe meta ativa para esta categoria
            meta_existente = Meta.query.filter_by(
                tipo='categoria',
                categoria_id=categoria_id,
                ativa=True
            ).first()
            
            if meta_existente:
                flash(f'Já existe uma meta ativa para a categoria {categoria.nome}!', 'error')
                return redirect(url_for('metas.listar_metas'))
            
            nome = f"Meta: {categoria.nome}"
            nova_meta = Meta(
                nome=nome,
                tipo=tipo,
                categoria_id=categoria_id,
                valor_limite=valor_limite,
                periodo=periodo,
                data_inicio=data_inicio,
                alertar_percentual=alertar_percentual,
                renovar_automaticamente=renovar_automaticamente,
                incluir_cartao=incluir_cartao
            )
            
        elif tipo == 'tag':
            tag = request.form.get('tag')
            
            if not tag:
                flash('Tag inválida!', 'error')
                return redirect(url_for('metas.listar_metas'))
            
            # Verificar se já existe meta ativa para esta tag
            meta_existente = Meta.query.filter_by(
                tipo='tag',
                tag=tag,
                ativa=True
            ).first()
            
            if meta_existente:
                flash(f'Já existe uma meta ativa para a tag {tag}!', 'error')
                return redirect(url_for('metas.listar_metas'))
            
            nome = f"Meta: {tag}"
            nova_meta = Meta(
                nome=nome,
                tipo=tipo,
                tag=tag,
                valor_limite=valor_limite,
                periodo=periodo,
                data_inicio=data_inicio,
                alertar_percentual=alertar_percentual,
                renovar_automaticamente=renovar_automaticamente,
                incluir_cartao=incluir_cartao
            )
            
        elif tipo == 'global':
            # Verificar se já existe meta global ativa
            meta_existente = Meta.query.filter_by(
                tipo='global',
                ativa=True
            ).first()
            
            if meta_existente:
                flash('Já existe uma meta global ativa!', 'error')
                return redirect(url_for('metas.listar_metas'))
            
            nome = "Meta Global: Todas as Despesas"
            nova_meta = Meta(
                nome=nome,
                tipo=tipo,
                valor_limite=valor_limite,
                periodo=periodo,
                data_inicio=data_inicio,
                alertar_percentual=alertar_percentual,
                renovar_automaticamente=renovar_automaticamente,
                incluir_cartao=incluir_cartao
            )
        else:
            flash('Tipo de meta inválido!', 'error')
            return redirect(url_for('metas.listar_metas'))
        
        # Salvar meta
        db.session.add(nova_meta)
        db.session.commit()
        
        flash('Meta criada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar meta: {e}")
        flash('Erro ao criar meta. Tente novamente.', 'error')
    
    return redirect(url_for('metas.listar_metas'))

@metas_bp.route('/<int:id>/editar', methods=['POST'])
def editar_meta(id):
    """Editar meta existente"""
    try:
        meta = Meta.query.get_or_404(id)
        
        # Atualizar dados
        meta.valor_limite = Decimal(request.form.get('valor_limite', '0'))
        meta.alertar_percentual = int(request.form.get('alertar_percentual', 80))
        meta.renovar_automaticamente = request.form.get('renovar_automaticamente') == 'on'
        meta.incluir_cartao = request.form.get('incluir_cartao') == 'on'
        
        db.session.commit()
        flash('Meta atualizada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao editar meta: {e}")
        flash('Erro ao atualizar meta.', 'error')
    
    return redirect(url_for('metas.listar_metas'))

@metas_bp.route('/<int:id>/pausar', methods=['POST'])
def pausar_meta(id):
    """Pausar/Reativar meta"""
    try:
        meta = Meta.query.get_or_404(id)
        meta.ativa = not meta.ativa
        
        db.session.commit()
        
        acao = 'reativada' if meta.ativa else 'pausada'
        flash(f'Meta {acao} com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao pausar meta: {e}")
        flash('Erro ao pausar/reativar meta.', 'error')
    
    return redirect(url_for('metas.listar_metas'))

@metas_bp.route('/<int:id>/excluir', methods=['POST'])
def excluir_meta(id):
    """Excluir meta"""
    try:
        meta = Meta.query.get_or_404(id)
        
        # Excluir históricos relacionados
        MetaHistorico.query.filter_by(meta_id=id).delete()
        
        # Excluir meta
        db.session.delete(meta)
        db.session.commit()
        
        flash('Meta excluída com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir meta: {e}")
        flash('Erro ao excluir meta.', 'error')
    
    return redirect(url_for('metas.listar_metas'))

# Funções auxiliares
def calcular_progresso_meta(meta, mes_referencia):
    """Calcular o progresso de uma meta para um determinado mês"""
    # Calcular período baseado no tipo
    if meta.periodo == 'mensal':
        data_inicio = mes_referencia
        data_fim = mes_referencia + relativedelta(months=1) - relativedelta(days=1)
    elif meta.periodo == 'trimestral':
        # Descobrir qual trimestre
        trimestre = ((mes_referencia.month - 1) // 3) * 3 + 1
        data_inicio = date(mes_referencia.year, trimestre, 1)
        data_fim = data_inicio + relativedelta(months=3) - relativedelta(days=1)
    elif meta.periodo == 'anual':
        data_inicio = date(mes_referencia.year, 1, 1)
        data_fim = date(mes_referencia.year, 12, 31)
    else:
        data_inicio = mes_referencia
        data_fim = mes_referencia + relativedelta(months=1) - relativedelta(days=1)
    
    # Determinar se estamos visualizando período futuro
    periodo_futuro = mes_referencia > date.today().replace(day=1)
    
    # Construir query base para cálculo do gasto
    if periodo_futuro:
        # Para períodos futuros, considerar todos os lançamentos (pagos e pendentes)
        query_base = Lancamento.query.filter(
            Lancamento.tipo.in_(['despesa', 'cartao_credito'])
        )
    else:
        # Para períodos passados e atual, considerar apenas pagos
        query_base = Lancamento.query.filter(
            Lancamento.tipo.in_(['despesa', 'cartao_credito']),
            Lancamento.status == 'pago'
        )
    
    # Filtrar por tipo de meta
    if meta.tipo == 'categoria':
        query_base = query_base.filter(Lancamento.categoria_id == meta.categoria_id)
    elif meta.tipo == 'tag':
        query_base = query_base.filter(Lancamento.tag == meta.tag)
    # Se for global, não precisa filtrar mais nada
    
    # Incluir ou não despesas de cartão
    if not meta.incluir_cartao:
        query_base = query_base.filter(Lancamento.tipo != 'cartao_credito')
    
    # Para despesas normais
    if periodo_futuro:
        # Para futuro, usar data_vencimento
        despesas_normais = query_base.filter(
            Lancamento.tipo == 'despesa',
            Lancamento.data_vencimento >= data_inicio,
            Lancamento.data_vencimento <= data_fim
        )
    else:
        # Para passado/atual, usar data_pagamento
        despesas_normais = query_base.filter(
            Lancamento.tipo == 'despesa',
            Lancamento.data_pagamento >= data_inicio,
            Lancamento.data_pagamento <= data_fim
        )
    
    # Para despesas de cartão, sempre usar mes_inicial_cartao
    # independente se é futuro ou passado
    if meta.periodo == 'mensal':
        # Para metas mensais, filtrar pelo mês específico
        despesas_cartao = query_base.filter(
            Lancamento.tipo == 'cartao_credito',
            extract('year', Lancamento.mes_inicial_cartao) == data_inicio.year,
            extract('month', Lancamento.mes_inicial_cartao) == data_inicio.month
        )
    else:
        # Para metas trimestrais/anuais, usar range de datas
        despesas_cartao = query_base.filter(
            Lancamento.tipo == 'cartao_credito',
            Lancamento.mes_inicial_cartao >= data_inicio,
            Lancamento.mes_inicial_cartao <= data_fim
        )
    
    # Calcular total gasto
    total_normal = despesas_normais.with_entities(func.sum(Lancamento.valor)).scalar() or 0
    total_cartao = despesas_cartao.with_entities(func.sum(Lancamento.valor)).scalar() or 0
    total_gasto = total_normal + total_cartao
    
    # Calcular percentual
    percentual = (total_gasto / meta.valor_limite * 100) if meta.valor_limite > 0 else 0
    
    # Definir status
    if percentual <= meta.alertar_percentual:
        status = 'ok'
        cor = 'success'
    elif percentual <= 100:
        status = 'alerta'
        cor = 'warning'
    else:
        status = 'excedido'
        cor = 'danger'
    
    return {
        'valor_gasto': total_gasto,
        'valor_limite': meta.valor_limite,
        'percentual': float(percentual),
        'status': status,
        'cor': cor,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'periodo_futuro': periodo_futuro
    }