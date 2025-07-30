# app/routes/contas_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models import db, Conta
from decimal import Decimal
import os
from werkzeug.utils import secure_filename

# Criar o Blueprint
contas_bp = Blueprint('contas', __name__)

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

@contas_bp.route('/contas', methods=['GET', 'POST'])
def pagina_contas():
    if request.method == 'POST':
        # Processar o formulário
        nome = request.form.get('nome')
        tipo_conta = request.form.get('tipo_conta')
        saldo_inicial = request.form.get('saldo_inicial', '0.00')
        
        # Verificar se a conta já existe
        conta_existente = Conta.query.filter_by(nome=nome).first()
        if conta_existente:
            flash('Já existe uma conta com esse nome!', 'error')
            return redirect(url_for('contas.pagina_contas'))
        
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
                    # Criar nome seguro baseado no nome da conta
                    safe_name = secure_filename(nome.lower().replace(' ', '_'))
                    # Nome final com timestamp para evitar conflitos
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{safe_name}_{timestamp}.{file_ext}"
                    
                    try:
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        imagem_arquivo = filename
                        print(f"Imagem salva com sucesso: {filepath}")
                    except Exception as e:
                        print(f"Erro ao salvar imagem: {e}")
                        flash('Erro ao fazer upload da imagem, mas a conta foi criada.', 'warning')
        
        # Criar nova conta
        nova_conta = Conta(
            nome=nome,
            tipo_conta=tipo_conta,
            saldo_inicial=Decimal(saldo_inicial),
            imagem_arquivo=imagem_arquivo
        )
        
        try:
            db.session.add(nova_conta)
            db.session.commit()
            flash('Conta cadastrada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar conta. Tente novamente.', 'error')
            print(f"Erro: {e}")
        
        return redirect(url_for('contas.pagina_contas'))
    
    # GET - Buscar todas as contas
    contas = Conta.query.order_by(Conta.nome).all()
    return render_template('contas.html', contas=contas)

@contas_bp.route('/contas/<int:id>/editar', methods=['POST'])
def editar_conta(id):
    conta = Conta.query.get_or_404(id)
    
    conta.nome = request.form.get('nome')
    conta.tipo_conta = request.form.get('tipo_conta')
    conta.saldo_inicial = Decimal(request.form.get('saldo_inicial', '0.00'))
    
    try:
        db.session.commit()
        flash('Conta atualizada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao atualizar conta.', 'error')
    
    return redirect(url_for('contas.pagina_contas'))

@contas_bp.route('/contas/<int:id>/excluir', methods=['POST'])
def excluir_conta(id):
    conta = Conta.query.get_or_404(id)
    
    try:
        db.session.delete(conta)
        db.session.commit()
        flash('Conta excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir conta.', 'error')
    
    return redirect(url_for('contas.pagina_contas'))