@echo off
echo ========================================
echo    SISTEMA DE FINANCAS PESSOAIS
echo ========================================
echo.

REM Navegar para o diretório do projeto
cd /d "%~dp0"

REM Verificar se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo.
    echo Criando ambiente virtual...
    python -m venv venv
    
    echo.
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
    
    echo.
    echo Instalando dependencias...
    pip install -r requirements.txt
) else (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

echo.
echo ========================================
echo Iniciando o sistema...
echo ========================================
echo.
echo Acesse: http://localhost:5000
echo.
echo Pressione CTRL+C para parar o servidor
echo ========================================
echo.

REM Abrir o navegador após 3 segundos (em background)
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

REM Executar a aplicação
python app.py

REM Pausa ao final para ver mensagens de erro (se houver)
pause