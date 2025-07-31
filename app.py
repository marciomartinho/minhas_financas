# app.py (na pasta raiz do projeto)
# Este arquivo agora serve como o ponto de entrada principal para a sua aplicação.

from app import create_app
from app.services.scheduler import iniciar_scheduler
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Cria a instância da aplicação Flask usando a factory.
app = create_app()

# Inicializar o scheduler após criar a app
with app.app_context():
    iniciar_scheduler(app)

# Este bloco é útil se você quiser executar o servidor de desenvolvimento
# diretamente com 'python app.py'. O comando 'flask run' também funcionará.
if __name__ == '__main__':
    # O modo debug já é ativado pelo seu arquivo .flaskenv
    app.run()