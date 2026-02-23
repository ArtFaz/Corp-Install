"""Etapa 1: Renomear PC e ingressar no domínio AD."""
import re
import time
from config import CONFIG
from utils.powershell import run_powershell
from utils.logger import get_logger
from utils.console import console, print_header, print_step, print_info, print_error, print_warning, ask_input, confirm_action
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text


def _validate_hostname(name: str) -> bool:
    """Valida nome NetBIOS: 1-15 chars, alfanumérico + hífen, sem hífen nas extremidades."""
    return bool(re.match(r'^[A-Za-z0-9](?:[A-Za-z0-9\-]{0,13}[A-Za-z0-9])?$', name))


def _validate_domain(domain: str) -> bool:
    """Valida formato FQDN (ex: empresa.local)."""
    return bool(re.match(r'^[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?)+$', domain))


def _validate_admin_user(user: str) -> bool:
    """Valida formato usuario, DOMINIO\\usuario ou usuario@dominio."""
    return bool(re.match(r'^[A-Za-z0-9\.\-_]+\\[A-Za-z0-9\.\-_]+$', user) or
                re.match(r'^[A-Za-z0-9\.\-_]+@[A-Za-z0-9\.\-]+$', user) or
                re.match(r'^[A-Za-z0-9\.\-_]+$', user))


def _ask_validated(prompt: str, validator, error_msg: str, allow_empty: bool = False, default: str = None) -> str:
    """Pede input ao usuário com validação em loop."""
    while True:
        value = ask_input(prompt, default=default)
        if not value and allow_empty:
            return value or ""
        if not value:
            print_error("Este campo é obrigatório.")
            continue
        if validator(value):
            return value
        print_error(error_msg)


def _draw_summary_box(novo_nome: str, dominio: str, usuario_admin: str):
    """Caixa de resumo antes da confirmação."""
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(justify="right", style="dim white")
    grid.add_column(justify="left", style="bold")

    grid.add_row("Novo Nome:", f"[primary]{novo_nome}[/]")
    grid.add_row("Domínio:", f"[cyan]{dominio}[/]")
    grid.add_row("Usuário:", f"[warning]{usuario_admin}[/]")

    console.print(Panel(
        grid,
        title="[bold]RESUMO DA OPERAÇÃO[/]",
        border_style="dim white",
        padding=(1, 2)
    ))


def run_identity_setup(hostname: str = None, domain: str = None,
                       admin_user: str = None, auto_reboot: bool = False):
    """Renomeia o computador e ingressa no domínio.

    Se hostname/domain/admin_user forem fornecidos, opera em modo não-interativo.
    """
    logger = get_logger()
    unattended = all([hostname, admin_user])

    print_header("ETAPA 1: CONFIGURAÇÃO DE IDENTIDADE")

    if not unattended:
        console.print("[dim]Esta etapa irá:[/]")
        console.print("    [primary]•[/] Renomear o computador")
        console.print("    [primary]•[/] Ingressar a máquina no domínio")
        console.print("    [warning]•[/] [warning]REQUER REINICIALIZAÇÃO após conclusão[/]")
        console.print()

    # Hostname
    if hostname:
        novo_nome = hostname
        if not _validate_hostname(novo_nome):
            print_error(f"Hostname '{novo_nome}' inválido no perfil.")
            return False
    else:
        novo_nome = _ask_validated(
            "Novo nome da máquina",
            _validate_hostname,
            "Nome inválido. Use 1-15 caracteres (letras, números, hífen). Sem hífen no início/fim."
        )

    # Domínio
    dominio_default = CONFIG.default_domain
    if domain:
        dominio = domain
    elif unattended:
        dominio = dominio_default
    else:
        dominio_input = ask_input(f"Domínio [{dominio_default}]")
        dominio = dominio_input if dominio_input else dominio_default

    if not _validate_domain(dominio):
        print_error(f"Domínio '{dominio}' inválido. Formato esperado: empresa.local")
        return False

    # Usuário admin
    if admin_user:
        usuario_admin = admin_user
        if not _validate_admin_user(usuario_admin):
            print_error(f"Usuário '{usuario_admin}' inválido no perfil.")
            return False
    else:
        usuario_admin = _ask_validated(
            "Usuário Admin do Domínio (ex: admin)",
            _validate_admin_user,
            "Formato inválido. Use apenas o usuário, DOMINIO\\\\usuario ou usuario@dominio."
        )

    _draw_summary_box(novo_nome, dominio, usuario_admin)

    if not unattended and not confirm_action("Confirma as configurações acima?"):
        print_warning("Operação cancelada.")
        return False

    logger.info(f"Configurando identidade: {novo_nome} -> {dominio}")

    # Add-Computer com -NewName faz rename + join em operação única,
    # garantindo que o nome seja propagado corretamente no AD.
    ps_script = f'''
$cred = Get-Credential -Message "Credenciais de {usuario_admin}" -UserName "{usuario_admin}"
if ($null -eq $cred) {{
    Write-Error "Credenciais não fornecidas."
    exit 1
}}

try {{
    Add-Computer -DomainName "{dominio}" -NewName "{novo_nome}" -Credential $cred -Force -Restart:$false -ErrorAction Stop
    Write-Host "[OK] Computador renomeado para: {novo_nome}"
    Write-Host "[OK] Máquina adicionada ao domínio: {dominio}"
}} catch {{
    Write-Error "Falha ao configurar identidade: $_"
    exit 1
}}

Write-Host ""
Write-Host "=========================================="
Write-Host " CONFIGURAÇÃO CONCLUÍDA!"
Write-Host " A máquina precisa ser REINICIADA."
Write-Host "=========================================="
'''

    print_step("Executando comandos PowerShell...")
    print_info("Uma janela de credenciais será exibida")

    with console.status("[primary]Configurando identidade...[/]", spinner="dots"):
        return_code, stdout, stderr = run_powershell(ps_script, capture_output=False)

    if return_code != 0:
        logger.error(f"Falha na configuração. Código: {return_code}")
        if stderr:
            console.print(f"    [dim]Detalhes: {stderr}[/]")
        return False

    logger.success(f"Identidade configurada: {novo_nome}@{dominio}")

    console.print()
    should_reboot = auto_reboot if unattended else confirm_action("Deseja REINICIAR a máquina agora?")

    if should_reboot:
        logger.info("Reinicialização solicitada.")
        with Live(refresh_per_second=4, console=console) as live:
            for i in range(5, 0, -1):
                bar = "█" * i + "░" * (5 - i)
                live.update(Text(f"  ⏳ Reiniciando em {i}s  [{bar}]", style="bold warning"))
                time.sleep(1)
        console.print()
        run_powershell("shutdown /r /t 0 /c 'Reinicialização pós-ingresso no domínio'")
    else:
        print_warning("Reinicie a máquina manualmente para aplicar as alterações.")

    return True

