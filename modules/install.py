"""Etapa 2: Softwares e Configurações Pós-Login AD."""
import os
import shutil
import subprocess
from pathlib import Path

from config import CONFIG
from utils.common import print_header, print_step
from utils.powershell import run_powershell
from utils.logger import get_logger


def run_full_install():
    """Instalação completa pós-login no domínio."""
    logger = get_logger()
    
    print_header("ETAPA 2: INSTALAÇÃO DE SOFTWARES")
    print("\nEsta etapa irá:")
    print("  • Instalar Chrome, WinRAR, Teams, AnyDesk (Winget)")
    print("  • Copiar pastas da rede para C:")
    print("  • Instalar Office")
    print("  • Criar atalho do sistema web")
    print("  • Abrir AnyDesk para coletar ID\n")
    
    # --- 1. Winget ---
    _install_winget_packages()
    
    # --- 2. Cópia de Pastas ---
    _copy_network_folders()
    
    # --- 3. Office ---
    _install_local_software()
    
    # --- 4. WebApp ---
    _create_webapp_shortcut()
    
    # --- 5. AnyDesk ---
    _launch_anydesk()
    
    logger.success("Etapa 2 concluída!")
    print("\n" + "=" * 50)
    print("   INSTALAÇÃO CONCLUÍDA!")
    print("=" * 50)
    print(f"\nLog: {logger.get_log_path()}")
    
    return True


def _install_winget_packages():
    logger = get_logger()
    print_step("Instalando softwares via Winget...")
    
    packages = CONFIG.get("winget_packages", [])
    
    for package_id in packages:
        logger.info(f"Winget: {package_id}")
        print(f"    -> {package_id}...")
        
        cmd = f'winget install --id "{package_id}" --accept-source-agreements --accept-package-agreements --silent'
        return_code, stdout, stderr = run_powershell(cmd, capture_output=False)
        
        if return_code == 0:
            logger.success(f"{package_id} instalado.")
        else:
            logger.warning(f"Erro em {package_id}. Verifique manualmente.")


def _copy_network_folders():
    logger = get_logger()
    print_step("Copiando pastas da rede...")
    
    folders = CONFIG.get("unc_folders_to_copy", [])
    
    if not folders:
        print("    (Nenhuma pasta configurada)")
        return
    
    for source, destination in folders:
        logger.info(f"Copiando: {source} -> {destination}")
        print(f"    {source} -> {destination}")
        
        try:
            if os.path.exists(destination):
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
            logger.success(f"Copiado: {destination}")
        except Exception as e:
            logger.error(f"Falha: {e}")
            print(f"    [ERRO] {e}")


def _install_local_software():
    logger = get_logger()
    print_step("Instalando Office...")
    
    office_version = _select_office_version()
    
    if office_version == "2013":
        office_cfg = CONFIG.get("office_installer", {})
        if office_cfg.get("path"):
            _run_installer("Office 2013", office_cfg["path"], office_cfg.get("args", ""))
    elif office_version == "365":
        office_cfg = CONFIG.get("office16_365_installer", {})
        if office_cfg.get("path"):
            _run_installer("Office 365", office_cfg["path"], office_cfg.get("args", ""))
    else:
        print("    [INFO] Instalação do Office pulada.")
        logger.info("Office pulado.")


def _select_office_version() -> str:
    print("\n  ┌─────────────────────────────────────────────┐")
    print("  │       SELECIONE A VERSÃO DO OFFICE          │")
    print("  ├─────────────────────────────────────────────┤")
    print("  │  [1]  Office 2013 (Standard SP.01 x64)      │")
    print("  │  [2]  Office 365 (Pacote 2016)              │")
    print("  │  [0]  Pular instalação do Office            │")
    print("  └─────────────────────────────────────────────┘")
    
    while True:
        try:
            opcao = input("\n  Versão desejada: ").strip()
        except (KeyboardInterrupt, EOFError):
            return ""
        
        if opcao == "1":
            return "2013"
        elif opcao == "2":
            return "365"
        elif opcao == "0":
            return ""
        else:
            print("  [!] Opção inválida.")


def _run_installer(name: str, path: str, args: str):
    logger = get_logger()
    print(f"    -> Instalando {name}...")
    
    if not os.path.exists(path):
        logger.error(f"{name}: Arquivo não encontrado: {path}")
        print(f"    [ERRO] Arquivo não encontrado: {path}")
        return
    
    logger.info(f"Executando: {path}")
    
    try:
        full_cmd = f'"{path}" {args}'
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.success(f"{name} instalado.")
            print(f"    [OK] {name} instalado.")
        else:
            logger.warning(f"{name}: Código {result.returncode}")
            print(f"    [AVISO] Código {result.returncode}")
    except Exception as e:
        logger.error(f"Falha: {e}")
        print(f"    [ERRO] {e}")


def _create_webapp_shortcut():
    logger = get_logger()
    print_step("Configurando atalho WebApp...")
    
    webapp_url = CONFIG.get("webapp_url", "")
    webapp_name = CONFIG.get("webapp_name", "WebApp")
    chrome_path = CONFIG.get("chrome_path", "")
    
    if not webapp_url:
        print("    (URL não configurada)")
        return
    
    if not os.path.exists(chrome_path):
        logger.warning(f"Chrome não encontrado: {chrome_path}")
        print(f"    [AVISO] Chrome não encontrado: {chrome_path}")
        
        # Caminhos alternativos
        alt_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        chrome_path = None
        for alt in alt_paths:
            if os.path.exists(alt):
                chrome_path = alt
                break
        
        if not chrome_path:
            logger.error("Chrome não encontrado.")
            print("    [ERRO] Chrome não encontrado.")
            return
    
    logger.info(f"Atalho: {webapp_name} -> {webapp_url}")
    
    if CONFIG.get("webapp_shortcut_location") == "Desktop":
        shortcut_dir = os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), "Desktop")
    else:
        shortcut_dir = os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), 
                                     "Microsoft", "Windows", "Start Menu", "Programs")
    
    shortcut_path = os.path.join(shortcut_dir, f"{webapp_name}.lnk")
    
    # VBScript para criar atalho
    vbs_script = f'''
Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{shortcut_path}")
Shortcut.TargetPath = "{chrome_path}"
Shortcut.Arguments = "--app={webapp_url}"
Shortcut.WorkingDirectory = "{os.path.dirname(chrome_path)}"
Shortcut.Description = "{webapp_name}"
Shortcut.Save
'''
    
    vbs_path = os.path.join(os.environ.get("TEMP", "/tmp"), "create_shortcut.vbs")
    try:
        with open(vbs_path, 'w', encoding='utf-8') as f:
            f.write(vbs_script)
        
        subprocess.run(["cscript", "//Nologo", vbs_path], capture_output=True)
        
        logger.success(f"Atalho criado: {shortcut_path}")
        print(f"    [OK] Atalho: {shortcut_path}")
    except Exception as e:
        logger.error(f"Falha: {e}")
        print(f"    [ERRO] {e}")
    finally:
        try:
            os.remove(vbs_path)
        except:
            pass


def _launch_anydesk():
    logger = get_logger()
    print_step("Abrindo AnyDesk...")
    
    # Caminhos comuns do AnyDesk
    anydesk_paths = [
        r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe",
        r"C:\Program Files\AnyDesk\AnyDesk.exe",
        os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "AnyDesk", "AnyDesk.exe"),
    ]
    
    anydesk_exe = None
    for path in anydesk_paths:
        if os.path.exists(path):
            anydesk_exe = path
            break
    
    if anydesk_exe:
        logger.info(f"Abrindo: {anydesk_exe}")
        try:
            subprocess.Popen([anydesk_exe])
            print("    [OK] AnyDesk aberto. Anote o ID.")
        except Exception as e:
            logger.error(f"Falha: {e}")
            print(f"    [ERRO] {e}")
    else:
        logger.warning("AnyDesk não encontrado.")
        print("    [AVISO] AnyDesk não encontrado.")
