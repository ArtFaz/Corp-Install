#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
  AUTOMATIZADOR DE PROVISIONAMENTO CORPORATIVO v1.0
  -------------------------------------------------
  Ferramenta CLI para automação pós-formatação de máquinas Windows.
  
  Uso: Execute como Administrador e siga as opções do menu.
===============================================================================
"""
import sys
import time

from utils.common import is_admin, clear_screen, pause, get_terminal_width
from utils.logger import get_logger
from modules.identity import run_identity_setup
from modules.install import run_full_install


VERSION = "1.0.0"


def draw_box(lines: list, title: str = None) -> str:
    """
    Desenha uma caixa com bordas Unicode adaptada à largura do terminal.
    
    Args:
        lines: Lista de linhas de conteúdo
        title: Título opcional para o topo da caixa
    
    Returns:
        String formatada com a caixa
    """
    width = get_terminal_width() - 4  # Margem lateral
    
    result = []
    
    # Linha superior
    if title:
        title_display = f" {title} "
        padding = width - len(title_display) - 2
        result.append(f"  ╔{title_display}{'═' * padding}╗")
    else:
        result.append(f"  ╔{'═' * (width - 2)}╗")
    
    # Conteúdo
    for line in lines:
        # Trunca linhas muito longas
        if len(line) > width - 4:
            line = line[:width - 7] + "..."
        padding = width - len(line) - 4
        result.append(f"  ║  {line}{' ' * padding}║")
    
    # Linha inferior
    result.append(f"  ╚{'═' * (width - 2)}╝")
    
    return "\n".join(result)


def show_banner():
    """Exibe o banner/título da ferramenta."""
    width = get_terminal_width()
    
    title = "AUTOMATIZADOR DE PROVISIONAMENTO CORPORATIVO"
    version = f"v{VERSION}"
    
    print("")
    print("  " + "═" * (width - 4))
    print("")
    print(f"{title:^{width}}")
    print(f"{version:^{width}}")
    print("")
    print("  " + "═" * (width - 4))
    print("")


def show_menu():
    """Exibe as opções do menu principal com largura adaptativa."""
    print("  Selecione a etapa do processo de provisionamento:\n")
    
    menu_lines = [
        "",
        "[1]  Configurar Nome e Domínio (ANTES do reboot)",
        "     → Renomeia máquina e ingressa no domínio",
        "     → Requer reinicialização após conclusão",
        "",
        "[2]  Instalar Softwares e Configs (APÓS login no AD)",
        "     → Chrome, WinRAR, Teams, AnyDesk (Winget)",
        "     → Office (escolha 2013 ou 365)",
        "     → Atalho WebApp, Pastas de Sistema",
        "",
        "[0]  Sair",
        "",
    ]
    
    print(draw_box(menu_lines, "MENU PRINCIPAL"))
    print("")


def main_menu():
    """Loop principal do menu interativo."""
    logger = get_logger()
    logger.info(f"Ferramenta iniciada - Versão {VERSION}")
    
    while True:
        clear_screen()
        show_banner()
        show_menu()
        
        try:
            opcao = input("  Digite a opção desejada: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Saindo...")
            break
        
        if opcao == '1':
            clear_screen()
            try:
                run_identity_setup()
            except Exception as e:
                logger.error(f"Erro na Etapa 1: {e}")
                print(f"\n[ERRO CRÍTICO] {e}")
            pause("Pressione ENTER para voltar ao menu...")
            
        elif opcao == '2':
            clear_screen()
            try:
                run_full_install()
            except Exception as e:
                logger.error(f"Erro na Etapa 2: {e}")
                print(f"\n[ERRO CRÍTICO] {e}")
            pause("Pressione ENTER para voltar ao menu...")
            
        elif opcao == '0':
            logger.info("Ferramenta encerrada pelo usuário.")
            print("\n  Encerrando. Até logo!\n")
            break
            
        else:
            print("\n  [!] Opção inválida. Tente novamente.")
            time.sleep(1.5)


def show_admin_error():
    """Exibe erro de privilégios de forma responsiva."""
    error_lines = [
        "",
        "Esta ferramenta PRECISA ser executada como",
        "ADMINISTRADOR para funcionar corretamente.",
        "",
        "Clique com botão direito no .exe e selecione:",
        '"Executar como administrador"',
        "",
    ]
    print("")
    print(draw_box(error_lines, "⚠ ERRO FATAL"))


def main():
    """Entry point principal."""
    # Verifica privilégios de administrador
    if not is_admin():
        show_admin_error()
        input("\nPressione ENTER para sair...")
        sys.exit(1)
    
    # Inicia o menu principal
    try:
        main_menu()
    except Exception as e:
        print(f"\n[ERRO FATAL] Ocorreu um erro inesperado: {e}")
        input("Pressione ENTER para sair...")
        sys.exit(1)


if __name__ == "__main__":
    main()
