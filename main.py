#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provisionador Corporativo v2.0 — Automação pós-formatação Windows."""
import os
import re
import sys
import time

from utils.common import is_admin, clear_screen, pause, get_terminal_width
from utils.logger import get_logger
from utils.colors import (
    Colors, green, red, yellow, cyan, bold, success, error, warning, info,
    gradient_text, styled_input, muted
)
from modules.identity import run_identity_setup
from modules.install import (
    run_full_install,
    install_winget_packages,
    copy_network_folders,
    install_office,
    create_webapp_shortcut,
    launch_anydesk
)
from modules.diagnostics import run_full_diagnostics, open_logs_folder
from utils.progress import smooth_transition


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


def _strip_ansi(text: str) -> str:
    """Remove códigos ANSI para cálculo de largura visual."""
    return re.sub(r'\033\[[^m]*m', '', text)


def draw_box(lines: list, title: str = None, color: str = None) -> str:
    """Caixa com bordas Unicode adaptada à largura do terminal."""
    width = get_terminal_width() - 4
    c = color or Colors.SURFACE
    r = Colors.RESET

    result = []

    if title:
        title_display = f" {title} "
        padding = width - len(title_display) - 2
        result.append(f"  {c}╔{title_display}{'═' * padding}╗{r}")
    else:
        result.append(f"  {c}╔{'═' * (width - 2)}╗{r}")

    for line in lines:
        display_line = line
        if len(line) > width - 4:
            display_line = line[:width - 7] + "..."
        padding = width - len(display_line) - 4
        result.append(f"  {c}║{r}  {display_line}{' ' * padding}{c}║{r}")

    result.append(f"  {c}╚{'═' * (width - 2)}╝{r}")
    return "\n".join(result)


def get_system_info() -> dict:
    return {
        "hostname": os.environ.get("COMPUTERNAME", "N/A"),
        "username": os.environ.get("USERNAME", "N/A"),
        "domain": os.environ.get("USERDOMAIN", "N/A"),
    }


def show_banner():
    """Banner com ASCII art, info do sistema e status admin."""
    width = get_terminal_width()
    sys_info = get_system_info()
    grad = [Colors.GRAD_1, Colors.GRAD_2, Colors.GRAD_3, Colors.GRAD_4, Colors.GRAD_5]
    r = Colors.RESET

    logo = LOGO_COMPACT if width < 105 else LOGO_LINES

    print("")
    print(f"  {Colors.SURFACE}{'═' * (width - 4)}{r}")
    print("")

    for i, line in enumerate(logo):
        color = grad[i % len(grad)]
        pad = max(0, (width - len(line)) // 2)
        print(f"{' ' * pad}{color}{line}{r}")

    print("")

    subtitle = "Ultra Displays — Automação de TI"
    pad_sub = (width - len(subtitle)) // 2
    print(f"{' ' * pad_sub}{gradient_text(subtitle)}")

    admin_status = f"{Colors.SUCCESS}🛡 Admin{r}" if is_admin() else f"{Colors.DANGER}⚠ Sem Admin{r}"
    clean_meta = f"v{VERSION}  |  Admin"
    meta_line = f"{Colors.MUTED}v{VERSION}{r}  {Colors.SURFACE}│{r}  {admin_status}"
    pad_meta = (width - len(clean_meta)) // 2
    print(f"{' ' * pad_meta}{meta_line}")

    print("")

    c = Colors.SURFACE
    info_width = min(width - 4, 60)
    pad_card = (width - info_width - 4) // 2

    items = [
        ("🖥️  PC", sys_info['hostname']),
        ("👤  Usuário", sys_info['username']),
        ("🌐  Domínio", sys_info['domain']),
    ]

    print(f"{' ' * pad_card}  {c}┌{'─' * (info_width - 2)}┐{r}")
    for icon_label, value in items:
        clean_item = f"  {icon_label}: {value}"
        styled_item = f"  {Colors.MUTED}{icon_label}:{r} {Colors.PRIMARY}{value}{r}"
        padding = info_width - len(clean_item) - 3
        print(f"{' ' * pad_card}  {c}│{r}{styled_item}{' ' * max(padding, 1)}{c}│{r}")
    print(f"{' ' * pad_card}  {c}└{'─' * (info_width - 2)}┘{r}")

    print("")
    print(f"  {Colors.SURFACE}{'═' * (width - 4)}{r}")
    print("")


def show_menu():
    """Menu principal com categorias visuais."""
    width = get_terminal_width() - 4
    c = Colors.SURFACE
    r = Colors.RESET

    print(f"  {c}╔{'═' * (width - 2)}╗{r}")

    title = "MENU PRINCIPAL"
    pad = (width - len(title) - 4) // 2
    print(f"  {c}║{r}{' ' * pad}  {Colors.BOLD}{title}{r}{' ' * (width - len(title) - pad - 4)}{c}║{r}")
    print(f"  {c}╠{'═' * (width - 2)}╣{r}")

    sections = [
        ("", ""),
        ("   ⚙  CONFIGURAÇÃO", "section"),
        (f"   {Colors.SURFACE}{'─' * 30}{r}", "divider"),
        (f"    {green('[1]')}  Nome e Domínio          {Colors.MUTED}→ Renomeia + ingresso AD{r}", "item"),
        ("", ""),
        ("   📦  INSTALAÇÃO", "section"),
        (f"   {Colors.SURFACE}{'─' * 30}{r}", "divider"),
        (f"    {green('[2]')}  Instalação Completa     {Colors.MUTED}→ Tudo automatizado{r}", "item"),
        (f"    {cyan('[3]')}  Instalações Avulsas     {Colors.MUTED}→ Escolha individual{r}", "item"),
        ("", ""),
        ("   🔧  UTILIDADES", "section"),
        (f"   {Colors.SURFACE}{'─' * 30}{r}", "divider"),
        (f"    {yellow('[4]')}  Diagnóstico do Sistema  {Colors.MUTED}→ Verificar tudo{r}", "item"),
        (f"    {yellow('[5]')}  Abrir Pasta de Logs     {Colors.MUTED}→ Histórico{r}", "item"),
        ("", ""),
        (f"   {Colors.SURFACE}{'─' * 30}{r}", "divider"),
        (f"    {red('[0]')}  Sair", "item"),
        ("", ""),
    ]

    for line_text, _ in sections:
        if not line_text:
            print(f"  {c}║{r}{' ' * (width - 2)}{c}║{r}")
        else:
            clean = _strip_ansi(line_text)
            padding = width - len(clean) - 2
            print(f"  {c}║{r}{line_text}{' ' * max(padding, 1)}{c}║{r}")

    print(f"  {c}╚{'═' * (width - 2)}╝{r}")
    print("")


def show_submenu_avulso():
    """Submenu de instalações avulsas."""
    clear_screen()
    show_banner()

    width = get_terminal_width() - 4
    c = Colors.SURFACE
    r = Colors.RESET

    print(f"  {c}╔{'═' * (width - 2)}╗{r}")

    title = "INSTALAÇÕES AVULSAS"
    pad = (width - len(title) - 4) // 2
    print(f"  {c}║{r}{' ' * pad}  {Colors.BOLD}{title}{r}{' ' * (width - len(title) - pad - 4)}{c}║{r}")
    print(f"  {c}╠{'═' * (width - 2)}╣{r}")

    items = [
        "",
        f"    {green('[1]')}  Instalar Softwares      {Colors.MUTED}→ Chrome, WinRAR, Teams, AnyDesk{r}",
        f"    {green('[2]')}  Copiar Pastas da Rede    {Colors.MUTED}→ NextUltraDisplays, NextUltraArt{r}",
        f"    {green('[3]')}  Instalar Office          {Colors.MUTED}→ Office 2013 ou 365{r}",
        f"    {green('[4]')}  Criar Atalho WebApp      {Colors.MUTED}→ Atalho Chrome --app{r}",
        f"    {green('[5]')}  Abrir AnyDesk            {Colors.MUTED}→ Para coletar o ID{r}",
        "",
        f"   {Colors.SURFACE}{'─' * 30}{r}",
        f"    {yellow('[0]')}  Voltar ao Menu Principal",
        "",
    ]

    for line_text in items:
        if not line_text:
            print(f"  {c}║{r}{' ' * (width - 2)}{c}║{r}")
        else:
            clean = _strip_ansi(line_text)
            padding = width - len(clean) - 2
            print(f"  {c}║{r}{line_text}{' ' * max(padding, 1)}{c}║{r}")

    print(f"  {c}╚{'═' * (width - 2)}╝{r}")
    print("")


def show_footer():
    """Footer discreto com versão e hora."""
    import datetime
    width = get_terminal_width()
    now = datetime.datetime.now().strftime("%H:%M")
    footer = f"Provisionador v{VERSION}  •  {now}"
    pad = (width - len(footer)) // 2
    print(f"{' ' * pad}{Colors.MUTED}{footer}{Colors.RESET}")


def submenu_avulso_loop():
    """Loop do submenu de instalações avulsas."""
    logger = get_logger()

    while True:
        show_submenu_avulso()
        show_footer()

        opcao = styled_input("Opção")

        if opcao == '1':
            clear_screen()
            install_winget_packages()
            pause("Pressione ENTER para voltar...")

        elif opcao == '2':
            clear_screen()
            copy_network_folders()
            pause("Pressione ENTER para voltar...")

        elif opcao == '3':
            clear_screen()
            install_office()
            pause("Pressione ENTER para voltar...")

        elif opcao == '4':
            clear_screen()
            create_webapp_shortcut()
            pause("Pressione ENTER para voltar...")

        elif opcao == '5':
            clear_screen()
            launch_anydesk()
            pause("Pressione ENTER para voltar...")

        elif opcao == '0' or not opcao:
            break

        else:
            print(warning("Opção inválida. Tente novamente."))
            time.sleep(1)


def main_menu():
    """Loop principal do menu interativo."""
    logger = get_logger()
    logger.info(f"Ferramenta iniciada - Versão {VERSION}")

    while True:
        clear_screen()
        show_banner()
        show_menu()
        show_footer()

        opcao = styled_input("Opção")

        if opcao == '1':
            smooth_transition("Abrindo configuração...")
            clear_screen()
            try:
                run_identity_setup()
            except Exception as e:
                logger.error(f"Erro na Etapa 1: {e}")
                print(error(f"Erro crítico: {e}"))
            pause("Pressione ENTER para voltar ao menu...")

        elif opcao == '2':
            smooth_transition("Preparando instalação...")
            clear_screen()
            try:
                run_full_install()
            except Exception as e:
                logger.error(f"Erro na Etapa 2: {e}")
                print(error(f"Erro crítico: {e}"))
            pause("Pressione ENTER para voltar ao menu...")

        elif opcao == '3':
            submenu_avulso_loop()

        elif opcao == '4':
            smooth_transition("Executando diagnóstico...")
            clear_screen()
            try:
                run_full_diagnostics()
            except Exception as e:
                logger.error(f"Erro no diagnóstico: {e}")
                print(error(f"Erro: {e}"))
            pause("Pressione ENTER para voltar ao menu...")

        elif opcao == '5':
            open_logs_folder()
            pause("Pressione ENTER para voltar ao menu...")

        elif opcao == '0' or not opcao:
            logger.info("Ferramenta encerrada pelo usuário.")
            _show_farewell()
            break

        else:
            print(warning("Opção inválida. Tente novamente."))
            time.sleep(1.5)


def _show_farewell():
    width = get_terminal_width()
    r = Colors.RESET

    print("")
    msg = "Até logo! 👋"
    pad = (width - len(msg)) // 2
    print(f"{' ' * pad}{Colors.SUCCESS}{msg}{r}")

    sub = "Provisionador encerrado com sucesso."
    pad2 = (width - len(sub)) // 2
    print(f"{' ' * pad2}{Colors.MUTED}{sub}{r}")
    print("")


def show_admin_error():
    """Erro de privilégios insuficientes."""
    width = get_terminal_width() - 4
    c = Colors.DANGER
    r = Colors.RESET

    print("")
    print(f"  {c}╔{'═' * (width - 2)}╗{r}")

    title = "⚠ ERRO — PRIVILÉGIOS INSUFICIENTES"
    pad = (width - len(title) - 4) // 2
    print(f"  {c}║{r}{' ' * pad}  {Colors.BOLD}{c}{title}{r}{' ' * (width - len(title) - pad - 4)}{c}║{r}")
    print(f"  {c}╠{'═' * (width - 2)}╣{r}")

    lines = [
        "",
        "Esta ferramenta PRECISA ser executada como",
        f"{Colors.BOLD}ADMINISTRADOR{r} para funcionar corretamente.",
        "",
        "Clique com botão direito no .exe e selecione:",
        f'{yellow("Executar como administrador")}',
        "",
    ]

    for line in lines:
        if not line:
            print(f"  {c}║{r}{' ' * (width - 2)}{c}║{r}")
        else:
            clean = _strip_ansi(line)
            padding = width - len(clean) - 4
            print(f"  {c}║{r}  {line}{' ' * max(padding, 1)}{c}║{r}")

    print(f"  {c}╚{'═' * (width - 2)}╝{r}")


def main():
    if not is_admin():
        show_admin_error()
        input(f"\n  {Colors.MUTED}Pressione ENTER para sair...{Colors.RESET}")
        sys.exit(1)

    try:
        main_menu()
    except Exception as e:
        print(error(f"Ocorreu um erro inesperado: {e}"))
        input(f"\n  {Colors.MUTED}Pressione ENTER para sair...{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
