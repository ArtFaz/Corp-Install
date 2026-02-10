# Configuração global — altere conforme o ambiente da rede corporativa.

CONFIG = {
    "default_domain": "ultradisplays.local",

    "unc_installers": r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS",

    # Pastas a copiar: (origem UNC, destino local)
    "unc_folders_to_copy": [
        (r"\\192.168.0.8\nextone\client", r"C:\NextUltraDisplays"),
        (r"\\192.168.0.8\nextone\MEGAPAPER\Client_Mega", r"C:\NextUltraArt"),
    ],

    "office_installer": {
        "path": r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS\Microsoft Office 2013 (Pacote Standard)\Microsoft Office 2013 (Standard SP.01)\Microsoft Office 2013 - x64\setup.exe",
        "args": ""
    },
    "office16_365_installer": {
        "path": r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS\Microsoft Office 2016 (Pacote 365)\Microsoft Office (Pacote365)\OfficeSetup.exe",
        "args": ""
    },

    "winget_packages": [
        "Google.Chrome",
        "RARLab.WinRAR",
        "Microsoft.Teams",
        "AnyDesk.AnyDesk",
    ],

    "webapp_url": "http://192.168.0.15",
    "webapp_name": "NextBP Sistema",
    "webapp_shortcut_location": "Desktop",

    "chrome_path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
}
