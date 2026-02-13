"""Etapa 2: Softwares e configurações pós-login AD."""
import os
import shutil
import subprocess
import time

from config import CONFIG
from utils.console import console, print_header, print_step, print_success, print_error, print_warning, print_info, ask_input
from utils.powershell import run_powershell
from utils.logger import get_logger
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table


def run_full_install():
    """Instalação completa pós-login no domínio."""
    logger = get_logger()
    start_time = time.time()

    print_header("ETAPA 2: INSTALAÇÃO DE SOFTWARES")

    steps = [
        ("Softwares (Chocolatey)", install_choco_packages, "Chrome, WinRAR, Teams, AnyDesk"),
        ("Pastas da Rede", copy_network_folders, "UNC → C:\\"),
        ("Office", install_office, "Instalação Opcional"),
        ("Atalho NextBP", create_webapp_shortcut, ""),
        ("AnyDesk", launch_anydesk, "Anote o ID"),
    ]

    console.print("[dim]Esta etapa irá:[/]")
    for label, _, detail in steps:
        if detail:
            console.print(f"    [blue]•[/] {label} ([dim]{detail}[/])")
        else:
            console.print(f"    [blue]•[/] {label}")
    console.print()

    results = []

    for label, func, detail in steps:
        try:
            ok = func()
            results.append((label, ok, detail))
        except Exception as e:
            logger.error(f"Erro em {label}: {e}")
            results.append((label, False, f"Erro: {e}"))

    elapsed = time.time() - start_time
    logger.success(f"Etapa 2 concluída em {elapsed:.0f}s!")

    # Summary Table
    table = Table(box=None, padding=(0, 2), expand=True)
    table.add_column("Tarefa", style="bold")
    table.add_column("Status", justify="right")
    table.add_column("Detalhes", style="dim white")

    for label, status, detail in results:
        if status is True:
            status_text = "[success]✅ Sucesso[/]"
        elif status is False:
            status_text = "[error]❌ Falha[/]"
        else:
            status_text = "[warning]⏭ Pulado[/]"

        table.add_row(label, status_text, detail)

    console.print()
    console.print(Panel(
        table,
        title="[bold]INSTALAÇÃO CONCLUÍDA[/]",
        subtitle=f"[dim]Tempo total: {elapsed:.0f}s[/]",
        border_style="green",
        padding=(1, 2)
    ))
    console.print()

    return True

CHOCO_BIN_DIR = os.path.join(
    os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "chocolatey", "bin"
)
CHOCO_EXE = os.path.join(CHOCO_BIN_DIR, "choco.exe")


def _get_choco_cmd() -> str:
    """Retorna o caminho do choco.exe, preferindo o caminho completo."""
    if os.path.exists(CHOCO_EXE):
        return f'"{CHOCO_EXE}"'
    return "choco"


def _refresh_path():
    """Adiciona o diretório do Chocolatey ao PATH do processo atual."""
    current_path = os.environ.get("PATH", "")
    if CHOCO_BIN_DIR.lower() not in current_path.lower():
        os.environ["PATH"] = CHOCO_BIN_DIR + ";" + current_path


def ensure_chocolatey() -> bool:
    """Garante que o Chocolatey está instalado no sistema."""
    logger = get_logger()

    _refresh_path()

    if os.path.exists(CHOCO_EXE):
        return_code, stdout, _ = run_powershell(f'"{CHOCO_EXE}" --version', capture_output=True)
        if return_code == 0 and stdout.strip():
            logger.info(f"Chocolatey já instalado: v{stdout.strip()}")
            return True

    logger.info("Chocolatey não encontrado. Instalando...")

    install_cmd = (
        "Set-ExecutionPolicy Bypass -Scope Process -Force; "
        "[System.Net.ServicePointManager]::SecurityProtocol = "
        "[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
        "iex ((New-Object System.Net.WebClient).DownloadString("
        "'https://community.chocolatey.org/install.ps1'))"
    )

    with console.status("[primary]Instalando Chocolatey...[/]"):
        return_code, _, stderr = run_powershell(install_cmd, capture_output=True)

    if return_code == 0:
        _refresh_path()
        logger.success("Chocolatey instalado com sucesso.")
        return True
    else:
        logger.error(f"Falha ao instalar Chocolatey: {stderr}")
        return False


def install_choco_packages() -> bool:
    """Instala pacotes configurados via Chocolatey."""
    logger = get_logger()
    print_step("Instalando softwares via Chocolatey...")

    if not ensure_chocolatey():
        print_error("Não foi possível garantir o Chocolatey. Abortando instalação.")
        return False

    choco = _get_choco_cmd()
    packages = CONFIG.choco_packages
    all_ok = True

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Instalando pacotes...[/]", total=len(packages))

        for idx, entry in enumerate(packages, 1):
            if isinstance(entry, (list, tuple)):
                package_id, extra_args = entry[0], entry[1]
            else:
                package_id, extra_args = entry, ""

            progress.update(task, description=f"[cyan]Instalando {package_id}...[/]")
            logger.info(f"Chocolatey: {package_id}")

            if choco.startswith('"'):
                cmd = f'& {choco} install {package_id} -y --no-progress --ignore-checksums'
            else:
                cmd = f'{choco} install {package_id} -y --no-progress --ignore-checksums'
                
            if extra_args:
                cmd += f' {extra_args}'

            return_code, stdout, _ = run_powershell(cmd, capture_output=True)

            if return_code == 0:
                logger.success(f"{package_id} instalado.")
            elif return_code in (1641, 3010):
                # Reboot necessário — considerado sucesso
                logger.success(f"{package_id} instalado (reboot pendente).")
            else:
                output_lower = stdout.lower() if stdout else ""
                if "already installed" in output_lower or "nothing to do" in output_lower:
                    logger.warning(f"{package_id} já está instalado. Pulando.")
                else:
                    all_ok = False
                    logger.warning(f"Erro em {package_id}. Verifique manualmente.")
            
            progress.advance(task)

    return all_ok


def _count_files(source: str) -> int:
    """Conta o número de arquivos em um diretório."""
    count = 0
    for _, _, files in os.walk(source):
        count += len(files)
    return count


def copy_network_folders() -> bool:
    """Copia pastas de rede para destinos locais com progress bar."""
    logger = get_logger()
    print_step("Copiando pastas da rede...")

    folders = CONFIG.unc_folders_to_copy
    all_ok = True

    if not folders:
        print_info("Nenhuma pasta configurada")
        return True

    for source, destination in folders:
        logger.info(f"Copiando: {source} -> {destination}")
        folder_name = os.path.basename(source)

        try:
            total_files = _count_files(source)
            if total_files == 0:
                total_files = 1

            if os.path.exists(destination):
                shutil.rmtree(destination)

            start = time.time()

            with Progress(
                SpinnerColumn(),
                TextColumn("[cyan]{task.description}"),
                BarColumn(bar_width=30),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task(f"[cyan]Copiando {folder_name}...[/]", total=total_files)

                def _copy_with_progress(src, dst):
                    shutil.copy2(src, dst)
                    progress.advance(task)

                shutil.copytree(source, destination, copy_function=_copy_with_progress)

            elapsed = time.time() - start
            logger.success(f"{folder_name} → {destination} ({elapsed:.0f}s)")
        except Exception as e:
            logger.error(f"{folder_name} — {e}")
            all_ok = False

    return all_ok


def install_office() -> bool:
    """Instala o Office (2013 ou 365)."""
    logger = get_logger()
    print_step("Instalando Office...")

    office_version = _select_office_version()

    if office_version == "2013":
        cfg = CONFIG.office_installer
        if cfg.path:
            return _run_installer("Office 2013", cfg.path, cfg.args)
    elif office_version == "365":
        cfg = CONFIG.office16_365_installer
        if cfg.path:
            return _run_installer("Office 365", cfg.path, cfg.args)
    else:
        logger.info("Instalação do Office pulada.")

    return False


def _select_office_version() -> str:
    """Seleção interativa de versão do Office."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Opção", style="bold green", justify="right")
    table.add_column("Pacote")
    table.add_column("Detalhe", style="dim white")

    table.add_row("[1]", "Office 2013", "Standard SP.01 x64")
    table.add_row("[2]", "Office 365", "Pacote 2016")
    table.add_row("[0]", "[warning]Pular[/]", "")

    console.print()
    console.print(Panel(
        table,
        title="[bold]VERSÃO DO OFFICE[/]",
        border_style="blue",
        padding=(1, 2)
    ))

    while True:
        opcao = ask_input("Versão desejada")
        if opcao == "1": return "2013"
        elif opcao == "2": return "365"
        elif opcao == "0": return ""
        else: print_warning("Opção inválida.")


def _run_installer(name: str, path: str, args: str) -> bool:
    """Executa um instalador com Spinner e retorna sucesso."""
    logger = get_logger()

    if not os.path.exists(path):
        logger.error(f"{name}: Arquivo não encontrado: {path}")
        return False

    logger.info(f"Executando: {path}")

    try:
        cmd = [path] + (args.split() if args else [])
        start = time.time()

        with console.status(f"[primary]Instalando {name}...[/]"):
            result = subprocess.run(cmd, capture_output=True, text=True)

        elapsed = time.time() - start

        if result.returncode == 0:
            logger.success(f"{name} instalado ({elapsed:.0f}s)")
            return True
        else:
            logger.warning(f"{name}: Código {result.returncode}")
            return False
    except Exception as e:
        logger.error(f"Falha: {e}")
        return False


def create_webapp_shortcut() -> bool:
    """Cria atalho .lnk do NextBP via VBScript."""
    logger = get_logger()
    print_step("Configurando atalho NextBP...")

    webapp_url = CONFIG.webapp_url
    webapp_name = CONFIG.webapp_name
    chrome_path = CONFIG.chrome_path

    if not webapp_url:
        print_info("URL não configurada")
        return False

    if not os.path.exists(chrome_path):
        logger.error(f"Chrome não encontrado: {chrome_path}")
        return False

    logger.info(f"Atalho: {webapp_name} -> {webapp_url}")

    if CONFIG.webapp_shortcut_location == "Desktop":
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
        return True
    except Exception as e:
        logger.error(f"Falha: {e}")
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
        os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "chocolatey", "bin", "anydesk.exe"),
        os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "chocolatey", "lib", "anydesk", "tools", "AnyDesk.exe"),
    ]

    for path in anydesk_paths:
        if os.path.exists(path):
            logger.info(f"Abrindo: {path}")
            try:
                subprocess.Popen([path])
                logger.success("AnyDesk aberto — Anote o ID")
                return True
            except Exception as e:
                logger.error(f"Falha ao abrir {path}: {e}")
                return False

    logger.warning("AnyDesk não encontrado.")
    return False
