# app/__init__.py

import os
from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv

from .models import db

load_dotenv()

# --- MUDANÇA PRINCIPAL ---
# Pega o caminho absoluto para a pasta raiz do projeto (um nível acima de 'app')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def create_app():
    """
    Função Factory para criar e configurar a instância da aplicação Flask.
    """
    app = Flask(
        __name__,
        # Aponta para as pastas na raiz do projeto
        template_folder=os.path.join(project_root, 'templates'),
        static_folder=os.path.join(project_root, 'static')
    )

    # --- CONFIGURAÇÃO ---
    # Secret key para sessões (necessário para flash messages)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Garante que o UPLOAD_FOLDER também use o caminho correto
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    
    # Criar pasta de uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db_uri = os.getenv('DATABASE_URI')
    if not db_uri:
        raise ValueError("DATABASE_URI não foi encontrada no arquivo .env")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- INICIALIZAÇÃO DAS EXTENSÕES ---
    db.init_app(app)
    Migrate(app, db)
    
    # --- FILTROS PERSONALIZADOS ---
    @app.template_filter('moeda')
    def moeda_filter(value):
        """Formata valor para moeda brasileira com separador de milhar"""
        try:
            return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return "0,00"

    # --- REGISTRO DOS BLUEPRINTS (ROTAS) ---
    with app.app_context():
        from .routes.main_routes import main_bp
        from .routes.contas_routes import contas_bp
        from .routes.categorias_routes import categorias_bp
        from .routes.cartoes_routes import cartoes_bp
        from .routes.lancamentos_routes import lancamentos_bp
        from .routes.tags_routes import tags_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(contas_bp)
        app.register_blueprint(categorias_bp, url_prefix='/categorias')
        app.register_blueprint(cartoes_bp)
        app.register_blueprint(lancamentos_bp)
        app.register_blueprint(tags_bp)

    return app