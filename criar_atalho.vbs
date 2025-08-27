' criar_atalho.vbs
' Script VBScript para criar um atalho no Desktop

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Obter caminhos
strDesktop = WshShell.SpecialFolders("Desktop")
strCurrentDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' Criar atalho
Set oShellLink = WshShell.CreateShortcut(strDesktop & "\Sistema Finanças.lnk")

' Configurar o atalho
oShellLink.TargetPath = strCurrentDir & "\iniciar_sistema.bat"
oShellLink.WindowStyle = 1
oShellLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll, 13"
oShellLink.Description = "Sistema de Finanças Pessoais"
oShellLink.WorkingDirectory = strCurrentDir

' Salvar o atalho
oShellLink.Save

MsgBox "Atalho criado com sucesso no Desktop!", vbInformation, "Sistema de Finanças"