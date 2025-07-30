# app/__init__.py

import os
from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv

from .models import db

load_dotenv()

# --- AQUI ESTÁ A MUDANÇA PRINCIPAL ---
# Pega o caminho absoluto para a pasta 'app' onde este arquivo está.
basedir = os.path.abspath(os.path.dirname(__file__))

def create_app():
    """
    Função Factory para criar e configurar a instância da aplicação Flask.
    """
    app = Flask(
        __name__,
        # Usamos o caminho absoluto para garantir que o Flask encontre as pastas.
        template_folder=os.path.join(basedir, 'templates'),
        static_folder=os.path.join(basedir, 'static')
    )

    # --- CONFIGURAÇÃO ---
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
        app.register_blueprint(main_bp)

        from .routes.contas_routes import contas_bp
        app.register_blueprint(contas_bp)

    return app
