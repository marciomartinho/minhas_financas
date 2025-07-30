# app/routes/contas_routes.py

from flask import Blueprint, render_template

# A forma mais simples de criar um Blueprint, sem caminhos.
contas_bp = Blueprint('contas', __name__)

@contas_bp.route('/contas')
def pagina_contas():
    return render_template('contas.html')
