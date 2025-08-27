# criar_atalho.py
# Script Python para criar um atalho no Desktop do Windows

import os
import win32com.client
import pythoncom

def criar_atalho_desktop():
    """Cria um atalho para o sistema no Desktop"""
    try:
        # Obter o caminho do Desktop
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        
        # Caminho do script atual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Caminho do arquivo .bat
        target_path = os.path.join(current_dir, 'iniciar_sistema.bat')
        
        # Verificar se o arquivo .bat existe
        if not os.path.exists(target_path):
            print(f"[ERRO] Arquivo não encontrado: {target_path}")
            print("Por favor, certifique-se de que o arquivo 'iniciar_sistema.bat' existe.")
            return False
        
        # Criar o objeto shell
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # Caminho do atalho
        shortcut_path = os.path.join(desktop, "Sistema Finanças.lnk")
        
        # Criar o atalho
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = current_dir
        shortcut.Description = "Sistema de Finanças Pessoais"
        
        # Ícone (usando um ícone do sistema por padrão)
        shortcut.IconLocation = "%SystemRoot%\\System32\\SHELL32.dll,13"
        
        # Se houver um favicon.ico na pasta static, usar ele
        icon_path = os.path.join(current_dir, 'static', 'favicon.ico')
        if os.path.exists(icon_path):
            shortcut.IconLocation = icon_path
        
        # Salvar o atalho
        shortcut.save()
        
        print(f"✓ Atalho criado com sucesso em: {shortcut_path}")
        return True
        
    except ImportError:
        print("[ERRO] Biblioteca pywin32 não instalada.")
        print("Execute: pip install pywin32")
        return False
    except Exception as e:
        print(f"[ERRO] Falha ao criar atalho: {str(e)}")
        return False

def criar_atalho_simples():
    """Alternativa simples sem dependências externas"""
    try:
        import subprocess
        
        # Script PowerShell para criar atalho
        ps_script = '''
$desktop = [Environment]::GetFolderPath("Desktop")
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$desktop\\Sistema Finanças.lnk")
$Shortcut.TargetPath = "{}"
$Shortcut.WorkingDirectory = "{}"
$Shortcut.Description = "Sistema de Finanças Pessoais"
$Shortcut.IconLocation = "%SystemRoot%\\System32\\SHELL32.dll,13"
$Shortcut.Save()
Write-Host "Atalho criado com sucesso!"
'''
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        target_path = os.path.join(current_dir, 'iniciar_sistema.bat')
        
        # Formatar o script com os caminhos corretos
        ps_script = ps_script.format(
            target_path.replace('\\', '\\\\'),
            current_dir.replace('\\', '\\\\')
        )
        
        # Executar o PowerShell
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Atalho criado com sucesso no Desktop!")
        else:
            print(f"[ERRO] {result.stderr}")
            
    except Exception as e:
        print(f"[ERRO] {str(e)}")

if __name__ == "__main__":
    print("=== Criar Atalho do Sistema de Finanças ===\n")
    
    # Tentar primeiro com pywin32
    try:
        import win32com.client
        criar_atalho_desktop()
    except ImportError:
        print("Biblioteca pywin32 não encontrada.")
        print("Tentando método alternativo...\n")
        criar_atalho_simples()
    
    input("\nPressione Enter para sair...")