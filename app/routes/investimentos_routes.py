# app/routes/investimentos_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Conta, SaldoInvestimento, Lancamento
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from sqlalchemy import func, extract, and_
import json

# Criar o Blueprint
investimentos_bp = Blueprint('investimentos', __name__, url_prefix='/investimentos')

@investimentos_bp.route('/')
def dashboard():
    """Dashboard principal de investimentos"""
    # Buscar todas as contas de investimento
    contas_investimento = Conta.query.filter_by(tipo_conta='Investimento').order_by(Conta.nome).all()
    
    # Calcular total atual
    total_investido = sum(conta.saldo_atual for conta in contas_investimento)
    
    # Preparar dados para os gráficos individuais
    dados_contas = {}
    ultimo_registro_geral = None
    
    for conta in contas_investimento:
        historico = SaldoInvestimento.query.filter_by(conta_id=conta.id).order_by(SaldoInvestimento.data_registro).all()
        
        # Preparar dados no formato esperado pelo JavaScript
        labels = []
        valores = []
        
        # Incluir saldo inicial como primeiro ponto
        data_inicial = conta.data_criacao if hasattr(conta, 'data_criacao') else date.today()
        labels.append(data_inicial.strftime('%d/%m/%Y'))
        valores.append(float(conta.saldo_inicial))
        
        # Adicionar histórico
        for registro in historico:
            labels.append(registro.data_registro.strftime('%d/%m/%Y'))
            valores.append(float(registro.saldo))
            
            # Atualizar último registro geral
            if not ultimo_registro_geral or registro.data_registro > ultimo_registro_geral:
                ultimo_registro_geral = registro.data_registro
        
        # Adicionar saldo atual como último ponto se diferente do último registro
        if not historico or (historico and historico[-1].saldo != conta.saldo_atual):
            labels.append(date.today().strftime('%d/%m/%Y'))
            valores.append(float(conta.saldo_atual))
        
        dados_contas[conta.id] = {
            'labels': labels,
            'valores': valores
        }
        
        # Adicionar informações extras à conta
        conta.rendimento = conta.saldo_atual - conta.saldo_inicial
        conta.percentual_rendimento = ((conta.saldo_atual / conta.saldo_inicial - 1) * 100) if conta.saldo_inicial > 0 else 0
        
        # Último registro da conta
        ultimo_reg = historico[-1] if historico else None
        conta.ultimo_registro = ultimo_reg.data_registro if ultimo_reg else None
    
    # Preparar dados consolidados para o gráfico geral
    labels_consolidado = []
    valores_consolidado = []
    
    # Coletar todas as datas únicas
    datas_set = set()
    
    # Adicionar datas iniciais das contas
    for conta in contas_investimento:
        if hasattr(conta, 'data_criacao') and conta.data_criacao:
            datas_set.add(conta.data_criacao.date() if hasattr(conta.data_criacao, 'date') else conta.data_criacao)
    
    # Adicionar datas dos registros
    for conta in contas_investimento:
        historico = SaldoInvestimento.query.filter_by(conta_id=conta.id).all()
        for registro in historico:
            datas_set.add(registro.data_registro)
    
    if datas_set:
        datas_ordenadas = sorted(list(datas_set))
        
        for data in datas_ordenadas:
            total = Decimal('0')
            
            for conta in contas_investimento:
                # Buscar o saldo mais recente até esta data
                registro = SaldoInvestimento.query.filter(
                    and_(
                        SaldoInvestimento.conta_id == conta.id,
                        SaldoInvestimento.data_registro <= data
                    )
                ).order_by(SaldoInvestimento.data_registro.desc()).first()
                
                if registro:
                    total += registro.saldo
                else:
                    # Se não há registro até esta data, usar saldo inicial
                    if hasattr(conta, 'data_criacao'):
                        data_conta = conta.data_criacao.date() if hasattr(conta.data_criacao, 'date') else conta.data_criacao
                        if data_conta <= data:
                            total += conta.saldo_inicial
                    else:
                        total += conta.saldo_inicial
            
            labels_consolidado.append(data.strftime('%d/%m/%Y'))
            valores_consolidado.append(float(total))
    
    # Adicionar ponto atual se necessário
    if contas_investimento and (not valores_consolidado or valores_consolidado[-1] != float(total_investido)):
        labels_consolidado.append(date.today().strftime('%d/%m/%Y'))
        valores_consolidado.append(float(total_investido))
    
    dados_consolidado = {
        'labels': labels_consolidado,
        'valores': valores_consolidado
    }
    
    # Calcular estatísticas gerais
    total_inicial = sum(conta.saldo_inicial for conta in contas_investimento)
    rendimento_total = total_investido - total_inicial
    percentual_total = ((total_investido / total_inicial - 1) * 100) if total_inicial > 0 else 0
    
    return render_template('investimentos.html',
                         contas_investimento=contas_investimento,
                         total_investimentos=total_investido,
                         rendimento_total=rendimento_total,
                         percentual_total=percentual_total,
                         ultimo_registro=ultimo_registro_geral,
                         dados_consolidado=json.dumps(dados_consolidado),
                         dados_contas=json.dumps(dados_contas))

@investimentos_bp.route('/registrar-saldo', methods=['GET', 'POST'])
def registrar_saldo():
    """Registrar novo saldo mensal"""
    if request.method == 'POST':
        conta_id = int(request.form.get('conta_id'))
        data_registro = datetime.strptime(request.form.get('data_registro'), '%Y-%m-%d').date()
        saldo = Decimal(request.form.get('saldo', '0').replace(',', '.'))
        observacoes = request.form.get('observacoes', '')
        
        # Buscar conta
        conta = Conta.query.get_or_404(conta_id)
        
        # Verificar se já existe registro para esta data
        registro_existente = SaldoInvestimento.query.filter_by(
            conta_id=conta_id,
            data_registro=data_registro
        ).first()
        
        if registro_existente:
            flash('Já existe um registro para esta conta nesta data!', 'error')
            return redirect(url_for('investimentos.registrar_saldo'))
        
        # Buscar último saldo registrado
        ultimo_registro = SaldoInvestimento.query.filter_by(conta_id=conta_id).order_by(
            SaldoInvestimento.data_registro.desc()
        ).first()
        
        # Calcular rendimento
        saldo_anterior = ultimo_registro.saldo if ultimo_registro else conta.saldo_inicial
        rendimento_mes = saldo - saldo_anterior
        percentual_mes = ((saldo / saldo_anterior - 1) * 100) if saldo_anterior > 0 else 0
        
        # Criar novo registro
        novo_registro = SaldoInvestimento(
            conta_id=conta_id,
            data_registro=data_registro,
            saldo=saldo,
            rendimento_mes=rendimento_mes,
            percentual_mes=percentual_mes,
            observacoes=observacoes
        )
        
        # Atualizar saldo atual da conta
        conta.saldo_atual = saldo
        
        try:
            db.session.add(novo_registro)
            db.session.commit()
            flash('Saldo registrado com sucesso!', 'success')
            return redirect(url_for('investimentos.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao registrar saldo. Tente novamente.', 'error')
            print(f"Erro: {e}")
    
    # GET - Buscar contas de investimento
    contas = Conta.query.filter_by(tipo_conta='Investimento').order_by(Conta.nome).all()
    
    # Sugerir última data do mês anterior
    hoje = date.today()
    if hoje.day < 15:
        # Se estamos no início do mês, sugerir último dia do mês anterior
        data_sugerida = hoje.replace(day=1) - timedelta(days=1)
    else:
        # Se estamos no final do mês, sugerir último dia do mês atual
        proximo_mes = hoje.replace(day=28) + timedelta(days=4)
        data_sugerida = proximo_mes - timedelta(days=proximo_mes.day)
    
    return render_template('registrar_saldo.html',
                         contas=contas,
                         data_sugerida=data_sugerida,
                         today=hoje)

@investimentos_bp.route('/historico/<int:conta_id>')
def historico_conta(conta_id):
    """Ver histórico detalhado de uma conta"""
    conta = Conta.query.get_or_404(conta_id)
    
    if conta.tipo_conta != 'Investimento':
        flash('Esta conta não é de investimento!', 'error')
        return redirect(url_for('investimentos.dashboard'))
    
    # Buscar histórico
    historico = SaldoInvestimento.query.filter_by(conta_id=conta_id).order_by(
        SaldoInvestimento.data_registro.asc()
    ).all()
    
    # Buscar lançamentos da conta
    lancamentos = Lancamento.query.filter_by(
        conta_id=conta_id,
        status='pago'
    ).order_by(Lancamento.data_pagamento.desc()).limit(20).all()
    
    # Preparar dados para o gráfico
    labels = []
    valores = []
    rendimentos = []
    percentuais = []
    
    # Adicionar ponto inicial
    data_inicial = conta.data_criacao if hasattr(conta, 'data_criacao') else date.today()
    labels.append(data_inicial.strftime('%d/%m/%Y'))
    valores.append(float(conta.saldo_inicial))
    rendimentos.append(0)
    percentuais.append(0)
    
    # Adicionar dados do histórico
    for registro in historico:
        labels.append(registro.data_registro.strftime('%d/%m/%Y'))
        valores.append(float(registro.saldo))
        rendimentos.append(float(registro.rendimento_mes) if registro.rendimento_mes else 0)
        percentuais.append(float(registro.percentual_mes) if registro.percentual_mes else 0)
    
    dados_grafico = {
        'labels': labels,
        'valores': valores,
        'rendimentos': rendimentos,
        'percentuais': percentuais
    }
    
    # Reverter a ordem do histórico para exibição na tabela (mais recente primeiro)
    historico_tabela = list(reversed(historico))
    
    return render_template('historico_conta.html',
                         conta=conta,
                         historico=historico_tabela,
                         lancamentos=lancamentos,
                         dados_grafico=json.dumps(dados_grafico))

@investimentos_bp.route('/api/dados-grafico-consolidado')
def dados_grafico_consolidado():
    """API para retornar dados do gráfico consolidado"""
    # Buscar todas as contas de investimento
    contas = Conta.query.filter_by(tipo_conta='Investimento').all()
    
    # Coletar todas as datas únicas
    datas_set = set()
    
    for conta in contas:
        # Data inicial
        if hasattr(conta, 'data_criacao') and conta.data_criacao:
            datas_set.add(conta.data_criacao.date() if hasattr(conta.data_criacao, 'date') else conta.data_criacao)
        
        # Datas do histórico
        historico = SaldoInvestimento.query.filter_by(conta_id=conta.id).all()
        for registro in historico:
            datas_set.add(registro.data_registro)
    
    # Ordenar datas
    datas_ordenadas = sorted(list(datas_set))
    
    # Construir dados consolidados
    labels = []
    valores = []
    
    for data in datas_ordenadas:
        total = Decimal('0')
        
        for conta in contas:
            # Buscar o saldo mais recente até esta data
            registro = SaldoInvestimento.query.filter(
                and_(
                    SaldoInvestimento.conta_id == conta.id,
                    SaldoInvestimento.data_registro <= data
                )
            ).order_by(SaldoInvestimento.data_registro.desc()).first()
            
            if registro:
                total += registro.saldo
            else:
                # Verificar se a conta já existia nesta data
                if hasattr(conta, 'data_criacao'):
                    data_conta = conta.data_criacao.date() if hasattr(conta.data_criacao, 'date') else conta.data_criacao
                    if data_conta <= data:
                        total += conta.saldo_inicial
                else:
                    total += conta.saldo_inicial
        
        labels.append(data.strftime('%d/%m/%Y'))
        valores.append(float(total))
    
    # Adicionar ponto atual se necessário
    total_atual = sum(conta.saldo_atual for conta in contas)
    if not valores or valores[-1] != float(total_atual):
        labels.append(date.today().strftime('%d/%m/%Y'))
        valores.append(float(total_atual))
    
    return jsonify({
        'labels': labels,
        'valores': valores
    })

@investimentos_bp.route('/editar-registro/<int:id>', methods=['GET', 'POST'])
def editar_registro(id):
    """Editar registro de saldo"""
    registro = SaldoInvestimento.query.get_or_404(id)
    
    if request.method == 'POST':
        novo_saldo = Decimal(request.form.get('saldo', '0').replace(',', '.'))
        registro.observacoes = request.form.get('observacoes', '')
        
        # Recalcular rendimento
        ultimo_registro_anterior = SaldoInvestimento.query.filter(
            and_(
                SaldoInvestimento.conta_id == registro.conta_id,
                SaldoInvestimento.data_registro < registro.data_registro
            )
        ).order_by(SaldoInvestimento.data_registro.desc()).first()
        
        saldo_anterior = ultimo_registro_anterior.saldo if ultimo_registro_anterior else registro.conta.saldo_inicial
        registro.saldo = novo_saldo
        registro.rendimento_mes = novo_saldo - saldo_anterior
        registro.percentual_mes = ((novo_saldo / saldo_anterior - 1) * 100) if saldo_anterior > 0 else 0
        
        # Se for o registro mais recente, atualizar saldo da conta
        registro_mais_recente = SaldoInvestimento.query.filter_by(
            conta_id=registro.conta_id
        ).order_by(SaldoInvestimento.data_registro.desc()).first()
        
        if registro.id == registro_mais_recente.id:
            registro.conta.saldo_atual = novo_saldo
        
        try:
            db.session.commit()
            flash('Registro atualizado com sucesso!', 'success')
            return redirect(url_for('investimentos.historico_conta', conta_id=registro.conta_id))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar registro.', 'error')
            print(f"Erro: {e}")
    
    return jsonify({
        'id': registro.id,
        'saldo': str(registro.saldo),
        'observacoes': registro.observacoes
    })

@investimentos_bp.route('/excluir-registro/<int:id>', methods=['POST'])
def excluir_registro(id):
    """Excluir registro de saldo"""
    registro = SaldoInvestimento.query.get_or_404(id)
    conta_id = registro.conta_id
    
    # Verificar se é o registro mais recente
    registro_mais_recente = SaldoInvestimento.query.filter_by(
        conta_id=conta_id
    ).order_by(SaldoInvestimento.data_registro.desc()).first()
    
    try:
        # Se for o mais recente, atualizar saldo da conta
        if registro.id == registro_mais_recente.id:
            # Buscar o penúltimo registro
            penultimo = SaldoInvestimento.query.filter(
                and_(
                    SaldoInvestimento.conta_id == conta_id,
                    SaldoInvestimento.id != registro.id
                )
            ).order_by(SaldoInvestimento.data_registro.desc()).first()
            
            if penultimo:
                registro.conta.saldo_atual = penultimo.saldo
            else:
                registro.conta.saldo_atual = registro.conta.saldo_inicial
        
        db.session.delete(registro)
        db.session.commit()
        flash('Registro excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir registro.', 'error')
        print(f"Erro: {e}")
    
    return redirect(url_for('investimentos.historico_conta', conta_id=conta_id))