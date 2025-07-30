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


# Mapeamento da tabela de Categorias
class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'Receita' ou 'Despesa'
    icone = db.Column(db.String(50), nullable=True)  # Nome do ícone Material Symbols
    cor = db.Column(db.String(7), nullable=True)  # Cor em hexadecimal (#RRGGBB)
    ativa = db.Column(db.Boolean, default=True)  # Para desativar categorias sem excluir
    
    # Relacionamento com subcategorias
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Categoria {self.nome}>'


# Mapeamento da tabela de Subcategorias
class Subcategoria(db.Model):
    __tablename__ = 'subcategorias'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    ativa = db.Column(db.Boolean, default=True)  # Para desativar subcategorias sem excluir
    
    # Constraint única para garantir que não existam subcategorias com mesmo nome na mesma categoria
    __table_args__ = (
        db.UniqueConstraint('nome', 'categoria_id', name='_nome_categoria_uc'),
    )

    def __repr__(self):
        return f'<Subcategoria {self.nome} - Categoria: {self.categoria.nome}>'


# Mapeamento da tabela de Cartões de Crédito
class Cartao(db.Model):
    __tablename__ = 'cartoes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=False)
    dia_vencimento = db.Column(db.Integer, nullable=False)  # Dia do mês (1-31)
    imagem_arquivo = db.Column(db.String(255), nullable=True)  # Logo do cartão
    limite = db.Column(db.Numeric(10, 2), nullable=True)  # Limite do cartão (opcional)
    ativo = db.Column(db.Boolean, default=True)  # Para desativar sem excluir
    
    # Relacionamento com conta
    conta = db.relationship('Conta', backref='cartoes')

    def __repr__(self):
        return f'<Cartao {self.nome} - Conta: {self.conta.nome}>'
    
# Mapeamento da tabela de Lançamentos
class Lancamento(db.Model):
    __tablename__ = 'lancamentos'

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # despesa, receita, cartao_credito, transferencia
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategorias.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pendente')  # pendente, pago, cancelado
    recorrencia = db.Column(db.String(20), nullable=False, default='unica')  # unica, mensal, anual, semanal, quinzenal, parcelada
    data_criacao = db.Column(db.DateTime, nullable=False, default=db.func.now())
    cartao_id = db.Column(db.Integer, db.ForeignKey('cartoes.id'), nullable=True)
    conta_destino_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=True)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)
    numero_parcela = db.Column(db.Integer, nullable=True)
    total_parcelas = db.Column(db.Integer, nullable=True)
    lancamento_pai_id = db.Column(db.Integer, db.ForeignKey('lancamentos.id'), nullable=True)
    tag = db.Column(db.String(50), nullable=True)  # Campo para tags/etiquetas
    
    # Relacionamentos
    conta = db.relationship('Conta', foreign_keys=[conta_id], backref='lancamentos')
    conta_destino = db.relationship('Conta', foreign_keys=[conta_destino_id])
    categoria = db.relationship('Categoria', backref='lancamentos')
    subcategoria = db.relationship('Subcategoria', backref='lancamentos')
    cartao = db.relationship('Cartao', backref='lancamentos')
    lancamento_pai = db.relationship('Lancamento', remote_side=[id], backref='parcelas')

    def __repr__(self):
        return f'<Lancamento {self.descricao} - R$ {self.valor}>'


# Você pode adicionar outras classes aqui no futuro (Ex: Lancamento, etc.)