#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provisionador Corporativo v2.0 — Automação pós-formatação Windows."""
import os
import sys
import time
import random
import socket

from utils.common import is_admin, clear_screen, pause, get_terminal_width, smooth_transition
from utils.logger import get_logger
from utils.console import console, print_error, print_warning, ask_input
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from modules.identity import run_identity_setup
from modules.install import (
    run_full_install,
    install_choco_packages,
    copy_network_folders,
    install_office,
    create_webapp_shortcut,
    launch_anydesk
)
from modules.diagnostics import run_full_diagnostics, open_logs_folder


VERSION = "2.0.0"

LOGO_LINES = [
    "██████╗ ██████╗  ██████╗ ██╗   ██╗██╗███████╗██╗ ██████╗ ███╗   ██╗ █████╗ ██████╗  ██████╗ ██████╗ ",
    "██╔══██╗██╔══██╗██╔═══██╗██║   ██║██║██╔════╝██║██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗",
    "██████╔╝██████╔╝██║   ██║██║   ██║██║███████╗██║██║   ██║██╔██╗ ██║███████║██║  ██║██║   ██║██████╔╝",
    "██╔═══╝ ██╔══██╗██║   ██║╚██╗ ██╔╝██║╚════██║██║██║   ██║██║╚██╗██║██╔══██║██║  ██║██║   ██║██╔══██╗",
    "██║     ██║  ██║╚██████╔╝ ╚████╔╝ ██║███████║██║╚██████╔╝██║ ╚████║██║  ██║██████╔╝╚██████╔╝██║  ██║",
    "╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═══╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝",
]

LOGO_COMPACT = [
    " ██████╗ ██████╗ ██████╗ ██╗   ██╗",
    " ██╔══██╗██╔══██╗██╔══██╗██║   ██║",
    " ██████╔╝██████╔╝██║  ██║╚██╗ ██╔╝",
    " ██╔═══╝ ██╔══██╗██║  ██║ ╚████╔╝ ",
    " ██║     ██║  ██║██████╔╝  ╚██╔╝  ",
    " ╚═╝     ╚═╝  ╚═╝╚═════╝    ╚═╝   ",
]


GRADIENT_COLORS = ["#5f5fff", "#5f87ff", "#5fafff", "#5fd7ff", "#5fffff", "#87ffff"]

TIPS = [
    "Dica: Use [bold]Ctrl+C[/] para cancelar qualquer operação",
    "Dica: Os logs ficam em C:\\ProvisioningLogs",
    "Dica: Execute como Admin para todas as funcionalidades",
    "Dica: A opção [bold]Diagnóstico[/] verifica rede e caminhos UNC",
    "Dica: Use [bold]Instalações Avulsas[/] para escolher individualmente",
]


def _styled_logo(lines: list) -> Text:
    """Aplica gradiente de cores ao logo ASCII."""
    text = Text(justify="center")
    for i, line in enumerate(lines):
        color = GRADIENT_COLORS[i % len(GRADIENT_COLORS)]
        text.append(line + "\n", style=color)
    return text


def _get_local_ip() -> str:
    """Obtém o IP local da máquina."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "N/A"


def _check_choco_available() -> bool:
    """Verifica rapidamente se o Chocolatey está disponível."""
    choco_exe = os.path.join(
        os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "chocolatey", "bin", "choco.exe"
    )
    return os.path.exists(choco_exe)


def get_system_info() -> dict:
    return {
        "hostname": os.environ.get("COMPUTERNAME", "N/A"),
        "username": os.environ.get("USERNAME", "N/A"),
        "domain": os.environ.get("USERDOMAIN", "N/A"),
        "ip": _get_local_ip(),
    }


def show_banner():
    """Banner com ASCII art gradiente e info do sistema."""
    sys_info = get_system_info()

    # Logo com gradiente
    if console.width < 100:
        logo_text = _styled_logo(LOGO_COMPACT)
    else:
        logo_text = _styled_logo(LOGO_LINES)

    # Subtitle
    subtitle = Text("Ultra Displays — Automação de TI", justify="center", style="bold magenta")

    # Version Info
    admin_status = "🛡 Admin" if is_admin() else "⚠ Sem Admin"
    admin_style = "success" if is_admin() else "error"
    version_info = Text.assemble(
        (f"v{VERSION}", "dim white"),
        ("  |  ", "dim white"),
        (admin_status, admin_style),
        justify="center"
    )

    # System Info Grid (agora com IP)
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)

    grid.add_row(
        f"[dim]🖥️ PC:[/]\n[blue]{sys_info['hostname']}[/]",
        f"[dim]👤 Usuário:[/]\n[blue]{sys_info['username']}[/]",
        f"[dim]🌐 Domínio:[/]\n[blue]{sys_info['domain']}[/]",
        f"[dim]📡 IP:[/]\n[blue]{sys_info['ip']}[/]"
    )

    full_content = Align.center(
        Text.assemble(
            logo_text, "\n",
            subtitle, "\n",
            version_info, "\n\n"
        )
    )

    layout = Table.grid(expand=True)
    layout.add_row(full_content)
    layout.add_row("")
    layout.add_row(grid)

    console.print(Panel(
        layout,
        border_style="blue",
        padding=(1, 2)
    ))


def show_menu():
    """Menu principal com rich table e indicadores de status."""
    from utils.console import print_menu

    choco_ok = _check_choco_available()
    choco_indicator = "[success]●[/] Choco OK" if choco_ok else "[error]●[/] Choco N/A"

    items = [
        # Config
        ("", "⚙  CONFIGURAÇÃO", ""),
        ("1", "Nome e Domínio", "Renomeia + ingresso AD"),
        ("", "", ""),

        # Instalação
        ("", "📦  INSTALAÇÃO", ""),
        ("2", "Instalação Completa", f"Tudo automatizado  {choco_indicator}"),
        ("3", "Instalações Avulsas", "Escolha individual"),
        ("", "", ""),

        # Utilidades
        ("", "🔧  UTILIDADES", ""),
        ("4", "Diagnóstico do Sistema", "Verificar tudo"),
        ("5", "Abrir Pasta de Logs", "Histórico"),
        ("", "", ""),

        # Exit
        ("0", "[red]Sair[/]", ""),
    ]
    print_menu("MENU PRINCIPAL", items)


def show_submenu_avulso():
    """Submenu de instalações avulsas com rich."""
    from utils.console import print_menu
    
    clear_screen()
    show_banner()

    items = [
        ("1", "Instalar Softwares", "Chocolatey: Chrome, WinRAR, Teams, AnyDesk"),
        ("2", "Copiar Pastas da Rede", "NextUltraDisplays, NextUltraArt"),
        ("3", "Instalar Office", "Office 2013 ou 365"),
        ("4", "Criar Atalho NextBP", "Atalho Chrome --app"),
        ("5", "Abrir AnyDesk", "Para coletar o ID"),
        ("", "", ""),
        ("0", "[yellow]Voltar[/]", ""),
    ]
    print_menu("INSTALAÇÕES AVULSAS", items)


def show_footer():
    """Footer com versão, hora e dica rotativa."""
    import datetime
    width = get_terminal_width()
    now = datetime.datetime.now().strftime("%H:%M")
    footer = f"Provisionador v{VERSION}  •  {now}"
    pad = (width - len(footer)) // 2
    console.print(f"{' ' * pad}[muted]{footer}[/]")

    tip = random.choice(TIPS)
    console.print(f"  [dim italic]{tip}[/]")
    console.print()


def submenu_avulso_loop():
    """Loop do submenu de instalações avulsas."""
    actions = {
        '1': install_choco_packages,
        '2': copy_network_folders,
        '3': install_office,
        '4': create_webapp_shortcut,
        '5': launch_anydesk,
    }

    while True:
        try:
            show_submenu_avulso()
            show_footer()
            opcao = ask_input("Opção")

            if opcao in actions:
                clear_screen()
                actions[opcao]()
                pause("Pressione ENTER para voltar...")
            elif opcao == '0' or not opcao:
                break
            else:
                print_warning("Opção inválida. Tente novamente.")
                time.sleep(1)

        except KeyboardInterrupt:
            console.print("\n[yellow]Voltando ao menu principal...[/]")
            time.sleep(0.5)
            break


def main_menu():
    """Loop principal do menu interativo."""
    logger = get_logger()
    logger.info(f"Ferramenta iniciada - Versão {VERSION}")

    while True:
        smooth_transition()
        show_banner()
        show_menu()
        show_footer()

        opcao = ask_input("Opção")

        if opcao == '1':
            clear_screen()
            try:
                run_identity_setup()
            except KeyboardInterrupt:
                print_warning("\nOperação cancelada pelo usuário.")
            except Exception as e:
                logger.error(f"Erro na Etapa 1: {e}")
                print_error(f"Erro crítico: {e}")
            pause("Pressione ENTER para voltar ao menu...")

        elif opcao == '2':
            clear_screen()
            try:
                run_full_install()
            except KeyboardInterrupt:
                print_warning("\nInstalação cancelada pelo usuário.")
            except Exception as e:
                logger.error(f"Erro na Etapa 2: {e}")
                print_error(f"Erro crítico: {e}")
            pause("Pressione ENTER para voltar ao menu...")

        elif opcao == '3':
            try:
                submenu_avulso_loop()
            except KeyboardInterrupt:
                print_warning("\nMenu cancelado.")

        elif opcao == '4':
            clear_screen()
            try:
                run_full_diagnostics()
            except KeyboardInterrupt:
                print_warning("\nDiagnóstico cancelado.")
            except Exception as e:
                logger.error(f"Erro no diagnóstico: {e}")
                print_error(f"Erro: {e}")
            pause("Pressione ENTER para voltar ao menu...")

        elif opcao == '5':
            open_logs_folder()
            pause("Pressione ENTER para voltar ao menu...")

        elif opcao == '0' or not opcao:
            logger.info("Ferramenta encerrada pelo usuário.")
            _show_farewell()
            break

        else:
            print_warning("Opção inválida. Tente novamente.")
            time.sleep(1.5)


def _show_farewell():
    width = get_terminal_width()

    console.print("")
    msg = "Até logo! 👋"
    pad = (width - len(msg)) // 2
    console.print(f"{' ' * pad}[success]{msg}[/]")

    sub = "Provisionador encerrado com sucesso."
    pad2 = (width - len(sub)) // 2
    console.print(f"{' ' * pad2}[muted]{sub}[/]")
    console.print("")


def show_admin_error():
    """Erro de privilégios insuficientes."""
    console.print(Panel(
        "[bold red]Esta ferramenta PRECISA ser executada como ADMINISTRADOR.[/]\n\n"
        "Clique com botão direito no .exe e selecione:\n"
        "[yellow]Executar como administrador[/]",
        title="[bold red]⚠ ERRO — PRIVILÉGIOS INSUFICIENTES[/]",
        border_style="red"
    ))


def main():
    if not is_admin():
        show_admin_error()
        console.input(f"\n  [muted]Pressione ENTER para sair...[/]")
        sys.exit(1)

    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n")
        _show_farewell()
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Erro fatal não tratado:[/]\n{e}")
        console.input(f"\n  [muted]Pressione ENTER para sair...[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()
