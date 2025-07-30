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
    # Garante que o UPLOAD_FOLDER também use o caminho correto
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    
    db_uri = os.getenv('DATABASE_URI')
    if not db_uri:
        raise ValueError("DATABASE_URI não foi encontrada no arquivo .env")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- INICIALIZAÇÃO DAS EXTENSÕES ---
    db.init_app(app)
    Migrate(app, db)

    # --- REGISTRO DOS BLUEPRINTS (ROTAS) ---
    with app.app_context():
        from .routes.main_routes import main_bp
        from .routes.contas_routes import contas_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(contas_bp)

    return app