"""Utilitários comuns de UI para terminal."""
import os
import shutil
import ctypes
import time


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
    from utils.console import console
    console.input(f"\n  [dim]{message}[/]")


def smooth_transition():
    """Transição visual suave entre telas."""
    from utils.console import console
    console.print(f"[dim]{'─' * console.width}[/]")
    time.sleep(0.15)
    clear_screen()
