# app/routes/categorias_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app.models import db, Categoria, Subcategoria
from sqlalchemy.exc import IntegrityError

# Criar o Blueprint
categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route('/categorias', methods=['GET', 'POST'])
def pagina_categorias():
    if request.method == 'POST':
        # Processar o formulário
        nome = request.form.get('nome')
        tipo = request.form.get('tipo')
        icone = request.form.get('icone', 'category')  # Ícone padrão
        cor = request.form.get('cor', '#28a745')  # Cor padrão
        
        # Verificar se a categoria já existe
        categoria_existente = Categoria.query.filter_by(nome=nome).first()
        if categoria_existente:
            flash('Já existe uma categoria com esse nome!', 'error')
            return redirect(url_for('categorias.pagina_categorias'))
        
        # Criar nova categoria
        nova_categoria = Categoria(
            nome=nome,
            tipo=tipo,
            icone=icone,
            cor=cor,
            ativa=True
        )
        
        try:
            db.session.add(nova_categoria)
            db.session.commit()
            flash('Categoria cadastrada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar categoria. Tente novamente.', 'error')
            print(f"Erro: {e}")
        
        return redirect(url_for('categorias.pagina_categorias'))
    
    # GET - Buscar todas as categorias com suas subcategorias
    categorias = Categoria.query.order_by(Categoria.tipo, Categoria.nome).all()
    return render_template('categorias.html', categorias=categorias)

@categorias_bp.route('/categorias/<int:id>/editar', methods=['POST'])
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    
    categoria.nome = request.form.get('nome')
    categoria.tipo = request.form.get('tipo')
    categoria.icone = request.form.get('icone', 'category')
    categoria.cor = request.form.get('cor', '#28a745')
    
    try:
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Já existe uma categoria com esse nome!', 'error')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao atualizar categoria.', 'error')
        print(f"Erro: {e}")
    
    return redirect(url_for('categorias.pagina_categorias'))

@categorias_bp.route('/categorias/<int:id>/excluir', methods=['POST'])
def excluir_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    
    try:
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoria excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir categoria.', 'error')
        print(f"Erro: {e}")
    
    return redirect(url_for('categorias.pagina_categorias'))

# Rotas para Subcategorias
@categorias_bp.route('/categorias/<int:categoria_id>/subcategorias', methods=['POST'])
def adicionar_subcategoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    nome = request.form.get('nome')
    descricao = request.form.get('descricao', '')
    
    # Verificar se já existe subcategoria com mesmo nome nesta categoria
    subcategoria_existente = Subcategoria.query.filter_by(
        nome=nome, 
        categoria_id=categoria_id
    ).first()
    
    if subcategoria_existente:
        flash('Já existe uma subcategoria com esse nome nesta categoria!', 'error')
        return redirect(url_for('categorias.pagina_categorias'))
    
    nova_subcategoria = Subcategoria(
        nome=nome,
        categoria_id=categoria_id,
        descricao=descricao,
        ativa=True
    )
    
    try:
        db.session.add(nova_subcategoria)
        db.session.commit()
        flash('Subcategoria adicionada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao adicionar subcategoria.', 'error')
        print(f"Erro: {e}")
    
    return redirect(url_for('categorias.pagina_categorias'))

@categorias_bp.route('/subcategorias/<int:id>/editar', methods=['POST'])
def editar_subcategoria(id):
    subcategoria = Subcategoria.query.get_or_404(id)
    
    subcategoria.nome = request.form.get('nome')
    subcategoria.descricao = request.form.get('descricao', '')
    
    try:
        db.session.commit()
        flash('Subcategoria atualizada com sucesso!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Já existe uma subcategoria com esse nome nesta categoria!', 'error')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao atualizar subcategoria.', 'error')
        print(f"Erro: {e}")
    
    return redirect(url_for('categorias.pagina_categorias'))

@categorias_bp.route('/subcategorias/<int:id>/excluir', methods=['POST'])
def excluir_subcategoria(id):
    subcategoria = Subcategoria.query.get_or_404(id)
    
    try:
        db.session.delete(subcategoria)
        db.session.commit()
        flash('Subcategoria excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir subcategoria.', 'error')
        print(f"Erro: {e}")
    
    return redirect(url_for('categorias.pagina_categorias'))

# Rota para buscar subcategorias de uma categoria (AJAX)
@categorias_bp.route('/api/categorias/<int:categoria_id>/subcategorias')
def obter_subcategorias(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    subcategorias = [{
        'id': sub.id,
        'nome': sub.nome,
        'descricao': sub.descricao
    } for sub in categoria.subcategorias if sub.ativa]
    
    return jsonify(subcategorias)