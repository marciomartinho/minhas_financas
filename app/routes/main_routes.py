# app/routes/main_routes.py

from flask import Blueprint, render_template

# A forma mais simples de criar um Blueprint, sem caminhos.
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')
