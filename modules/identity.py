"""Etapa 1: Renomear PC e ingressar no domínio AD."""
import time
from config import CONFIG
from utils.powershell import run_powershell
from utils.logger import get_logger
from utils.console import console, print_header, print_step, print_info, print_error, print_warning, ask_input, confirm_action
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text


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


def run_identity_setup():
    """Renomeia o computador e ingressa no domínio."""
    logger = get_logger()

    print_header("ETAPA 1: CONFIGURAÇÃO DE IDENTIDADE")

    console.print("[dim]Esta etapa irá:[/]")
    console.print("    [primary]•[/] Renomear o computador")
    console.print("    [primary]•[/] Ingressar a máquina no domínio")
    console.print("    [warning]•[/] [warning]REQUER REINICIALIZAÇÃO após conclusão[/]")
    console.print()

    novo_nome = ask_input("Novo nome da máquina")
    if not novo_nome:
        print_error("O nome da máquina não pode ser vazio.")
        return False

    dominio_default = CONFIG.default_domain
    dominio = ask_input(f"Domínio [{dominio_default}]")
    if not dominio:
        dominio = dominio_default

    usuario_admin = ask_input("Usuário Admin do Domínio (ex: DOMINIO\\\\admin)")
    if not usuario_admin:
        print_error("O usuário administrador é obrigatório.")
        return False

    _draw_summary_box(novo_nome, dominio, usuario_admin)

    if not confirm_action("Confirma as configurações acima?"):
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
    if confirm_action("Deseja REINICIAR a máquina agora?"):
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
