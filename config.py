# =============================================================================
# CONFIGURAÇÃO GLOBAL
# =============================================================================
# Altere os valores abaixo conforme o ambiente da sua rede corporativa.

CONFIG = {
    # --- DOMÍNIO ---
    "default_domain": "ultradisplays.local",  # Domínio padrão para ingresso

    # --- CAMINHOS DE REDE (UNC) ---
    # Caminho para os instaladores locais (Office)
    "unc_installers": r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS",
    
    # Pastas a serem copiadas para C:\
    # Formato: (origem, destino)
    "unc_folders_to_copy": [
        (r"\\192.168.0.8\nextone\client", r"C:\NextUltraDisplays"),
        (r"\\192.168.0.8\nextone\MEGAPAPER\Client_Mega", r"C:\NextUltraArt"),
    ],

    # --- INSTALADORES OFFLINE ---
    # Office 2013 (Padrão)
    "office_installer": {
        "path": r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS\Microsoft Office 2013 (Pacote Standard)\Microsoft Office 2013 (Standard SP.01)\Microsoft Office 2013 - x64\setup.exe",
        "args": "/configure configuration.xml"
    },
    # Office 2016/365 (Alternativo)
    "office16_365_installer": {
        "path": r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS\Microsoft Office 2016 (Pacote 365)\Microsoft Office (Pacote365)\OfficeSetup.exe",
        "args": ""  # Office 365 geralmente não precisa de args
    },

    # --- WINGET (IDs de pacotes) ---
    "winget_packages": [
        "Google.Chrome",
        "RARLab.WinRAR",
        "Microsoft.Teams",
        "AnyDesk.AnyDesk",
    ],

    # --- WEBAPP (Atalho Chrome --app) ---
    "webapp_url": "http://192.168.0.15",
    "webapp_name": "NextBP Sistema",
    "webapp_shortcut_location": "Desktop",  # Desktop ou StartMenu

    # --- CHROME PATH ---
    "chrome_path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
}
