"""Etapa 1: Renomear PC e ingressar no domínio AD."""
import time
from config import CONFIG
from utils.common import print_header, print_step
from utils.powershell import run_powershell
from utils.logger import get_logger
from utils.colors import (
    Colors, cyan, yellow, success, error, warning, info,
    styled_input, styled_confirm
)


def _draw_summary_box(novo_nome: str, dominio: str, usuario_admin: str):
    """Caixa de resumo antes da confirmação."""
    from utils.common import get_terminal_width
    width = get_terminal_width() - 4
    c = Colors.SURFACE
    r = Colors.RESET

    print("")
    print(f"  {c}╔{'═' * (width - 2)}╗{r}")
    title = "RESUMO DA OPERAÇÃO"
    pad = (width - len(title) - 4) // 2
    print(f"  {c}║{r}{' ' * pad}  {Colors.BOLD}{title}{r}{' ' * (width - len(title) - pad - 4)}{c}║{r}")
    print(f"  {c}╠{'═' * (width - 2)}╣{r}")

    items = [
        ("Novo Nome", f"{Colors.PRIMARY}{novo_nome}{r}"),
        ("Domínio", f"{Colors.CYAN}{dominio}{r}"),
        ("Usuário", f"{Colors.YELLOW}{usuario_admin}{r}"),
    ]

    for label, value in items:
        clean_line = f"  {label}: {novo_nome if 'Nome' in label else (dominio if 'Dom' in label else usuario_admin)}"
        display_line = f"  {Colors.MUTED}{label}:{r} {value}"
        padding = width - len(clean_line) - 4
        print(f"  {c}║{r}  {display_line}{' ' * max(padding, 1)}{c}║{r}")

    print(f"  {c}╚{'═' * (width - 2)}╝{r}")
    print("")


def run_identity_setup():
    """Renomeia o computador e ingressa no domínio."""
    logger = get_logger()

    print_header("ETAPA 1: CONFIGURAÇÃO DE IDENTIDADE")

    print(f"  {Colors.MUTED}Esta etapa irá:{Colors.RESET}")
    print(f"    {Colors.PRIMARY}•{Colors.RESET} Renomear o computador")
    print(f"    {Colors.PRIMARY}•{Colors.RESET} Ingressar a máquina no domínio")
    print(f"    {Colors.WARN}•{Colors.RESET} {yellow('REQUER REINICIALIZAÇÃO após conclusão')}")
    print("")

    novo_nome = styled_input("Novo nome da máquina")
    if not novo_nome:
        print(error("O nome da máquina não pode ser vazio."))
        return False

    dominio_default = CONFIG['default_domain']
    dominio = styled_input(f"Domínio [{cyan(dominio_default)}]")
    if not dominio:
        dominio = dominio_default

    usuario_admin = styled_input("Usuário Admin do Domínio (ex: DOMINIO\\\\admin)")
    if not usuario_admin:
        print(error("O usuário administrador é obrigatório."))
        return False

    _draw_summary_box(novo_nome, dominio, usuario_admin)

    if not styled_confirm("Confirma as configurações acima?"):
        print(warning("Operação cancelada."))
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
    print(info("Uma janela de credenciais será exibida"))

    return_code, stdout, stderr = run_powershell(ps_script, capture_output=False)

    if return_code != 0:
        logger.error(f"Falha na configuração. Código: {return_code}")
        print(error(f"Código de erro: {return_code}"))
        if stderr:
            print(f"    {Colors.MUTED}Detalhes: {stderr}{Colors.RESET}")
        return False

    logger.success(f"Identidade configurada: {novo_nome}@{dominio}")

    print("")
    if styled_confirm("Deseja REINICIAR a máquina agora?"):
        logger.info("Reinicialização solicitada.")
        for i in range(5, 0, -1):
            print(f"\r    {Colors.WARN}●{Colors.RESET} Reiniciando em {Colors.BOLD}{i}{Colors.RESET}s...", end="", flush=True)
            time.sleep(1)
        print("")
        run_powershell("shutdown /r /t 0 /c 'Reinicialização pós-ingresso no domínio'")
    else:
        print(warning("Reinicie a máquina manualmente para aplicar as alterações."))

    return True
