"""Utilitários comuns."""
import os
import shutil
import ctypes


def get_terminal_width() -> int:
    """Retorna a largura do terminal (mínimo 60, máximo 120)."""
    try:
        width = shutil.get_terminal_size().columns
        return max(60, min(width, 120))
    except Exception:
        return 80


def is_admin() -> bool:
    """Verifica se está executando como Administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return True


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def pause(message: str = "Pressione ENTER para continuar..."):
    input(f"\n{message}")


def print_header(title: str):
    width = 50
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)


def print_step(step: str):
    print(f"\n>> {step}")


def confirm_action(prompt: str) -> bool:
    while True:
        choice = input(f"{prompt} (S/N): ").strip().upper()
        if choice in ('S', 'SIM', 'Y', 'YES'):
            return True
        elif choice in ('N', 'NAO', 'NÃO', 'NO'):
            return False
        else:
            print("Opção inválida. Digite S ou N.")
