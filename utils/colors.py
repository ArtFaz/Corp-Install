"""Cores ANSI e paleta temática para terminal Windows."""
import sys


def _enable_ansi_colors():
    """Habilita suporte a cores ANSI no terminal Windows."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


_enable_ansi_colors()


class Colors:
    """Códigos de cores ANSI com paleta semântica."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BG_MAGENTA = "\033[45m"
    BG_WHITE = "\033[47m"

    # Paleta semântica (256 cores)
    PRIMARY = "\033[38;5;39m"
    ACCENT = "\033[38;5;213m"
    SURFACE = "\033[38;5;245m"
    MUTED = "\033[38;5;242m"
    SUCCESS = "\033[38;5;82m"
    DANGER = "\033[38;5;196m"
    WARN = "\033[38;5;214m"
    INFO_COLOR = "\033[38;5;75m"
    HIGHLIGHT = "\033[38;5;229m"

    # Gradiente cyan → azul
    GRAD_1 = "\033[38;5;51m"
    GRAD_2 = "\033[38;5;45m"
    GRAD_3 = "\033[38;5;39m"
    GRAD_4 = "\033[38;5;33m"
    GRAD_5 = "\033[38;5;27m"


# Wrappers básicos
def green(text: str) -> str:
    return f"{Colors.GREEN}{text}{Colors.RESET}"

def red(text: str) -> str:
    return f"{Colors.RED}{text}{Colors.RESET}"

def yellow(text: str) -> str:
    return f"{Colors.YELLOW}{text}{Colors.RESET}"

def cyan(text: str) -> str:
    return f"{Colors.CYAN}{text}{Colors.RESET}"

def blue(text: str) -> str:
    return f"{Colors.BLUE}{text}{Colors.RESET}"

def magenta(text: str) -> str:
    return f"{Colors.MAGENTA}{text}{Colors.RESET}"

def gray(text: str) -> str:
    return f"{Colors.GRAY}{text}{Colors.RESET}"

def bold(text: str) -> str:
    return f"{Colors.BOLD}{text}{Colors.RESET}"

def dim(text: str) -> str:
    return f"{Colors.DIM}{text}{Colors.RESET}"


# Wrappers semânticos
def primary(text: str) -> str:
    return f"{Colors.PRIMARY}{text}{Colors.RESET}"

def accent(text: str) -> str:
    return f"{Colors.ACCENT}{text}{Colors.RESET}"

def muted(text: str) -> str:
    return f"{Colors.MUTED}{text}{Colors.RESET}"

def surface(text: str) -> str:
    return f"{Colors.SURFACE}{text}{Colors.RESET}"

def highlight(text: str) -> str:
    return f"{Colors.HIGHLIGHT}{text}{Colors.RESET}"


# Formatadores de status
def success(text: str) -> str:
    return f"  {Colors.SUCCESS}✓{Colors.RESET} {text}"

def error(text: str) -> str:
    return f"  {Colors.DANGER}✗{Colors.RESET} {Colors.RED}{text}{Colors.RESET}"

def warning(text: str) -> str:
    return f"  {Colors.WARN}⚠{Colors.RESET} {text}"

def info(text: str) -> str:
    return f"  {Colors.INFO_COLOR}●{Colors.RESET} {text}"


def step_status(step_num: int, total: int, text: str, status: str = "running") -> str:
    """Indicador de etapa com contagem. status: running | done | error | skip"""
    counter = f"{Colors.MUTED}[{step_num}/{total}]{Colors.RESET}"
    icons = {
        "running": f"{Colors.PRIMARY}▶{Colors.RESET}",
        "done": f"{Colors.SUCCESS}✓{Colors.RESET}",
        "error": f"{Colors.DANGER}✗{Colors.RESET}",
        "skip": f"{Colors.MUTED}○{Colors.RESET}",
    }
    icon = icons.get(status, icons["running"])
    return f"  {counter} {icon} {text}"


# Input estilizado
def styled_input(prompt: str = "") -> str:
    display_prompt = prompt if prompt else "Selecione"
    full_prompt = f"  {Colors.PRIMARY}❯{Colors.RESET} {display_prompt}: "
    try:
        return input(full_prompt).strip()
    except (KeyboardInterrupt, EOFError):
        return ""


def styled_confirm(prompt: str) -> bool:
    """Confirmação [S]im / [N]ão."""
    while True:
        styled_prompt = (
            f"  {Colors.PRIMARY}?{Colors.RESET} {prompt} "
            f"[{Colors.GREEN}S{Colors.RESET}]im / "
            f"[{Colors.RED}N{Colors.RESET}]ão: "
        )
        try:
            choice = input(styled_prompt).strip().upper()
        except (KeyboardInterrupt, EOFError):
            return False

        if choice in ('S', 'SIM', 'Y', 'YES'):
            return True
        elif choice in ('N', 'NAO', 'NÃO', 'NO'):
            return False
        else:
            print(warning("Opção inválida. Digite S ou N."))


# Gradiente
def gradient_text(text: str) -> str:
    """Aplica gradiente cyan→azul ao texto."""
    gradient = [Colors.GRAD_1, Colors.GRAD_2, Colors.GRAD_3, Colors.GRAD_4, Colors.GRAD_5]
    if not text:
        return text

    result = []
    chars = list(text)
    step = max(1, len(chars) // len(gradient))

    for i, char in enumerate(chars):
        color_idx = min(i // step, len(gradient) - 1)
        result.append(f"{gradient[color_idx]}{char}")

    result.append(Colors.RESET)
    return "".join(result)
