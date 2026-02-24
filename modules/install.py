"""Etapa 2: Softwares e configurações pós-login AD."""
import os
import shutil
import subprocess
import time

from config import CONFIG
from utils.console import console, print_header, print_step, print_success, print_error, print_warning, print_info, ask_input, confirm_action
from utils.powershell import run_powershell
from utils.logger import get_logger
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table


def _retry(func, max_attempts: int = 3, label: str = "operação"):
    """Executa func com retry progressivo. Retorna o resultado ou levanta a última exceção."""
    logger = get_logger()
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts:
                raise
            wait = attempt * 2
            logger.warning(f"{label}: tentativa {attempt}/{max_attempts} falhou — retry em {wait}s...")
            time.sleep(wait)


def _pre_flight_check() -> bool:
    """Verifica acessibilidade dos caminhos UNC antes de iniciar."""
    logger = get_logger()
    print_step("Verificação pré-voo...")

    folders = CONFIG.unc_folders_to_copy
    failed = []

    for cfg in folders:
        if not os.path.exists(cfg.source):
            failed.append(cfg.source)

    if not failed:
        print_success("Todos os caminhos de rede acessíveis.")
        return True

    for path in failed:
        print_error(f"Inacessível: {path}")

    logger.warning(f"Pré-voo: {len(failed)} caminho(s) inacessível(is).")
    return confirm_action("Alguns caminhos estão inacessíveis. Deseja prosseguir mesmo assim?")


STEP_KEYS = {
    "chocolatey": "Softwares (Chocolatey)",
    "sqlncli": "SQL Native Client",
    "folders": "Pastas da Rede",
    "office": "Office",
    "shortcut": "Atalho NextBP",
    "anydesk": "AnyDesk",
}


def run_full_install(skip_steps: list = None, office_version: str = None):
    """Instalação completa pós-login no domínio.

    skip_steps: lista de chaves a pular (chocolatey, folders, office, shortcut, anydesk).
    office_version: '2013', '365' ou '' para pular (modo automático).
    """
    logger = get_logger()
    start_time = time.time()
    skip = set(skip_steps or [])

    print_header("ETAPA 2: INSTALAÇÃO DE SOFTWARES")

    if not _pre_flight_check():
        print_warning("Instalação cancelada pelo usuário.")
        return False

    all_steps = [
        ("chocolatey", "Softwares (Chocolatey)", lambda: install_choco_packages(), "Chrome, WinRAR, Teams, AnyDesk"),
        ("sqlncli", "SQL Native Client", lambda: install_sql_native_client(), "SQL Server Native Client 2012"),
        ("folders", "Pastas da Rede", lambda: copy_network_folders(), "UNC → C:\\"),
        ("office", "Office", lambda: install_office(office_version=office_version), "Instalação Opcional"),
        ("power", "Plano de Energia", lambda: configure_power_plan(), "Anti-hibernação (High Performance)"),
        ("shortcut", "Atalho NextBP", lambda: create_webapp_shortcut(), ""),
        ("anydesk", "AnyDesk", lambda: launch_anydesk(), "Acesso não supervisionado"),
    ]

    steps = [(key, label, func, detail) for key, label, func, detail in all_steps if key not in skip]

    if skip:
        skipped_labels = [STEP_KEYS[s] for s in skip if s in STEP_KEYS]
        if skipped_labels:
            print_info(f"Pulando: {', '.join(skipped_labels)}")

    console.print("[dim]Esta etapa irá:[/]")
    for _, label, _, detail in steps:
        if detail:
            console.print(f"    [blue]•[/] {label} ([dim]{detail}[/])")
        else:
            console.print(f"    [blue]•[/] {label}")
    console.print()

    results = []

    for _, label, func, detail in steps:
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

            def _do_install(c=cmd, pid=package_id):
                rc, out, _ = run_powershell(c, capture_output=True)
                if rc == 0:
                    return True, "ok", out
                if rc in (1641, 3010):
                    return True, "reboot", out
                out_lower = out.lower() if out else ""
                if "already installed" in out_lower or "nothing to do" in out_lower:
                    return True, "skip", out
                raise RuntimeError(f"{pid} retornou código {rc}")

            try:
                ok, reason, _ = _retry(_do_install, max_attempts=2, label=package_id)
                if reason == "reboot":
                    logger.success(f"{package_id} instalado (reboot pendente).")
                elif reason == "skip":
                    logger.warning(f"{package_id} já está instalado. Pulando.")
                else:
                    logger.success(f"{package_id} instalado.")
            except Exception:
                all_ok = False
                logger.warning(f"Erro em {package_id}. Verifique manualmente.")

            progress.advance(task)

    return all_ok


def install_sql_native_client() -> bool:
    """Instala o SQL Server Native Client 2012."""
    logger = get_logger()
    print_step("Instalando SQL Native Client...")

    cfg = getattr(CONFIG, "sql_native_client_installer", None)
    if not cfg or not cfg.path:
        return False

    if not os.path.exists(cfg.path):
        logger.error(f"SQL Native Client: Arquivo não encontrado: {cfg.path}")
        return False

    logger.info(f"Executando: {cfg.path}")
    
    # Executa silenciosamente via msiexec
    cmd = f'Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"{cfg.path}`" /qn /norestart IACCEPTSQLNCLILICENSETERMS=YES" -Wait -NoNewWindow'
    
    start = time.time()
    with console.status("[primary]Instalando SQL Native Client 2012...[/]"):
        return_code, stdout, stderr = run_powershell(cmd, capture_output=True)
        
    elapsed = time.time() - start
    
    if return_code == 0:
        logger.success(f"SQL Native Client instalado ({elapsed:.0f}s)")
        return True
    else:
        logger.error(f"Falha ao instalar SQL Native Client. Código: {return_code}")
        return False


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

    for cfg in folders:
        logger.info(f"Copiando: {cfg.source} -> {cfg.destination}")
        folder_name = os.path.basename(cfg.source)

        def _do_copy(src=cfg.source, dst=cfg.destination, name=folder_name, shortcut_info=cfg.shortcut):
            total_files = _count_files(src)
            if total_files == 0:
                total_files = 1

            if os.path.exists(dst):
                shutil.rmtree(dst)

            start = time.time()

            with Progress(
                SpinnerColumn(),
                TextColumn("[cyan]{task.description}"),
                BarColumn(bar_width=30),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task(f"[cyan]Copiando {name}...[/]", total=total_files)

                def _copy_with_progress(s, d):
                    shutil.copy2(s, d)
                    progress.advance(task)

                shutil.copytree(src, dst, copy_function=_copy_with_progress)

            elapsed = time.time() - start
            logger.success(f"{name} → {dst} ({elapsed:.0f}s)")
            
            if shortcut_info:
                exe_path = os.path.join(dst, shortcut_info.target_exe)
                _create_desktop_shortcut(exe_path, shortcut_info.name)

        try:
            _retry(_do_copy, max_attempts=3, label=folder_name)
        except Exception as e:
            logger.error(f"{folder_name} — {e}")
            all_ok = False

    return all_ok


def install_office(office_version: str = None) -> bool:
    """Instala o Office (2013 ou 365).

    office_version: se fornecido, pula seleção interativa.
    """
    logger = get_logger()
    print_step("Instalando Office...")

    if office_version is None:
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


def _create_desktop_shortcut(target_exe: str, shortcut_name: str) -> bool:
    """Cria um atalho na Área de Trabalho Pública (Geral) para um executável local."""
    logger = get_logger()
    
    if not os.path.exists(target_exe):
        logger.warning(f"Executável alvo do atalho não encontrado: {target_exe}")
        return False
        
    shortcut_dir = os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), "Desktop")
    shortcut_path = os.path.join(shortcut_dir, f"{shortcut_name}.lnk")
    
    vbs_script = f'''
Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{shortcut_path}")
Shortcut.TargetPath = "{target_exe}"
Shortcut.WorkingDirectory = "{os.path.dirname(target_exe)}"
Shortcut.Description = "{shortcut_name}"
Shortcut.Save
'''
    vbs_path = os.path.join(os.environ.get("TEMP", "/tmp"), f"create_{shortcut_name.replace(' ', '')}.vbs")
    try:
        with open(vbs_path, 'w', encoding='utf-8') as f:
            f.write(vbs_script)

        subprocess.run(["cscript", "//Nologo", vbs_path], capture_output=True)
        logger.info(f"Atalho local criado: {shortcut_name}")
        return True
    except Exception as e:
        logger.error(f"Falha ao criar atalho para {shortcut_name}: {e}")
        return False
    finally:
        try:
            os.remove(vbs_path)
        except OSError:
            pass


def configure_power_plan() -> bool:
    """Configura o Windows para Alto Desempenho e impede hibernação/suspensão da tela e disco."""
    logger = get_logger()
    print_step("Configurando Plano de Energia...")

    commands = [
        ("Ativando Alta Performance", "powercfg /SETACTIVE 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"),
        ("Desativando suspensão do monitor", "powercfg /change standby-timeout-ac 0"),
        ("Desativando hibernação", "powercfg /change hibernate-timeout-ac 0"),
        ("Desativando suspensão de disco", "powercfg /change disk-timeout-ac 0")
    ]

    all_ok = True
    for desc, cmd in commands:
        logger.info(f"{desc}: {cmd}")
        return_code, _, _ = run_powershell(cmd, capture_output=True)
        if return_code != 0:
            logger.warning(f"Aviso ao executar: {desc}")
            all_ok = False
            
    if all_ok:
        logger.success("Plano de energia corporativo aplicado (Anti-hibernação)")
        return True
    return False


def launch_anydesk() -> bool:
    """Aplica a senha mestre não supervisionada via arquivo oculto de rede e abre o AnyDesk."""
    logger = get_logger()
    print_step("Configurando Acesso Remoto (AnyDesk)...")

    anydesk_paths = [
        r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe",
        r"C:\Program Files\AnyDesk\AnyDesk.exe",
        os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "AnyDesk", "AnyDesk.exe"),
        os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "chocolatey", "bin", "anydesk.exe"),
        os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "chocolatey", "lib", "anydesk", "tools", "AnyDesk.exe"),
    ]

    exe_path = None
    for path in anydesk_paths:
        if os.path.exists(path):
            exe_path = path
            break

    if not exe_path:
        logger.warning("AnyDesk não encontrado no sistema.")
        return False

    logger.info(f"Executável: {exe_path}")

    # Processamento seguro da senha
    secret_file = getattr(CONFIG, "anydesk_secret_file", None)
    if secret_file and os.path.exists(secret_file):
        try:
            with open(secret_file, "r", encoding="utf-8") as f:
                senha = f.read().strip()
            
            if senha:
                logger.info("Injetando senha mestre lida do servidor UNC...")
                # O AnyDesk CLI aceita receber a senha via pipe stdin
                process = subprocess.Popen([exe_path, "--set-password"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate(input=senha.encode())
                
                if process.returncode == 0:
                    logger.success("Senha autônoma configurada com sucesso!")
                else:
                    logger.warning("Ocorreu um erro ao definir a senha silenciosa do AnyDesk.")
        except Exception as e:
            logger.error(f"Não foi possível aplicar a senha do arquivo seguro: {e}")
    else:
        logger.info("Nenhum arquivo de senha ('anydesk_secret_file') encontrado. Pulando config de acesso autônomo.")

    # Inicia a Interface
    try:
        subprocess.Popen([exe_path])
        logger.success("AnyDesk iniciado!")
        return True
    except Exception as e:
        logger.error(f"Falha ao iniciar {exe_path}: {e}")
        return False
