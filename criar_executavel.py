# criar_executavel.py
# Script para criar um executável do sistema usando PyInstaller

import subprocess
import sys
import os

def instalar_pyinstaller():
    """Instala o PyInstaller se não estiver instalado"""
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def criar_executavel():
    """Cria o executável usando PyInstaller"""
    # Primeiro, criar um script launcher
    launcher_content = '''
import os
import sys
import webbrowser
import time
import threading
from app import create_app
from app.services.scheduler import iniciar_scheduler

def abrir_navegador():
    """Abre o navegador após 2 segundos"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # Mudar para o diretório do executável
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    
    # Criar a aplicação
    app = create_app()
    
    # Inicializar o scheduler
    with app.app_context():
        iniciar_scheduler(app)
    
    # Abrir o navegador em uma thread separada
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    # Iniciar o servidor
    print("========================================")
    print("   SISTEMA DE FINANÇAS PESSOAIS")
    print("========================================")
    print("")
    print("Servidor iniciado em: http://localhost:5000")
    print("Pressione CTRL+C para parar")
    print("")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
'''
    
    # Salvar o launcher
    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # Criar arquivo spec para PyInstaller
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('.env', '.'),
        ('.flaskenv', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_sqlalchemy',
        'flask_migrate',
        'flask_mail',
        'apscheduler',
        'psycopg2',
        'dotenv',
        'dateutil',
        'xlsxwriter',
        'email.mime.text',
        'email.mime.multipart',
        'email.mime.base',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SistemaFinancas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/favicon.ico' if os.path.exists('static/favicon.ico') else None,
)
'''
    
    # Salvar o arquivo spec
    with open('sistema_financas.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Criando executável...")
    
    # Executar PyInstaller
    subprocess.call([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'sistema_financas.spec'
    ])
    
    print("\nExecutável criado em: dist/SistemaFinancas.exe")
    
    # Limpar arquivos temporários
    os.remove('launcher.py')
    os.remove('sistema_financas.spec')

if __name__ == '__main__':
    instalar_pyinstaller()
    criar_executavel()