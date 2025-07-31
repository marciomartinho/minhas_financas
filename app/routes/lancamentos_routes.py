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
    cartoes = Cartao.query.filter_by(ativo=True).order_by(Cartao.nome).all()
    
    # Buscar lançamentos recentes (últimos 30 dias) - ordenados do mais recente para o mais antigo
    data_limite = date.today() - timedelta(days=30)
    lancamentos = Lancamento.query.filter(
        Lancamento.data_vencimento >= data_limite
    ).order_by(Lancamento.data_criacao.desc()).all()
    
    return render_template('lancamentos.html', 
                         contas=contas, 
                         categorias_despesa=categorias_despesa,
                         categorias_receita=categorias_receita,
                         cartoes=cartoes,
                         lancamentos=lancamentos,
                         today=date.today())

@lancamentos_bp.route('/lancamentos/cartao', methods=['POST'])
def criar_despesa_cartao():
    """Criar nova despesa no cartão de crédito"""
    try:
        # Capturar dados do formulário
        descricao = request.form.get('descricao')
        valor = Decimal(request.form.get('valor', '0'))
        cartao_id = int(request.form.get('cartao_id'))
        categoria_id = int(request.form.get('categoria_id'))
        subcategoria_id = request.form.get('subcategoria_id')
        data_vencimento = datetime.strptime(request.form.get('data_vencimento'), '%Y-%m-%d').date()
        mes_inicial = datetime.strptime(request.form.get('mes_inicial'), '%Y-%m-%d').date()
        recorrencia = request.form.get('recorrencia', 'unica')
        tag = request.form.get('tag', '').strip()
        
        # Converter subcategoria_id para int ou None
        subcategoria_id = int(subcategoria_id) if subcategoria_id else None
        
        # Validações básicas
        if valor <= 0:
            flash('O valor deve ser maior que zero!', 'error')
            return redirect(url_for('lancamentos.listar_lancamentos'))
        
        # Buscar cartão
        cartao = Cartao.query.get(cartao_id)
        if not cartao:
            flash('Cartão inválido!', 'error')
            return redirect(url_for('lancamentos.listar_lancamentos'))
        
        # Criar lançamentos baseado na recorrência
        if recorrencia == 'unica':
            # Lançamento único
            lancamento = Lancamento(
                descricao=descricao,
                valor=valor,
                tipo='cartao_credito',
                conta_id=cartao.conta_id,  # Conta vinculada ao cartão
                cartao_id=cartao_id,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                data_vencimento=data_vencimento,
                mes_inicial_cartao=mes_inicial,
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
            valor_parcela = Decimal(str(round(valor_parcela, 2)))
            
            # Calcular diferença para ajustar na primeira parcela
            valor_total_parcelas = valor_parcela * num_parcelas
            diferenca = valor - valor_total_parcelas
            
            # Criar lançamento pai
            lancamento_pai = Lancamento(
                descricao=f"{descricao} (1/{num_parcelas})",
                valor=valor_parcela + diferenca,
                tipo='cartao_credito',
                conta_id=cartao.conta_id,
                cartao_id=cartao_id,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                data_vencimento=data_vencimento,
                mes_inicial_cartao=mes_inicial,
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
                mes_parcela = mes_inicial + relativedelta(months=i-1)
                parcela = Lancamento(
                    descricao=f"{descricao} ({i}/{num_parcelas})",
                    valor=valor_parcela,
                    tipo='cartao_credito',
                    conta_id=cartao.conta_id,
                    cartao_id=cartao_id,
                    categoria_id=categoria_id,
                    subcategoria_id=subcategoria_id,
                    data_vencimento=data_parcela,
                    mes_inicial_cartao=mes_parcela,
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
                tipo='cartao_credito',
                conta_id=cartao.conta_id,
                cartao_id=cartao_id,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                data_vencimento=data_vencimento,
                mes_inicial_cartao=mes_inicial,
                status='pendente',
                recorrencia=recorrencia,
                tag=tag if tag else None
            )
            db.session.add(lancamento_pai)
            db.session.flush()
            
            # Criar lançamentos futuros
            data_atual = data_vencimento
            mes_atual = mes_inicial
            for i in range(1, total_lancamentos):
                # CORREÇÃO: Incrementar ambas as datas
                data_atual = data_atual + incremento
                mes_atual = mes_atual + incremento
                lancamento = Lancamento(
                    descricao=descricao,
                    valor=valor,
                    tipo='cartao_credito',
                    conta_id=cartao.conta_id,
                    cartao_id=cartao_id,
                    categoria_id=categoria_id,
                    subcategoria_id=subcategoria_id,
                    data_vencimento=data_atual,
                    mes_inicial_cartao=mes_atual,
                    status='pendente',
                    recorrencia=recorrencia,
                    lancamento_pai_id=lancamento_pai.id,
                    tag=tag if tag else None
                )
                db.session.add(lancamento)
        
        db.session.commit()
        flash('Despesa no cartão cadastrada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar despesa no cartão: {e}")
        flash('Erro ao cadastrar despesa no cartão. Tente novamente.', 'error')
    
    return redirect(url_for('lancamentos.listar_lancamentos'))

@lancamentos_bp.route('/lancamentos/transferencia', methods=['POST'])
def criar_transferencia():
    """Criar nova transferência entre contas"""
    try:
        # Capturar dados do formulário
        descricao = request.form.get('descricao')
        valor = Decimal(request.form.get('valor', '0'))
        conta_origem_id = int(request.form.get('conta_origem_id'))
        conta_destino_id = int(request.form.get('conta_destino_id'))
        data_vencimento = datetime.strptime(request.form.get('data_vencimento'), '%Y-%m-%d').date()
        
        # Validações básicas
        if valor <= 0:
            flash('O valor deve ser maior que zero!', 'error')
            return redirect(url_for('lancamentos.listar_lancamentos'))
        
        if conta_origem_id == conta_destino_id:
            flash('A conta de origem e destino devem ser diferentes!', 'error')
            return redirect(url_for('lancamentos.listar_lancamentos'))
        
        # Buscar contas
        conta_origem = Conta.query.get(conta_origem_id)
        conta_destino = Conta.query.get(conta_destino_id)
        
        if not conta_origem or not conta_destino:
            flash('Conta inválida selecionada!', 'error')
            return redirect(url_for('lancamentos.listar_lancamentos'))
        
        # Verificar saldo da conta de origem
        if conta_origem.saldo_atual < valor:
            flash(f'Saldo insuficiente na conta {conta_origem.nome}!', 'error')
            return redirect(url_for('lancamentos.listar_lancamentos'))
        
        # Buscar ou criar categoria "Transferência"
        categoria_transferencia = Categoria.query.filter_by(nome='Transferência').first()
        if not categoria_transferencia:
            # Criar categoria se não existir
            categoria_transferencia = Categoria(
                nome='Transferência',
                tipo='Despesa',
                icone='swap_horiz',
                cor='#17a2b8',
                ativa=True
            )
            db.session.add(categoria_transferencia)
            db.session.flush()
        
        # Criar lançamento de saída (despesa na conta origem)
        lancamento_saida = Lancamento(
            descricao=f"{descricao} - para {conta_destino.nome}",
            valor=valor,
            tipo='transferencia',
            conta_id=conta_origem_id,
            conta_destino_id=conta_destino_id,
            categoria_id=categoria_transferencia.id,
            data_vencimento=data_vencimento,
            data_pagamento=data_vencimento,  # Transferência é realizada imediatamente
            status='pago',  # Status sempre pago para transferências
            recorrencia='unica',
            tag='Transferência'
        )
        
        # Criar lançamento de entrada (receita na conta destino)
        lancamento_entrada = Lancamento(
            descricao=f"{descricao} - de {conta_origem.nome}",
            valor=valor,
            tipo='transferencia',
            conta_id=conta_destino_id,
            conta_destino_id=conta_origem_id,  # Inverter para rastreabilidade
            categoria_id=categoria_transferencia.id,
            data_vencimento=data_vencimento,
            data_pagamento=data_vencimento,
            status='pago',
            recorrencia='unica',
            tag='Transferência'
        )
        
        # Atualizar saldos das contas
        conta_origem.saldo_atual -= valor
        conta_destino.saldo_atual += valor
        
        # Salvar tudo
        db.session.add(lancamento_saida)
        db.session.add(lancamento_entrada)
        db.session.commit()
        
        flash(f'Transferência de R$ {valor:,.2f} realizada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar transferência: {e}")
        flash('Erro ao realizar transferência. Tente novamente.', 'error')
    
    return redirect(url_for('lancamentos.listar_lancamentos'))

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
        
        # Se o lançamento estava pago, reverter o saldo antes de excluir
        if lancamento.status == 'pago':
            conta = lancamento.conta
            if lancamento.tipo == 'receita':
                conta.saldo_atual -= lancamento.valor
            elif lancamento.tipo in ['despesa', 'cartao_credito']:
                conta.saldo_atual += lancamento.valor
            elif lancamento.tipo == 'transferencia':
                # Para transferências, reverter ambas as contas
                if lancamento.conta_destino_id:
                    # Este é o lançamento de saída
                    conta.saldo_atual += lancamento.valor
                    conta_destino = Conta.query.get(lancamento.conta_destino_id)
                    if conta_destino:
                        conta_destino.saldo_atual -= lancamento.valor
                else:
                    # Este é o lançamento de entrada - buscar o par
                    lancamento_par = Lancamento.query.filter_by(
                        tipo='transferencia',
                        data_vencimento=lancamento.data_vencimento,
                        valor=lancamento.valor,
                        conta_destino_id=lancamento.conta_id
                    ).first()
                    if lancamento_par:
                        db.session.delete(lancamento_par)
                        conta_origem = Conta.query.get(lancamento_par.conta_id)
                        if conta_origem:
                            conta_origem.saldo_atual += lancamento.valor
                    conta.saldo_atual -= lancamento.valor
        
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
            
            # Reverter saldo de todos os lançamentos pagos que serão excluídos
            for lanc in lancamentos_excluir:
                if lanc.status == 'pago' and lanc.id != lancamento.id:  # Já revertemos o principal
                    conta = lanc.conta
                    if lanc.tipo == 'receita':
                        conta.saldo_atual -= lanc.valor
                    else:  # despesa ou cartao_credito
                        conta.saldo_atual += lanc.valor
                db.session.delete(lanc)
                
            flash(f'{len(lancamentos_excluir)} lançamentos excluídos com sucesso!', 'success')
        else:
            # Excluir apenas este lançamento
            db.session.delete(lancamento)
            flash('Lançamento excluído com sucesso!', 'success')
        
        db.session.commit()
        
        # Redirecionar para home se vier de lá
        if request.form.get('from_home') == 'true':
            mes = request.form.get('mes', date.today().month)
            ano = request.form.get('ano', date.today().year)
            return redirect(url_for('main.home', mes=mes, ano=ano))
        
        # Redirecionar para extrato do cartão se vier de lá
        if request.form.get('from_extrato') == 'true':
            return redirect(url_for('main.extrato_cartao'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir lançamento: {e}")
        flash('Erro ao excluir lançamento.', 'error')
    
    return redirect(url_for('lancamentos.listar_lancamentos'))

@lancamentos_bp.route('/lancamentos/<int:id>/pagar', methods=['POST'])
def marcar_como_pago(id):
    """Marcar lançamento como pago/pendente e atualizar saldo da conta"""
    try:
        lancamento = Lancamento.query.get_or_404(id)
        conta = lancamento.conta
        
        if lancamento.status == 'pago':
            # Desmarcar como pago - reverter o saldo
            lancamento.status = 'pendente'
            lancamento.data_pagamento = None
            
            # Reverter o saldo
            if lancamento.tipo == 'receita':
                conta.saldo_atual -= lancamento.valor
            else:  # despesa ou cartao_credito
                conta.saldo_atual += lancamento.valor
                
            flash('Lançamento marcado como pendente!', 'info')
        else:
            # Marcar como pago - atualizar o saldo
            lancamento.status = 'pago'
            lancamento.data_pagamento = date.today()
            
            # Atualizar o saldo
            if lancamento.tipo == 'receita':
                conta.saldo_atual += lancamento.valor
            else:  # despesa ou cartao_credito
                conta.saldo_atual -= lancamento.valor
                
            flash('Lançamento marcado como pago!', 'success')
        
        db.session.commit()
        
        # Redirecionar para home se vier de lá
        if request.form.get('from_home') == 'true':
            mes = request.form.get('mes', date.today().month)
            ano = request.form.get('ano', date.today().year)
            return redirect(url_for('main.home', mes=mes, ano=ano))
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar status: {e}")
        flash('Erro ao atualizar status do lançamento.', 'error')
    
    return redirect(url_for('lancamentos.listar_lancamentos'))

@lancamentos_bp.route('/lancamentos/<int:id>/editar', methods=['GET', 'POST'])
def editar_lancamento(id):
    """Editar lançamento"""
    lancamento = Lancamento.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Se o lançamento está pago e o valor mudou, ajustar o saldo
            if lancamento.status == 'pago':
                valor_antigo = lancamento.valor
                valor_novo = Decimal(request.form.get('valor', '0'))
                
                if valor_antigo != valor_novo:
                    conta = lancamento.conta
                    diferenca = valor_novo - valor_antigo
                    
                    if lancamento.tipo == 'receita':
                        conta.saldo_atual += diferenca
                    else:  # despesa ou cartao_credito
                        conta.saldo_atual -= diferenca
            
            # Atualizar dados
            lancamento.descricao = request.form.get('descricao')
            lancamento.valor = Decimal(request.form.get('valor', '0'))
            
            # Para despesas do cartão, não atualizar conta_id
            if lancamento.tipo != 'cartao_credito':
                conta_id = request.form.get('conta_id')
                if conta_id:
                    lancamento.conta_id = int(conta_id)
            
            lancamento.categoria_id = int(request.form.get('categoria_id'))
            subcategoria_id = request.form.get('subcategoria_id')
            lancamento.subcategoria_id = int(subcategoria_id) if subcategoria_id else None
            lancamento.data_vencimento = datetime.strptime(request.form.get('data_vencimento'), '%Y-%m-%d').date()
            lancamento.tag = request.form.get('tag', '').strip() or None
            
            # Se for cartão de crédito, atualizar mês inicial
            if lancamento.tipo == 'cartao_credito' and request.form.get('mes_inicial'):
                lancamento.mes_inicial_cartao = datetime.strptime(request.form.get('mes_inicial'), '%Y-%m-%d').date()
            
            # Se marcar para editar todos os futuros
            editar_todos = request.form.get('editar_todos') == 'true'
            
            if editar_todos and lancamento.recorrencia != 'unica':
                # Buscar lançamentos futuros relacionados
                if lancamento.lancamento_pai_id:
                    lancamentos_editar = Lancamento.query.filter(
                        Lancamento.lancamento_pai_id == lancamento.lancamento_pai_id,
                        Lancamento.data_vencimento >= lancamento.data_vencimento
                    ).all()
                else:
                    lancamentos_editar = Lancamento.query.filter(
                        Lancamento.lancamento_pai_id == lancamento.id,
                        Lancamento.data_vencimento >= lancamento.data_vencimento
                    ).all()
                
                # Atualizar todos
                for lanc in lancamentos_editar:
                    lanc.valor = lancamento.valor
                    if lancamento.tipo != 'cartao_credito':
                        lanc.conta_id = lancamento.conta_id
                    lanc.categoria_id = lancamento.categoria_id
                    lanc.subcategoria_id = lancamento.subcategoria_id
                    lanc.tag = lancamento.tag
                    # NÃO atualizar mes_inicial_cartao para manter as datas originais
            
            db.session.commit()
            flash('Lançamento atualizado com sucesso!', 'success')
            
            # Redirecionar para home se vier de lá
            if request.form.get('from_home') == 'true':
                mes = request.form.get('mes', date.today().month)
                ano = request.form.get('ano', date.today().year)
                return redirect(url_for('main.home', mes=mes, ano=ano))
            
            # Redirecionar para extrato do cartão se vier de lá
            if request.form.get('from_extrato') == 'true':
                return redirect(url_for('main.extrato_cartao'))
            
            return redirect(url_for('lancamentos.listar_lancamentos'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao editar lançamento: {e}")
            flash('Erro ao atualizar lançamento.', 'error')
    
    # GET - Retornar dados em JSON para o modal
    return jsonify({
        'id': lancamento.id,
        'descricao': lancamento.descricao,
        'valor': str(lancamento.valor),
        'tipo': lancamento.tipo,
        'conta_id': lancamento.conta_id,
        'cartao_id': lancamento.cartao_id,
        'categoria_id': lancamento.categoria_id,
        'subcategoria_id': lancamento.subcategoria_id,
        'data_vencimento': lancamento.data_vencimento.strftime('%Y-%m-%d'),
        'mes_inicial_cartao': lancamento.mes_inicial_cartao.strftime('%Y-%m-%d') if lancamento.mes_inicial_cartao else None,
        'tag': lancamento.tag or '',
        'recorrencia': lancamento.recorrencia
    })

@lancamentos_bp.route('/lancamentos/pagar-fatura', methods=['POST'])
def pagar_fatura_cartao():
    """Marcar fatura do cartão como paga"""
    try:
        cartao_id = int(request.form.get('cartao_id'))
        mes = int(request.form.get('mes'))
        ano = int(request.form.get('ano'))
        valor_fatura = Decimal(request.form.get('valor_fatura', '0'))
        
        # Buscar o cartão
        cartao = Cartao.query.get(cartao_id)
        if not cartao:
            flash('Cartão não encontrado!', 'error')
            return redirect(url_for('main.home', mes=mes, ano=ano))
        
        # Buscar ou criar categoria para pagamento de fatura
        categoria_fatura = Categoria.query.filter_by(nome='Pagamento de Fatura').first()
        if not categoria_fatura:
            categoria_fatura = Categoria(
                nome='Pagamento de Fatura',
                tipo='Despesa',
                icone='credit_score',
                cor='#6f42c1',
                ativa=True
            )
            db.session.add(categoria_fatura)
            db.session.flush()
        
        # Calcular data de vencimento
        try:
            data_vencimento = date(ano, mes, cartao.dia_vencimento)
        except ValueError:
            # Se o dia não existir no mês, usar o último dia
            from calendar import monthrange
            ultimo_dia = monthrange(ano, mes)[1]
            data_vencimento = date(ano, mes, ultimo_dia)
        
        # Criar lançamento de pagamento
        pagamento = Lancamento(
            descricao=f'Pagamento Fatura {cartao.nome}',
            valor=valor_fatura,
            tipo='despesa',
            conta_id=cartao.conta_id,
            categoria_id=categoria_fatura.id,
            data_vencimento=data_vencimento,
            data_pagamento=date.today(),
            status='pago',
            recorrencia='unica',
            tag='Fatura Cartão'
        )
        
        # Atualizar saldo da conta
        conta = cartao.conta
        conta.saldo_atual -= valor_fatura
        
        db.session.add(pagamento)
        db.session.commit()
        
        flash(f'Fatura do {cartao.nome} paga com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao pagar fatura: {e}")
        flash('Erro ao registrar pagamento da fatura.', 'error')
    
    return redirect(url_for('main.home', mes=mes, ano=ano))

# API para buscar subcategorias
@lancamentos_bp.route('/api/categorias/<int:categoria_id>/subcategorias')
def obter_subcategorias(categoria_id):
    """Retorna subcategorias de uma categoria"""
    subcategorias = Subcategoria.query.filter_by(
        categoria_id=categoria_id,
        ativa=True
    ).order_by(Subcategoria.nome).all()
    
    return jsonify([{
        'id': s.id,
        'nome': s.nome,
        'descricao': s.descricao
    } for s in subcategorias])