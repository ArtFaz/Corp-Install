# Configuração global — altere conforme o ambiente da rede corporativa.
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

VERSION = "3.0.0"

@dataclass
class InstallerConfig:
    path: str
    args: str = ""

@dataclass
class ShortcutConfig:
    name: str
    target_exe: str

@dataclass
class FolderCopyConfig:
    source: str
    destination: str
    shortcut: Optional[ShortcutConfig] = None

@dataclass
class AppConfig:
    default_domain: str = "ultradisplays.local"
    unc_installers: str = r"\\192.168.0.11\t.i\@Instaladores de Formatação\@PROGRAMAS E UTILITÁRIOS"
    log_dir: str = r"C:\ProvisioningLogs"
    anydesk_secret_file: str = r"\\192.168.0.11\T.I\@Provisionador\anydesk_pswrd.txt"
    # Pastas a copiar e seus atalhos
    unc_folders_to_copy: List[FolderCopyConfig] = field(default_factory=lambda: [
        FolderCopyConfig(
            source=r"\\192.168.0.8\nextone\client",
            destination=r"C:\NextUltraDisplays",
            shortcut=ShortcutConfig(name="NextSI UltraDisplays", target_exe="NextSIClient.exe")
        ),
        FolderCopyConfig(
            source=r"\\192.168.0.8\nextone\MEGAPAPER\Client_Mega",
            destination=r"C:\NextUltraArt",
            shortcut=ShortcutConfig(name="NextSI UltraArt", target_exe="NextSIClient.exe")
        ),
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

    # Configurações de Auto-Update
    auto_update_enabled: bool = True
    # Diretório de rede onde os binários de atualização (.exe) e o arquivo version.json são hospedados
    update_network_dir: str = r"\\192.168.0.11\T.I\@Provisionador"

    def __post_init__(self):
        if not self.default_domain:
            raise ValueError("default_domain não pode ser vazio")
        if not self.log_dir:
            raise ValueError("log_dir não pode ser vazio")

# Instância global
CONFIG = AppConfig()

