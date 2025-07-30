# app.py (na pasta raiz do projeto)

import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÃO INICIAL ---
load_dotenv()

# Com o app.py na raiz, o Flask encontra 'templates' e 'static' automaticamente.
app = Flask(__name__)

# Configurações da aplicação
db_uri = os.getenv('DATABASE_URI')
if not db_uri:
    raise ValueError("DATABASE_URI não foi encontrada no arquivo .env")

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')


# --- 2. BANCO DE DADOS E MIGRAÇÕES ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# --- 3. MODELOS (TABELAS DO BANCO) ---
# Trazemos a definição da tabela para cá
class Conta(db.Model):
    __tablename__ = 'contas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    tipo_conta = db.Column(db.String(50), nullable=False)
    saldo_inicial = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    imagem_arquivo = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Conta {self.nome}>'


# --- 4. ROTAS (AS PÁGINAS DO SITE) ---
@app.route('/')
def home():
    """ Rota para a página inicial. """
    return render_template('home.html')

@app.route('/contas')
def pagina_contas():
    """ Rota para a página de cadastro de contas. """
    return render_template('contas.html')


# --- PONTO DE PARTIDA PARA O COMANDO 'flask run' ---
# Não precisa de if __name__ == '__main__' para o comando 'flask run'
