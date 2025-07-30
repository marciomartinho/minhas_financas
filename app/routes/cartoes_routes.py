# app/routes/cartoes_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models import db, Cartao, Conta
from decimal import Decimal
import os
from werkzeug.utils import secure_filename

# Criar o Blueprint
cartoes_bp = Blueprint('cartoes', __name__)

# Configuração para upload de imagens
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_size(file):
    # Limita o tamanho do arquivo a 5MB
    file.seek(0, 2)  # Move para o final do arquivo
    file_size = file.tell()
    file.seek(0)  # Volta para o início
    return file_size <= 5 * 1024 * 1024  # 5MB em bytes

@cartoes_bp.route('/cartoes', methods=['GET', 'POST'])
def pagina_cartoes():
    if request.method == 'POST':
        # Processar o formulário
        nome = request.form.get('nome')
        conta_id = request.form.get('conta_id')
        dia_vencimento = request.form.get('dia_vencimento')
        limite = request.form.get('limite')
        
        # Validar dia do vencimento
        try:
            dia_vencimento = int(dia_vencimento)
            if dia_vencimento < 1 or dia_vencimento > 31:
                flash('O dia de vencimento deve estar entre 1 e 31!', 'error')
                return redirect(url_for('cartoes.pagina_cartoes'))
        except ValueError:
            flash('Dia de vencimento inválido!', 'error')
            return redirect(url_for('cartoes.pagina_cartoes'))
        
        # Verificar se o cartão já existe
        cartao_existente = Cartao.query.filter_by(nome=nome).first()
        if cartao_existente:
            flash('Já existe um cartão com esse nome!', 'error')
            return redirect(url_for('cartoes.pagina_cartoes'))
        
        # Processar upload de imagem (se houver)
        imagem_arquivo = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename != '' and allowed_file(file.filename):
                # Verificar tamanho do arquivo
                if not allowed_file_size(file):
                    flash('Imagem muito grande! O tamanho máximo é 5MB.', 'warning')
                else:
                    # Pegar extensão original do arquivo
                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                    # Criar nome seguro baseado no nome do cartão
                    safe_name = secure_filename(nome.lower().replace(' ', '_'))
                    # Nome final com timestamp para evitar conflitos
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"cartao_{safe_name}_{timestamp}.{file_ext}"
                    
                    try:
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        imagem_arquivo = filename
                        print(f"Imagem salva com sucesso: {filepath}")
                    except Exception as e:
                        print(f"Erro ao salvar imagem: {e}")
                        flash('Erro ao fazer upload da imagem, mas o cartão foi criado.', 'warning')
        
        # Criar novo cartão
        novo_cartao = Cartao(
            nome=nome,
            conta_id=int(conta_id),
            dia_vencimento=dia_vencimento,
            limite=Decimal(limite) if limite else None,
            imagem_arquivo=imagem_arquivo,
            ativo=True
        )
        
        try:
            db.session.add(novo_cartao)
            db.session.commit()
            flash('Cartão cadastrado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar cartão. Tente novamente.', 'error')
            print(f"Erro: {e}")
        
        return redirect(url_for('cartoes.pagina_cartoes'))
    
    # GET - Buscar todos os cartões e contas
    cartoes = Cartao.query.join(Conta).order_by(Cartao.nome).all()
    contas = Conta.query.filter_by(tipo_conta='Corrente').order_by(Conta.nome).all()
    return render_template('cartoes.html', cartoes=cartoes, contas=contas)

@cartoes_bp.route('/cartoes/<int:id>/editar', methods=['POST'])
def editar_cartao(id):
    cartao = Cartao.query.get_or_404(id)
    
    cartao.nome = request.form.get('nome')
    cartao.conta_id = int(request.form.get('conta_id'))
    cartao.dia_vencimento = int(request.form.get('dia_vencimento'))
    limite = request.form.get('limite')
    cartao.limite = Decimal(limite) if limite else None
    
    try:
        db.session.commit()
        flash('Cartão atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao atualizar cartão.', 'error')
        print(f"Erro: {e}")
    
    return redirect(url_for('cartoes.pagina_cartoes'))

@cartoes_bp.route('/cartoes/<int:id>/excluir', methods=['POST'])
def excluir_cartao(id):
    cartao = Cartao.query.get_or_404(id)
    
    try:
        # Se houver imagem, podemos excluí-la do servidor
        if cartao.imagem_arquivo:
            try:
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], cartao.imagem_arquivo)
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"Erro ao excluir imagem: {e}")
        
        db.session.delete(cartao)
        db.session.commit()
        flash('Cartão excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir cartão.', 'error')
        print(f"Erro: {e}")
    
    return redirect(url_for('cartoes.pagina_cartoes'))

@cartoes_bp.route('/cartoes/<int:id>/toggle', methods=['POST'])
def toggle_cartao(id):
    cartao = Cartao.query.get_or_404(id)
    
    try:
        cartao.ativo = not cartao.ativo
        db.session.commit()
        status = 'ativado' if cartao.ativo else 'desativado'
        flash(f'Cartão {status} com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao alterar status do cartão.', 'error')
        print(f"Erro: {e}")
    
    return redirect(url_for('cartoes.pagina_cartoes'))