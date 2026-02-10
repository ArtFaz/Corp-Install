"""Etapa 2: Softwares e configurações pós-login AD."""
import os
import shutil
import subprocess
import time

from config import CONFIG
from utils.common import print_header, print_step
from utils.powershell import run_powershell
from utils.logger import get_logger
from utils.colors import (
    Colors, success, error, warning, info, green, yellow, cyan,
    step_status, styled_input
)
from utils.progress import Spinner, ProgressBar, show_summary_card, show_celebration


def run_full_install():
    """Instalação completa pós-login no domínio."""
    logger = get_logger()
    total_steps = 5
    start_time = time.time()

    print_header("ETAPA 2: INSTALAÇÃO DE SOFTWARES")

    print(f"  {Colors.MUTED}Esta etapa irá:{Colors.RESET}")
    print(f"    {Colors.PRIMARY}•{Colors.RESET} Instalar Chrome, WinRAR, Teams, AnyDesk (Winget)")
    print(f"    {Colors.PRIMARY}•{Colors.RESET} Copiar pastas da rede para C:")
    print(f"    {Colors.PRIMARY}•{Colors.RESET} Instalar Office")
    print(f"    {Colors.PRIMARY}•{Colors.RESET} Criar atalho do sistema web")
    print(f"    {Colors.PRIMARY}•{Colors.RESET} Abrir AnyDesk para coletar ID")
    print("")

    results = []

    print(step_status(1, total_steps, "Instalando softwares via Winget...", "running"))
    ok = install_winget_packages()
    results.append(("Softwares (Winget)", "ok" if ok else "warn", "Chrome, WinRAR, Teams, AnyDesk"))
    print(step_status(1, total_steps, "Softwares via Winget", "done" if ok else "error"))

    print(step_status(2, total_steps, "Copiando pastas da rede...", "running"))
    ok = copy_network_folders()
    results.append(("Pastas da Rede", "ok" if ok else "warn", "UNC → C:\\"))
    print(step_status(2, total_steps, "Pastas copiadas", "done" if ok else "error"))

    print(step_status(3, total_steps, "Instalando Office...", "running"))
    ok = install_office()
    results.append(("Office", "ok" if ok else "skip", ""))
    print(step_status(3, total_steps, "Office", "done" if ok else "skip"))

    print(step_status(4, total_steps, "Configurando atalho WebApp...", "running"))
    ok = create_webapp_shortcut()
    results.append(("Atalho WebApp", "ok" if ok else "warn", ""))
    print(step_status(4, total_steps, "WebApp configurado", "done" if ok else "error"))

    print(step_status(5, total_steps, "Abrindo AnyDesk...", "running"))
    ok = launch_anydesk()
    results.append(("AnyDesk", "ok" if ok else "warn", "Anote o ID"))
    print(step_status(5, total_steps, "AnyDesk", "done" if ok else "error"))

    elapsed = time.time() - start_time
    logger.success(f"Etapa 2 concluída em {elapsed:.0f}s!")

    show_summary_card("✓ INSTALAÇÃO CONCLUÍDA", results, elapsed)
    show_celebration()

    return True


def install_winget_packages() -> bool:
    """Instala pacotes configurados via Winget."""
    logger = get_logger()
    print_step("Instalando softwares via Winget...")

    packages = CONFIG.get("winget_packages", [])
    total = len(packages)
    all_ok = True
    pb = ProgressBar(total=total, label="Winget")

    for idx, package_id in enumerate(packages, 1):
        logger.info(f"Winget: {package_id}")
        pb.update(idx, detail=package_id)

        cmd = f'winget install --id "{package_id}" --source winget --accept-source-agreements --accept-package-agreements --silent'
        return_code, _, _ = run_powershell(cmd, capture_output=False)

        if return_code == 0:
            logger.success(f"{package_id} instalado.")
        else:
            all_ok = False
            logger.warning(f"Erro em {package_id}. Verifique manualmente.")

    pb.finish(f"{total} pacotes processados")
    return all_ok


def copy_network_folders() -> bool:
    """Copia pastas de rede para destinos locais."""
    logger = get_logger()
    print_step("Copiando pastas da rede...")

    folders = CONFIG.get("unc_folders_to_copy", [])
    all_ok = True

    if not folders:
        print(info("Nenhuma pasta configurada"))
        return True

    for source, destination in folders:
        logger.info(f"Copiando: {source} -> {destination}")
        folder_name = os.path.basename(source)

        try:
            with Spinner(f"Copiando {folder_name}..."):
                start = time.time()
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                shutil.copytree(source, destination)
                elapsed = time.time() - start

            print(f"    {Colors.SUCCESS}✓{Colors.RESET} {folder_name} {Colors.MUTED}→ {destination} [{elapsed:.0f}s]{Colors.RESET}")
            logger.success(f"Copiado: {destination}")
        except Exception as e:
            print(f"    {Colors.DANGER}✗{Colors.RESET} {folder_name} — {e}")
            logger.error(f"Falha: {e}")
            all_ok = False

    return all_ok


def install_office() -> bool:
    """Instala o Office (2013 ou 365)."""
    logger = get_logger()
    print_step("Instalando Office...")

    office_version = _select_office_version()

    if office_version == "2013":
        cfg = CONFIG.get("office_installer", {})
        if cfg.get("path"):
            return _run_installer("Office 2013", cfg["path"], cfg.get("args", ""))
    elif office_version == "365":
        cfg = CONFIG.get("office16_365_installer", {})
        if cfg.get("path"):
            return _run_installer("Office 365", cfg["path"], cfg.get("args", ""))
    else:
        print(info("Instalação do Office pulada"))
        logger.info("Office pulado.")

    return False


def _select_office_version() -> str:
    """Seleção interativa de versão do Office."""
    from main import draw_box

    menu_lines = [
        "",
        f"{green('[1]')}  Office 2013 {Colors.MUTED}(Standard SP.01 x64){Colors.RESET}",
        f"{green('[2]')}  Office 365 {Colors.MUTED}(Pacote 2016){Colors.RESET}",
        f"{yellow('[0]')}  Pular instalação do Office",
        "",
    ]

    print("")
    print(draw_box(menu_lines, "VERSÃO DO OFFICE", Colors.PRIMARY))

    while True:
        opcao = styled_input("Versão desejada")
        if opcao == "1":
            return "2013"
        elif opcao == "2":
            return "365"
        elif opcao == "0":
            return ""
        else:
            print(warning("Opção inválida."))


def _run_installer(name: str, path: str, args: str) -> bool:
    """Executa um instalador com Spinner e retorna sucesso."""
    logger = get_logger()

    if not os.path.exists(path):
        logger.error(f"{name}: Arquivo não encontrado: {path}")
        print(error(f"Arquivo não encontrado: {path}"))
        return False

    logger.info(f"Executando: {path}")

    try:
        full_cmd = f'"{path}" {args}'
        start = time.time()

        with Spinner(f"Instalando {name}..."):
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)

        elapsed = time.time() - start

        if result.returncode == 0:
            logger.success(f"{name} instalado.")
            print(f"    {Colors.SUCCESS}✓{Colors.RESET} {name} instalado {Colors.MUTED}[{elapsed:.0f}s]{Colors.RESET}")
            return True
        else:
            logger.warning(f"{name}: Código {result.returncode}")
            print(f"    {Colors.WARN}⚠{Colors.RESET} {name} — Código {result.returncode}")
            return False
    except Exception as e:
        logger.error(f"Falha: {e}")
        print(error(str(e)))
        return False


def create_webapp_shortcut() -> bool:
    """Cria atalho .lnk do WebApp via VBScript."""
    logger = get_logger()
    print_step("Configurando atalho WebApp...")

    webapp_url = CONFIG.get("webapp_url", "")
    webapp_name = CONFIG.get("webapp_name", "WebApp")
    chrome_path = CONFIG.get("chrome_path", "")

    if not webapp_url:
        print(info("URL não configurada"))
        return False

    if not os.path.exists(chrome_path):
        logger.warning(f"Chrome não encontrado: {chrome_path}")
        print(warning("Chrome não no caminho padrão"))

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
            print(error("Chrome não encontrado em nenhum caminho."))
            return False

    logger.info(f"Atalho: {webapp_name} -> {webapp_url}")

    if CONFIG.get("webapp_shortcut_location") == "Desktop":
        shortcut_dir = os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), "Desktop")
    else:
        shortcut_dir = os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"),
                                     "Microsoft", "Windows", "Start Menu", "Programs")

    shortcut_path = os.path.join(shortcut_dir, f"{webapp_name}.lnk")

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
        print(f"    {Colors.SUCCESS}✓{Colors.RESET} Atalho: {Colors.MUTED}{shortcut_path}{Colors.RESET}")
        return True
    except Exception as e:
        logger.error(f"Falha: {e}")
        print(error(str(e)))
        return False
    finally:
        try:
            os.remove(vbs_path)
        except OSError:
            pass


def launch_anydesk() -> bool:
    """Abre o AnyDesk para coleta do ID remoto."""
    logger = get_logger()
    print_step("Abrindo AnyDesk...")

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
            print(f"    {Colors.SUCCESS}✓{Colors.RESET} AnyDesk aberto — {Colors.MUTED}Anote o ID{Colors.RESET}")
            return True
        except Exception as e:
            logger.error(f"Falha: {e}")
            print(error(str(e)))
            return False
    else:
        logger.warning("AnyDesk não encontrado.")
        print(warning("AnyDesk não encontrado."))
        return False
