# models.py
# Este arquivo define a estrutura das tabelas do banco de dados.

from flask_sqlalchemy import SQLAlchemy

# Criamos uma instância de SQLAlchemy sem associá-la a um app ainda.
# A associação será feita no arquivo principal app.py.
db = SQLAlchemy()

# Mapeamento da tabela de Contas Bancárias
class Conta(db.Model):
    # Define o nome da tabela no banco de dados. Boa prática para evitar conflitos.
    __tablename__ = 'contas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    # Usaremos 'Corrente' ou 'Investimento' aqui
    tipo_conta = db.Column(db.String(50), nullable=False) 
    saldo_inicial = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    # Não guardamos a imagem, mas sim o nome do arquivo dela.
    imagem_arquivo = db.Column(db.String(255), nullable=True) 

    def __repr__(self):
        return f'<Conta {self.nome}>'

# Você pode adicionar outras classes aqui no futuro (Ex: Categoria, Lancamento, etc.)
