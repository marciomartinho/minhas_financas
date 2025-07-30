# app/routes/lancamentos_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Lancamento, Conta, Categoria, Subcategoria, Cartao
from decimal import Decimal
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

# Criar o Blueprint
lancamentos_bp = Blueprint('lancamentos', __name__)

@lancamentos_bp.route('/lancamentos')
def listar_lancamentos():
    """Página principal de lançamentos"""
    # Buscar contas e categorias de ambos os tipos
    contas = Conta.query.order_by(Conta.nome).all()
    categorias_despesa = Categoria.query.filter_by(tipo='Despesa', ativa=True).order_by(Categoria.nome).all()
    categorias_receita = Categoria.query.filter_by(tipo='Receita', ativa=True).order_by(Categoria.nome).all()
    
    # Buscar lançamentos recentes (últimos 30 dias) - ordenados do mais recente para o mais antigo
    data_limite = date.today() - timedelta(days=30)
    lancamentos = Lancamento.query.filter(
        Lancamento.data_vencimento >= data_limite,
        Lancamento.tipo.in_(['despesa', 'receita'])
    ).order_by(Lancamento.data_criacao.desc()).all()
    
    return render_template('lancamentos.html', 
                         contas=contas, 
                         categorias_despesa=categorias_despesa,
                         categorias_receita=categorias_receita,
                         lancamentos=lancamentos,
                         today=date.today())

@lancamentos_bp.route('/lancamentos/despesa', methods=['POST'])
def criar_despesa():
    """Criar nova despesa"""
    try:
        # Capturar dados do formulário
        descricao = request.form.get('descricao')
        valor = Decimal(request.form.get('valor', '0'))
        conta_id = int(request.form.get('conta_id'))
        categoria_id = int(request.form.get('categoria_id'))
        subcategoria_id = request.form.get('subcategoria_id')
        data_vencimento = datetime.strptime(request.form.get('data_vencimento'), '%Y-%m-%d').date()
        recorrencia = request.form.get('recorrencia', 'unica')
        tag = request.form.get('tag', '').strip()  # Novo campo tag
        
        # Converter subcategoria_id para int ou None
        subcategoria_id = int(subcategoria_id) if subcategoria_id else None
        
        # Validações básicas
        if valor <= 0:
            flash('O valor deve ser maior que zero!', 'error')
            return redirect(url_for('lancamentos.listar_lancamentos'))
        
        # Criar lançamentos baseado na recorrência
        if recorrencia == 'unica':
            # Lançamento único
            lancamento = Lancamento(
                descricao=descricao,
                valor=valor,
                tipo='despesa',
                conta_id=conta_id,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                data_vencimento=data_vencimento,
                status='pendente',
                recorrencia=recorrencia,
                tag=tag if tag else None
            )
            db.session.add(lancamento)
            
        elif recorrencia == 'parcelada':
            # Lançamento parcelado
            num_parcelas = int(request.form.get('num_parcelas', 1))
            if num_parcelas < 2:
                flash('Número de parcelas deve ser maior que 1!', 'error')
                return redirect(url_for('lancamentos.listar_lancamentos'))
            
            # Calcular valor da parcela
            valor_parcela = valor / num_parcelas
            # Arredondar para 2 casas decimais
            valor_parcela = Decimal(str(round(valor_parcela, 2)))
            
            # Calcular diferença para ajustar na primeira parcela
            valor_total_parcelas = valor_parcela * num_parcelas
            diferenca = valor - valor_total_parcelas
            
            # Criar lançamento pai
            lancamento_pai = Lancamento(
                descricao=f"{descricao} (1/{num_parcelas})",
                valor=valor_parcela + diferenca,  # Primeira parcela com ajuste
                tipo='despesa',
                conta_id=conta_id,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                data_vencimento=data_vencimento,
                status='pendente',
                recorrencia=recorrencia,
                numero_parcela=1,
                total_parcelas=num_parcelas,
                tag=tag if tag else None
            )
            db.session.add(lancamento_pai)
            db.session.flush()  # Para obter o ID
            
            # Criar parcelas restantes
            for i in range(2, num_parcelas + 1):
                data_parcela = data_vencimento + relativedelta(months=i-1)
                parcela = Lancamento(
                    descricao=f"{descricao} ({i}/{num_parcelas})",
                    valor=valor_parcela,
                    tipo='despesa',
                    conta_id=conta_id,
                    categoria_id=categoria_id,
                    subcategoria_id=subcategoria_id,
                    data_vencimento=data_parcela,
                    status='pendente',
                    recorrencia=recorrencia,
                    numero_parcela=i,
                    total_parcelas=num_parcelas,
                    lancamento_pai_id=lancamento_pai.id,
                    tag=tag if tag else None
                )
                db.session.add(parcela)
                
        else:
            # Lançamentos recorrentes (mensal, semanal, quinzenal, anual)
            # Definir período e incremento
            if recorrencia == 'mensal':
                incremento = relativedelta(months=1)
                total_lancamentos = 60  # 5 anos
            elif recorrencia == 'anual':
                incremento = relativedelta(years=1)
                total_lancamentos = 5  # 5 anos
            elif recorrencia == 'semanal':
                incremento = timedelta(weeks=1)
                total_lancamentos = 260  # ~5 anos
            elif recorrencia == 'quinzenal':
                incremento = timedelta(weeks=2)
                total_lancamentos = 130  # ~5 anos
            else:
                flash('Tipo de recorrência inválido!', 'error')
                return redirect(url_for('lancamentos.listar_lancamentos'))
            
            # Criar primeiro lançamento
            lancamento_pai = Lancamento(
                descricao=descricao,
                valor=valor,
                tipo='despesa',
                conta_id=conta_id,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                data_vencimento=data_vencimento,
                status='pendente',
                recorrencia=recorrencia,
                tag=tag if tag else None
            )
            db.session.add(lancamento_pai)
            db.session.flush()
            
            # Criar lançamentos futuros
            data_atual = data_vencimento
            for i in range(1, total_lancamentos):
                data_atual = data_atual + incremento
                lancamento = Lancamento(
                    descricao=descricao,
                    valor=valor,
                    tipo='despesa',
                    conta_id=conta_id,
                    categoria_id=categoria_id,
                    subcategoria_id=subcategoria_id,
                    data_vencimento=data_atual,
                    status='pendente',
                    recorrencia=recorrencia,
                    lancamento_pai_id=lancamento_pai.id,
                    tag=tag if tag else None
                )
                db.session.add(lancamento)
        
        db.session.commit()
        flash('Despesa cadastrada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar despesa: {e}")
        flash('Erro ao cadastrar despesa. Tente novamente.', 'error')
    
    return redirect(url_for('lancamentos.listar_lancamentos'))

@lancamentos_bp.route('/lancamentos/receita', methods=['POST'])
def criar_receita():
    """Criar nova receita"""
    try:
        # Capturar dados do formulário (mesma estrutura da despesa)
        descricao = request.form.get('descricao')
        valor = Decimal(request.form.get('valor', '0'))
        conta_id = int(request.form.get('conta_id'))
        categoria_id = int(request.form.get('categoria_id'))
        subcategoria_id = request.form.get('subcategoria_id')
        data_vencimento = datetime.strptime(request.form.get('data_vencimento'), '%Y-%m-%d').date()
        recorrencia = request.form.get('recorrencia', 'unica')
        tag = request.form.get('tag', '').strip()
        
        # Converter subcategoria_id para int ou None
        subcategoria_id = int(subcategoria_id) if subcategoria_id else None
        
        # Validações básicas
        if valor <= 0:
            flash('O valor deve ser maior que zero!', 'error')
            return redirect(url_for('lancamentos.listar_lancamentos'))
        
        # Criar lançamentos baseado na recorrência (mesma lógica da despesa)
        if recorrencia == 'unica':
            # Lançamento único
            lancamento = Lancamento(
                descricao=descricao,
                valor=valor,
                tipo='receita',
                conta_id=conta_id,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                data_vencimento=data_vencimento,
                status='pendente',
                recorrencia=recorrencia,
                tag=tag if tag else None
            )
            db.session.add(lancamento)
            
        elif recorrencia == 'parcelada':
            # Receita parcelada (raro, mas possível)
            num_parcelas = int(request.form.get('num_parcelas', 1))
            if num_parcelas < 2:
                flash('Número de parcelas deve ser maior que 1!', 'error')
                return redirect(url_for('lancamentos.listar_lancamentos'))
            
            # Calcular valor da parcela
            valor_parcela = valor / num_parcelas
            valor_parcela = Decimal(str(round(valor_parcela, 2)))
            
            # Calcular diferença para ajustar na primeira parcela
            valor_total_parcelas = valor_parcela * num_parcelas
            diferenca = valor - valor_total_parcelas
            
            # Criar lançamento pai
            lancamento_pai = Lancamento(
                descricao=f"{descricao} (1/{num_parcelas})",
                valor=valor_parcela + diferenca,
                tipo='receita',
                conta_id=conta_id,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                data_vencimento=data_vencimento,
                status='pendente',
                recorrencia=recorrencia,
                numero_parcela=1,
                total_parcelas=num_parcelas,
                tag=tag if tag else None
            )
            db.session.add(lancamento_pai)
            db.session.flush()
            
            # Criar parcelas restantes
            for i in range(2, num_parcelas + 1):
                data_parcela = data_vencimento + relativedelta(months=i-1)
                parcela = Lancamento(
                    descricao=f"{descricao} ({i}/{num_parcelas})",
                    valor=valor_parcela,
                    tipo='receita',
                    conta_id=conta_id,
                    categoria_id=categoria_id,
                    subcategoria_id=subcategoria_id,
                    data_vencimento=data_parcela,
                    status='pendente',
                    recorrencia=recorrencia,
                    numero_parcela=i,
                    total_parcelas=num_parcelas,
                    lancamento_pai_id=lancamento_pai.id,
                    tag=tag if tag else None
                )
                db.session.add(parcela)
                
        else:
            # Lançamentos recorrentes
            if recorrencia == 'mensal':
                incremento = relativedelta(months=1)
                total_lancamentos = 60
            elif recorrencia == 'anual':
                incremento = relativedelta(years=1)
                total_lancamentos = 5
            elif recorrencia == 'semanal':
                incremento = timedelta(weeks=1)
                total_lancamentos = 260
            elif recorrencia == 'quinzenal':
                incremento = timedelta(weeks=2)
                total_lancamentos = 130
            else:
                flash('Tipo de recorrência inválido!', 'error')
                return redirect(url_for('lancamentos.listar_lancamentos'))
            
            # Criar primeiro lançamento
            lancamento_pai = Lancamento(
                descricao=descricao,
                valor=valor,
                tipo='receita',
                conta_id=conta_id,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                data_vencimento=data_vencimento,
                status='pendente',
                recorrencia=recorrencia,
                tag=tag if tag else None
            )
            db.session.add(lancamento_pai)
            db.session.flush()
            
            # Criar lançamentos futuros
            data_atual = data_vencimento
            for i in range(1, total_lancamentos):
                data_atual = data_atual + incremento
                lancamento = Lancamento(
                    descricao=descricao,
                    valor=valor,
                    tipo='receita',
                    conta_id=conta_id,
                    categoria_id=categoria_id,
                    subcategoria_id=subcategoria_id,
                    data_vencimento=data_atual,
                    status='pendente',
                    recorrencia=recorrencia,
                    lancamento_pai_id=lancamento_pai.id,
                    tag=tag if tag else None
                )
                db.session.add(lancamento)
        
        db.session.commit()
        flash('Receita cadastrada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar receita: {e}")
        flash('Erro ao cadastrar receita. Tente novamente.', 'error')
    
    return redirect(url_for('lancamentos.listar_lancamentos'))

@lancamentos_bp.route('/lancamentos/<int:id>/excluir', methods=['POST'])
def excluir_lancamento(id):
    """Excluir lançamento"""
    try:
        lancamento = Lancamento.query.get_or_404(id)
        
        # Se for um lançamento pai com recorrência, perguntar se quer excluir todos
        excluir_todos = request.form.get('excluir_todos') == 'true'
        
        if excluir_todos and lancamento.recorrencia != 'unica':
            # Excluir este e todos os futuros
            if lancamento.lancamento_pai_id:
                # É uma parcela/recorrência filha
                lancamentos_excluir = Lancamento.query.filter(
                    Lancamento.lancamento_pai_id == lancamento.lancamento_pai_id,
                    Lancamento.data_vencimento >= lancamento.data_vencimento
                ).all()
                # Incluir o próprio lançamento
                lancamentos_excluir.append(lancamento)
            else:
                # É o lançamento pai
                lancamentos_excluir = Lancamento.query.filter(
                    db.or_(
                        Lancamento.id == lancamento.id,
                        db.and_(
                            Lancamento.lancamento_pai_id == lancamento.id,
                            Lancamento.data_vencimento >= lancamento.data_vencimento
                        )
                    )
                ).all()
            
            for lanc in lancamentos_excluir:
                db.session.delete(lanc)
                
            flash(f'{len(lancamentos_excluir)} lançamentos excluídos com sucesso!', 'success')
        else:
            # Excluir apenas este lançamento
            db.session.delete(lancamento)
            flash('Lançamento excluído com sucesso!', 'success')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir lançamento: {e}")
        flash('Erro ao excluir lançamento.', 'error')
    
    return redirect(url_for('lancamentos.listar_lancamentos'))

# API para buscar subcategorias
@lancamentos_bp.route('/api/categorias/<int:categoria_id>/subcategorias')
def get_subcategorias(categoria_id):
    """Retorna subcategorias de uma categoria"""
    subcategorias = Subcategoria.query.filter_by(
        categoria_id=categoria_id,
        ativa=True
    ).order_by(Subcategoria.nome).all()
    
    return jsonify([{
        'id': s.id,
        'nome': s.nome
    } for s in subcategorias])