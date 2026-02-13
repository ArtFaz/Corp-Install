"""Central module for Rich console and UI helpers."""
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

custom_theme = Theme({
    "info": "color(75)",
    "warning": "color(214)",
    "error": "color(196)",
    "success": "color(82)",
    "primary": "color(39)",
    "muted": "color(242)",
    "highlight": "color(229)",
    "accent": "color(213)",
})

console = Console(theme=custom_theme, force_terminal=True)


def ask_input(prompt: str, default: str = None) -> str:
    return Prompt.ask(f"  [primary]>[/] {prompt}", default=default)


def confirm_action(prompt: str) -> bool:
    return Confirm.ask(f"  [primary]?[/] {prompt}")


def print_header(title: str, subtitle: str = ""):
    console.print()
    console.print(Panel(
        Text(title, justify="center", style="bold white"),
        subtitle=subtitle, style="primary", border_style="primary", padding=(1, 2),
    ))
    console.print()


def print_step(message: str):
    console.print(f"[primary]>>[/] {message}")


def print_success(message: str):
    console.print(f"  [success]✓[/] {message}")


def print_error(message: str):
    console.print(f"  [error]✗[/] {message}")


def print_warning(message: str):
    console.print(f"  [warning]⚠[/] {message}")


def print_info(message: str):
    console.print(f"  [info]●[/] {message}")


def print_menu(title: str, items: list):
    from rich.table import Table

    table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    table.add_column("Opção", justify="right", style="success", width=6)
    table.add_column("Descrição", justify="left")
    table.add_column("Detalhe", justify="left", style="dim white")

    for key, desc, detail in items:
        if not key and desc:
            table.add_row("", f"[bold]{desc}[/]", "")
        elif not key and not desc:
            table.add_row("", "", "")
        else:
            table.add_row(f"[{key}]" if key else "", desc, detail)

    console.print(Panel(
        table, title=f"[bold]{title}[/]", border_style="dim white", padding=(1, 2)
    ))
