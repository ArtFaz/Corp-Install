# Configuração global — altere conforme o ambiente da rede corporativa.
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class InstallerConfig:
    path: str
    args: str = ""

@dataclass
class AppConfig:
    default_domain: str = "ultradisplays.local"
    unc_installers: str = r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS"
    
    # Pastas a copiar: (origem UNC, destino local)
    unc_folders_to_copy: List[Tuple[str, str]] = field(default_factory=lambda: [
        (r"\\192.168.0.8\nextone\client", r"C:\NextUltraDisplays"),
        (r"\\192.168.0.8\nextone\MEGAPAPER\Client_Mega", r"C:\NextUltraArt"),
    ])

    office_installer: InstallerConfig = field(default_factory=lambda: InstallerConfig(
        path=r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS\Microsoft Office 2013 (Pacote Standard)\Microsoft Office 2013 (Standard SP.01)\Microsoft Office 2013 - x64\setup.exe"
    ))

    office16_365_installer: InstallerConfig = field(default_factory=lambda: InstallerConfig(
        path=r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS\Microsoft Office 2016 (Pacote 365)\Microsoft Office (Pacote365)\OfficeSetup.exe"
    ))

    # Chocolatey packages: (package_id, arguments)
    # Teams por último — no Win11 ele já vem instalado e o Choco pode "falhar"
    choco_packages: List[Tuple[str, str]] = field(default_factory=lambda: [
        ("googlechrome", ""),
        ("winrar", ""),
        ("anydesk", "--params \"'/INSTALL'\""),
        ("microsoft-teams-new-install", ""),
    ])

    webapp_url: str = "http://192.168.0.15"
    webapp_name: str = "NextBP Sistema"
    webapp_shortcut_location: str = "Desktop"
    chrome_path: str = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Instância global
CONFIG = AppConfig()
