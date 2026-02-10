"""Diagnósticos do sistema: winget, rede, caminhos UNC."""
import os
import subprocess
from utils.colors import Colors, success, error, warning, info, gradient_text
from utils.common import print_header, print_step, get_terminal_width
from utils.powershell import run_powershell
from utils.logger import get_logger
from config import CONFIG


DIAGNOSTIC_LABELS = {
    "winget": "Gerenciador de Pacotes (Winget)",
    "network": "Conectividade de Rede",
    "unc_paths": "Caminhos de Rede (UNC)",
}


def _health_bar(passed: int, total: int) -> str:
    """Barra de saúde visual com cor baseada na porcentagem."""
    bar_width = 20
    filled = int((passed / total) * bar_width) if total > 0 else 0
    empty = bar_width - filled
    pct = int((passed / total) * 100) if total > 0 else 0

    if pct == 100:
        bar_color = Colors.SUCCESS
    elif pct >= 60:
        bar_color = Colors.WARN
    else:
        bar_color = Colors.DANGER

    bar = f"{bar_color}{'█' * filled}{Colors.SURFACE}{'░' * empty}{Colors.RESET}"
    return f"{bar} {bar_color}{pct}%{Colors.RESET}"


def run_full_diagnostics():
    """Executa todos os diagnósticos e exibe card de resumo."""
    logger = get_logger()

    print_header("DIAGNÓSTICO DO SISTEMA")
    print(f"  {Colors.MUTED}Executando verificações...{Colors.RESET}\n")

    results = {
        "winget": check_winget(),
        "network": check_network(),
        "unc_paths": check_unc_paths(),
    }

    width = get_terminal_width() - 4
    c = Colors.SURFACE
    r = Colors.RESET

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print("")
    print(f"  {c}╔{'═' * (width - 2)}╗{r}")
    title = "RESUMO DO DIAGNÓSTICO"
    pad = (width - len(title) - 4) // 2
    print(f"  {c}║{r}{' ' * pad}  {Colors.BOLD}{gradient_text(title)}{r}{' ' * (width - len(title) - pad - 4)}{c}║{r}")
    print(f"  {c}╠{'═' * (width - 2)}╣{r}")

    for name, status in results.items():
        label = DIAGNOSTIC_LABELS.get(name, name.upper())
        status_icon = f"{Colors.SUCCESS}✓ OK{r}" if status else f"{Colors.DANGER}✗ FALHA{r}"

        clean_line = f"  {label}  {('✓ OK' if status else '✗ FALHA')}"
        dots_count = width - len(clean_line) - 4
        dots = f"{Colors.SURFACE}{'·' * max(dots_count, 2)}{r}"
        print(f"  {c}║{r}  {label} {dots} {status_icon}  {c}║{r}")

    print(f"  {c}╠{'═' * (width - 2)}╣{r}")

    health = _health_bar(passed, total)
    print(f"  {c}║{r}  Saúde: {health}{'  '}{c}║{r}")

    print(f"  {c}╚{'═' * (width - 2)}╝{r}")
    print("")

    if passed == total:
        print(success(f"Todos os {total} testes passaram!"))
        logger.success("Diagnóstico completo: todos os testes passaram.")
    else:
        print(warning(f"{passed}/{total} testes passaram."))
        logger.warning(f"Diagnóstico: {passed}/{total} testes passaram.")

    return passed == total


def check_winget() -> bool:
    """Verifica se o winget está disponível."""
    print_step("Verificando Winget...")

    try:
        result = subprocess.run(
            ["winget", "--version"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(success(f"Winget encontrado: {result.stdout.strip()}"))
            return True
        else:
            print(error("Winget não está funcionando corretamente."))
            return False
    except FileNotFoundError:
        print(error("Winget não encontrado no sistema."))
        print(info("Instale via Microsoft Store: 'App Installer'"))
        return False
    except subprocess.TimeoutExpired:
        print(error("Timeout ao verificar winget."))
        return False
    except Exception as e:
        print(error(f"Erro ao verificar winget: {e}"))
        return False


def check_network() -> bool:
    """Verifica conectividade de rede."""
    print_step("Verificando conectividade de rede...")

    return_code, stdout, _ = run_powershell(
        "Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet"
    )

    if return_code == 0 and "True" in stdout:
        print(success("Conectividade de rede OK."))
        return True
    else:
        print(warning("Sem acesso à Internet (pode funcionar na rede local)."))
        return True  # Não é crítico para rede local


def check_unc_paths() -> bool:
    """Verifica acesso aos caminhos UNC configurados."""
    print_step("Verificando caminhos de rede (UNC)...")

    folders = CONFIG.get("unc_folders_to_copy", [])

    if not folders:
        print(info("Nenhuma pasta UNC configurada."))
        return True

    all_ok = True

    for source, _ in folders:
        if os.path.exists(source):
            print(f"    {Colors.SUCCESS}✓{Colors.RESET} {source}")
        else:
            print(f"    {Colors.DANGER}✗{Colors.RESET} {source} — {Colors.MUTED}Inacessível{Colors.RESET}")
            all_ok = False

    # Verifica instaladores do Office
    for key in ("office_installer", "office16_365_installer"):
        office_path = CONFIG.get(key, {}).get("path", "")
        if office_path:
            label = "Office 2013" if "16" not in key else "Office 365"
            if os.path.exists(office_path):
                print(f"    {Colors.SUCCESS}✓{Colors.RESET} {label} installer")
            else:
                print(f"    {Colors.DANGER}✗{Colors.RESET} {label} — {Colors.MUTED}Caminho inacessível{Colors.RESET}")
                all_ok = False

    if all_ok:
        print(success("Todos os caminhos de rede acessíveis."))
    else:
        print(warning("Alguns caminhos não estão acessíveis."))

    return all_ok


def open_logs_folder():
    """Abre a pasta de logs no Explorer."""
    logger = get_logger()
    log_dir = os.path.dirname(logger.get_log_path())

    print_step("Abrindo pasta de logs...")
    print(f"    {Colors.MUTED}{log_dir}{Colors.RESET}")

    try:
        os.startfile(log_dir)
        print(success("Pasta de logs aberta."))
    except Exception as e:
        print(error(f"Não foi possível abrir: {e}"))
