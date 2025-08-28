# app/routes/main_routes.py

from flask import Blueprint, render_template, request, Response, flash, redirect, url_for, current_app
from app.models import db, Conta, Lancamento, Cartao, Categoria, Subcategoria
from datetime import datetime, date, timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, extract, and_
from collections import defaultdict
import io
import xlsxwriter

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
    
    # IMPORTANTE: Buscar IDs das contas correntes para filtrar
    ids_contas_corrente = [conta.id for conta in contas_corrente]
    ids_contas_investimento = [conta.id for conta in contas_investimento]
    
    # Buscar lançamentos do mês - APENAS DE CONTAS CORRENTES
    # Para receitas: apenas tipo = 'receita' E conta_id em contas correntes
    receitas = Lancamento.query.filter(
        Lancamento.tipo == 'receita',
        Lancamento.conta_id.in_(ids_contas_corrente),  # FILTRO ADICIONADO
        Lancamento.data_vencimento >= primeiro_dia,
        Lancamento.data_vencimento <= ultimo_dia
    ).order_by(Lancamento.data_vencimento).all()
    
    # Para despesas: apenas tipo = 'despesa' E conta_id em contas correntes
    despesas_query = Lancamento.query.filter(
        Lancamento.tipo == 'despesa',
        Lancamento.conta_id.in_(ids_contas_corrente),  # FILTRO ADICIONADO
        Lancamento.data_vencimento >= primeiro_dia,
        Lancamento.data_vencimento <= ultimo_dia
    ).order_by(Lancamento.data_vencimento).all()
    
    # Processar faturas de cartão (mantém lógica existente - cartões já são de contas correntes)
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
    
    # Calcular totais de receitas e despesas PENDENTES para o resultado do mês
    total_receitas_pendentes = sum(lancamento.valor for lancamento in receitas if lancamento.status == 'pendente')
    total_despesas_pendentes = sum(lancamento.valor for lancamento in despesas if lancamento.status == 'pendente' and lancamento.tipo != 'fatura_cartao')
    
    # Calcular total das faturas de cartão não pagas
    total_faturas_pendentes = sum(lancamento.valor for lancamento in despesas if lancamento.tipo == 'fatura_cartao' and lancamento.status == 'pendente')
    
    # ========== ANÁLISE POR CATEGORIAS ==========
    
    # Estrutura para armazenar análise
    analise_categorias = {
        'despesas': [],
        'investimentos': [],
        'receitas': [],
        'total_despesas': 0,
        'total_investimentos': 0,
        'total_receitas': 0,
        'economia_mes': 0
    }
    
    # 1. ANÁLISE DE DESPESAS (excluindo investimentos)
    # Buscar apenas despesas normais (NÃO incluir cartão_credito aqui)
    despesas_normais = Lancamento.query.filter(
        Lancamento.tipo == 'despesa',  # Apenas despesas, sem cartão_credito
        Lancamento.conta_id.in_(ids_contas_corrente),
        Lancamento.data_vencimento >= primeiro_dia,
        Lancamento.data_vencimento <= ultimo_dia,
        Lancamento.status != 'cancelado'
    ).all()
    
    # Agrupar por categoria e subcategoria
    despesas_por_categoria = defaultdict(lambda: {
        'nome': '',
        'total': 0,
        'subcategorias': defaultdict(float),
        'cor': '#6c757d',
        'icone': 'category'
    })
    
    # Adicionar despesas normais
    for despesa in despesas_normais:
        if despesa.categoria:
            cat_id = despesa.categoria_id
            despesas_por_categoria[cat_id]['nome'] = despesa.categoria.nome
            despesas_por_categoria[cat_id]['cor'] = despesa.categoria.cor or '#6c757d'
            despesas_por_categoria[cat_id]['icone'] = despesa.categoria.icone or 'category'
            despesas_por_categoria[cat_id]['total'] += float(despesa.valor)
            
            if despesa.subcategoria:
                despesas_por_categoria[cat_id]['subcategorias'][despesa.subcategoria.nome] += float(despesa.valor)
            else:
                despesas_por_categoria[cat_id]['subcategorias']['Sem subcategoria'] += float(despesa.valor)
    
    # Adicionar APENAS as despesas do cartão que fazem parte das faturas deste mês
    for fatura in faturas_cartao:
        # Apenas processar despesas de faturas não canceladas
        if hasattr(fatura, 'despesas_cartao'):
            for despesa_cartao in fatura.despesas_cartao:
                if despesa_cartao.categoria:
                    cat_id = despesa_cartao.categoria_id
                    despesas_por_categoria[cat_id]['nome'] = despesa_cartao.categoria.nome
                    despesas_por_categoria[cat_id]['cor'] = despesa_cartao.categoria.cor or '#6c757d'
                    despesas_por_categoria[cat_id]['icone'] = despesa_cartao.categoria.icone or 'category'
                    despesas_por_categoria[cat_id]['total'] += float(despesa_cartao.valor)
                    
                    if despesa_cartao.subcategoria:
                        despesas_por_categoria[cat_id]['subcategorias'][despesa_cartao.subcategoria.nome] += float(despesa_cartao.valor)
                    else:
                        despesas_por_categoria[cat_id]['subcategorias']['Sem subcategoria'] += float(despesa_cartao.valor)
    
    # Converter para lista e ordenar
    for cat_id, dados in despesas_por_categoria.items():
        subcategorias_lista = []
        for sub_nome, sub_valor in dados['subcategorias'].items():
            subcategorias_lista.append({
                'nome': sub_nome,
                'valor': sub_valor
            })
        subcategorias_lista.sort(key=lambda x: x['valor'], reverse=True)
        
        analise_categorias['despesas'].append({
            'id': cat_id,
            'nome': dados['nome'],
            'cor': dados['cor'],
            'icone': dados['icone'],
            'total': dados['total'],
            'subcategorias': subcategorias_lista
        })
    
    analise_categorias['despesas'].sort(key=lambda x: x['total'], reverse=True)
    analise_categorias['total_despesas'] = sum(cat['total'] for cat in analise_categorias['despesas'])
    
    # 2. ANÁLISE DE INVESTIMENTOS
    # Buscar lançamentos de investimento
    lancamentos_investimento = Lancamento.query.filter(
        Lancamento.tipo == 'transferencia',
        Lancamento.conta_destino_id.in_(ids_contas_investimento),
        Lancamento.data_vencimento >= primeiro_dia,
        Lancamento.data_vencimento <= ultimo_dia,
        Lancamento.status != 'cancelado'
    ).all()
    
    investimentos_por_conta = defaultdict(float)
    for lanc in lancamentos_investimento:
        if lanc.conta_destino:
            investimentos_por_conta[lanc.conta_destino.nome] += float(lanc.valor)
    
    for conta_nome, valor in investimentos_por_conta.items():
        analise_categorias['investimentos'].append({
            'nome': conta_nome,
            'valor': valor
        })
    
    analise_categorias['investimentos'].sort(key=lambda x: x['valor'], reverse=True)
    analise_categorias['total_investimentos'] = sum(inv['valor'] for inv in analise_categorias['investimentos'])
    
    # 3. ANÁLISE DE RECEITAS
    receitas_por_categoria = defaultdict(lambda: {
        'nome': '',
        'total': 0,
        'subcategorias': defaultdict(float),
        'cor': '#28a745',
        'icone': 'attach_money'
    })
    
    for receita in receitas:
        if receita.categoria:
            cat_id = receita.categoria_id
            receitas_por_categoria[cat_id]['nome'] = receita.categoria.nome
            receitas_por_categoria[cat_id]['cor'] = receita.categoria.cor or '#28a745'
            receitas_por_categoria[cat_id]['icone'] = receita.categoria.icone or 'attach_money'
            receitas_por_categoria[cat_id]['total'] += float(receita.valor)
            
            if receita.subcategoria:
                receitas_por_categoria[cat_id]['subcategorias'][receita.subcategoria.nome] += float(receita.valor)
            else:
                receitas_por_categoria[cat_id]['subcategorias']['Sem subcategoria'] += float(receita.valor)
    
    # Converter para lista e ordenar
    for cat_id, dados in receitas_por_categoria.items():
        subcategorias_lista = []
        for sub_nome, sub_valor in dados['subcategorias'].items():
            subcategorias_lista.append({
                'nome': sub_nome,
                'valor': sub_valor
            })
        subcategorias_lista.sort(key=lambda x: x['valor'], reverse=True)
        
        analise_categorias['receitas'].append({
            'id': cat_id,
            'nome': dados['nome'],
            'cor': dados['cor'],
            'icone': dados['icone'],
            'total': dados['total'],
            'subcategorias': subcategorias_lista
        })
    
    analise_categorias['receitas'].sort(key=lambda x: x['total'], reverse=True)
    analise_categorias['total_receitas'] = sum(cat['total'] for cat in analise_categorias['receitas'])
    
    # 4. CALCULAR ECONOMIA DO MÊS
    analise_categorias['economia_mes'] = (
        analise_categorias['total_receitas'] - 
        analise_categorias['total_despesas'] - 
        analise_categorias['total_investimentos']
    )
    
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
                         total_receitas_pendentes=total_receitas_pendentes,
                         total_despesas_pendentes=total_despesas_pendentes,
                         total_faturas_pendentes=total_faturas_pendentes,
                         analise_categorias=analise_categorias,
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

@main_bp.route('/extrato-cartao/download')
def download_extrato_cartao():
    """Download do extrato do cartão em Excel"""
    # Obter parâmetros
    mes = request.args.get('mes', type=int, default=date.today().month)
    ano = request.args.get('ano', type=int, default=date.today().year)
    cartao_id = request.args.get('cartao_id', type=int)
    
    if not cartao_id:
        return "Cartão não selecionado", 400
    
    # Buscar cartão
    cartao = Cartao.query.get(cartao_id)
    if not cartao:
        return "Cartão não encontrado", 404
    
    # Buscar despesas do cartão para o mês selecionado
    despesas = Lancamento.query.filter(
        Lancamento.tipo == 'cartao_credito',
        Lancamento.cartao_id == cartao_id,
        extract('year', Lancamento.mes_inicial_cartao) == ano,
        extract('month', Lancamento.mes_inicial_cartao) == mes
    ).order_by(Lancamento.data_vencimento).all()
    
    # Calcular total
    total_fatura = sum(despesa.valor for despesa in despesas)
    
    # Criar arquivo Excel em memória
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Extrato')
    
    # Formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#6f42c1',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 16,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    subtitle_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    money_format = workbook.add_format({
        'num_format': 'R$ #,##0.00',
        'align': 'right'
    })
    
    total_format = workbook.add_format({
        'bold': True,
        'num_format': 'R$ #,##0.00',
        'align': 'right',
        'bg_color': '#f8f9fa',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd/mm/yyyy',
        'align': 'center'
    })
    
    # Ajustar largura das colunas
    worksheet.set_column('A:A', 12)  # Data
    worksheet.set_column('B:B', 40)  # Descrição
    worksheet.set_column('C:C', 20)  # Categoria
    worksheet.set_column('D:D', 20)  # Subcategoria
    worksheet.set_column('E:E', 15)  # Tag
    worksheet.set_column('F:F', 15)  # Valor
    
    # Título
    meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    worksheet.merge_range('A1:F1', f'Extrato {cartao.nome} - {meses_nomes[mes-1]}/{ano}', title_format)
    
    # Informações do cartão
    worksheet.write('A3', 'Cartão:', subtitle_format)
    worksheet.write('B3', cartao.nome)
    worksheet.write('A4', 'Banco:', subtitle_format)
    worksheet.write('B4', cartao.conta.nome)
    
    # Calcular data de vencimento
    try:
        data_vencimento_cartao = date(ano, mes, cartao.dia_vencimento)
    except ValueError:
        ultimo_dia = monthrange(ano, mes)[1]
        data_vencimento_cartao = date(ano, mes, ultimo_dia)
    
    worksheet.write('A5', 'Vencimento:', subtitle_format)
    worksheet.write_datetime('B5', data_vencimento_cartao, date_format)
    
    # Cabeçalhos da tabela
    row = 7
    worksheet.write(row, 0, 'Data', header_format)
    worksheet.write(row, 1, 'Descrição', header_format)
    worksheet.write(row, 2, 'Categoria', header_format)
    worksheet.write(row, 3, 'Subcategoria', header_format)
    worksheet.write(row, 4, 'Tag', header_format)
    worksheet.write(row, 5, 'Valor', header_format)
    
    # Dados
    row = 8
    for despesa in despesas:
        worksheet.write_datetime(row, 0, despesa.data_vencimento, date_format)
        
        # Descrição com indicador de parcela
        descricao = despesa.descricao
        if despesa.numero_parcela:
            descricao += f' ({despesa.numero_parcela}/{despesa.total_parcelas})'
        worksheet.write(row, 1, descricao)
        
        worksheet.write(row, 2, despesa.categoria.nome)
        worksheet.write(row, 3, despesa.subcategoria.nome if despesa.subcategoria else '')
        worksheet.write(row, 4, despesa.tag or '')
        worksheet.write(row, 5, float(despesa.valor), money_format)
        row += 1
    
    # Total
    row += 1
    worksheet.merge_range(f'A{row+1}:E{row+1}', 'TOTAL', header_format)
    worksheet.write(row, 5, float(total_fatura), total_format)
    
    # Fechar o workbook
    workbook.close()
    
    # Preparar o arquivo para download
    output.seek(0)
    
    # Nome do arquivo
    filename = f"extrato_{cartao.nome.lower().replace(' ', '_')}_{mes:02d}_{ano}.xlsx"
    
    return Response(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@main_bp.route('/testar-alertas')
def testar_alertas():
    """Rota de teste para enviar alertas de email imediatamente"""
    try:
        from app.services.scheduler import executar_alertas_agora
        
        # Executar alertas
        sucesso = executar_alertas_agora(current_app)
        
        if sucesso:
            flash('Alertas enviados com sucesso! Verifique seu email.', 'success')
        else:
            flash('Nenhum alerta foi enviado. Verifique se há lançamentos vencendo amanhã ou se houve algum erro.', 'info')
            
    except Exception as e:
        flash(f'Erro ao enviar alertas: {str(e)}', 'error')
        
    return redirect(url_for('main.home'))