"""Utilitários comuns de UI para terminal."""
import os
import shutil
import ctypes


def get_terminal_width() -> int:
    """Largura do terminal (min 60, max 120)."""
    try:
        width = shutil.get_terminal_size().columns
        return max(60, min(width, 120))
    except Exception:
        return 80


def is_admin() -> bool:
    """Verifica privilégios de Administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return True


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def pause(message: str = "Pressione ENTER para continuar..."):
    from utils.colors import Colors
    input(f"\n  {Colors.MUTED}{message}{Colors.RESET}")


def print_header(title: str):
    """Header com bordas Unicode e título em gradiente."""
    from utils.colors import Colors, gradient_text
    width = get_terminal_width() - 4
    c = Colors.SURFACE
    r = Colors.RESET

    styled_title = gradient_text(title)
    padding_total = width - len(title) - 4
    pad_left = padding_total // 2
    pad_right = padding_total - pad_left

    print("")
    print(f"  {c}╔{'═' * (width - 2)}╗{r}")
    print(f"  {c}║{r}{' ' * pad_left}  {styled_title}{' ' * pad_right}{c}║{r}")
    print(f"  {c}╚{'═' * (width - 2)}╝{r}")
    print("")


def print_step(step: str):
    from utils.colors import Colors
    print(f"\n  {Colors.PRIMARY}▸{Colors.RESET} {step}")


def print_section(icon: str, label: str):
    from utils.colors import Colors
    print(f"\n   {icon} {Colors.BOLD}{label}{Colors.RESET}")
    print(f"   {Colors.SURFACE}{'─' * 25}{Colors.RESET}")


def print_divider():
    from utils.colors import Colors
    width = get_terminal_width() - 8
    print(f"    {Colors.SURFACE}{'─' * width}{Colors.RESET}")


def confirm_action(prompt: str) -> bool:
    """Wrapper para styled_confirm."""
    from utils.colors import styled_confirm
    return styled_confirm(prompt)
