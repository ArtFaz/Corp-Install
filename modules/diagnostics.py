"""Diagnósticos do sistema: chocolatey, rede, caminhos UNC."""
import os
import subprocess
from utils.console import console, print_header, print_step, print_success, print_error, print_warning, print_info
from rich.table import Table
from rich.panel import Panel
from config import CONFIG
from utils.logger import get_logger
from utils.powershell import run_powershell


DIAGNOSTIC_LABELS = {
    "chocolatey": "Gerenciador de Pacotes (Chocolatey)",
    "network": "Conectividade de Rede",
    "unc_paths": "Caminhos de Rede (UNC)",
}



def run_full_diagnostics():
    """Executa todos os diagnósticos e exibe card de resumo."""
    logger = get_logger()

    print_header("DIAGNÓSTICO DO SISTEMA")
    console.print("[dim]Executando verificações...[/]\n")

    results = {
        "chocolatey": check_chocolatey(),
        "network": check_network(),
        "unc_paths": check_unc_paths(),
    }

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    # Diagnostic Table
    table = Table(box=None, padding=(0, 2), expand=True)
    table.add_column("Item", style="bold")
    table.add_column("Status", justify="right")

    for name, status in results.items():
        label = DIAGNOSTIC_LABELS.get(name, name.upper())
        status_text = "[success]✓ OK[/]" if status else "[error]✗ FALHA[/]"
        table.add_row(label, status_text)

    # Health Bar (Visual)
    pct = (passed / total) * 100 if total > 0 else 0
    bar_color = "green" if pct == 100 else ("yellow" if pct >= 60 else "red")
    filled = int(pct / 10)
    bar = f"[{bar_color}]{'━' * filled}[/][dim]{'━' * (10 - filled)}[/]"
    health_text = f"{bar}  [{bar_color}]{int(pct)}%[/]"

    console.print()
    console.print(Panel(
        table,
        title="[bold]RESUMO DO DIAGNÓSTICO[/]",
        subtitle=health_text,
        border_style="dim white",
        padding=(1, 2)
    ))
    console.print()

    if passed == total:
        print_success(f"Todos os {total} testes passaram!")
        logger.success("Diagnóstico completo: todos os testes passaram.")
    else:
        print_warning(f"{passed}/{total} testes passaram.")
        logger.warning(f"Diagnóstico: {passed}/{total} testes passaram.")

    return passed == total


def check_chocolatey() -> bool:
    """Verifica se o Chocolatey está disponível."""
    print_step("Verificando Chocolatey...")

    choco_exe = os.path.join(
        os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "chocolatey", "bin", "choco.exe"
    )

    if not os.path.exists(choco_exe):
        print_error("Chocolatey não encontrado no sistema.")
        print_info("Será instalado automaticamente na primeira instalação.")
        return False

    try:
        result = subprocess.run(
            [choco_exe, "--version"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            print_success(f"Chocolatey encontrado: v{result.stdout.strip()}")
            return True
        else:
            print_error("Chocolatey não está funcionando corretamente.")
            return False
    except subprocess.TimeoutExpired:
        print_error("Timeout ao verificar Chocolatey.")
        return False
    except Exception as e:
        print_error(f"Erro ao verificar Chocolatey: {e}")
        return False


def check_network() -> bool:
    """Verifica conectividade de rede."""
    print_step("Verificando conectividade de rede...")

    return_code, stdout, _ = run_powershell(
        "Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet"
    )

    if return_code == 0 and "True" in stdout:
        print_success("Conectividade de rede OK.")
        return True
    else:
        print_warning("Sem acesso à Internet (pode funcionar na rede local).")
        return True  # Não é crítico para rede local


def check_unc_paths() -> bool:
    """Verifica acesso aos caminhos UNC configurados."""
    print_step("Verificando caminhos de rede (UNC)...")

    folders = CONFIG.unc_folders_to_copy

    if not folders:
        print_info("Nenhuma pasta UNC configurada.")
        return True

    all_ok = True

    for cfg in folders:
        if os.path.exists(cfg.source):
            print_success(f"{cfg.source}")
        else:
            print_error(f"{cfg.source} — [dim]Inacessível[/]")
            all_ok = False

    # Verifica instaladores do Office
    office_configs = [
        ("Office 2013", CONFIG.office_installer),
        ("Office 365", CONFIG.office16_365_installer)
    ]

    for label, cfg in office_configs:
        office_path = cfg.path
        if office_path:
            if os.path.exists(office_path):
                print_success(f"{label} installer")
            else:
                print_error(f"{label} — [dim]Caminho inacessível[/]")
                all_ok = False

    if all_ok:
        print_success("Todos os caminhos de rede acessíveis.")
    else:
        print_warning("Alguns caminhos não estão acessíveis.")

    return all_ok


def open_logs_folder():
    """Abre a pasta de logs no Explorer."""
    logger = get_logger()
    log_dir = os.path.dirname(logger.get_log_path())

    print_step("Abrindo pasta de logs...")
    console.print(f"    [dim]{log_dir}[/]")

    try:
        os.startfile(log_dir)
        print_success("Pasta de logs aberta.")
    except Exception as e:
        print_error(f"Não foi possível abrir: {e}")
