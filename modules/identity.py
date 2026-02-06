"""Etapa 1: Renomear e Ingressar no Domínio."""
from config import CONFIG
from utils.common import print_header, print_step, confirm_action
from utils.powershell import run_powershell
from utils.logger import get_logger


def run_identity_setup():
    """Renomeia o computador e ingressa no domínio."""
    logger = get_logger()
    
    print_header("ETAPA 1: CONFIGURAÇÃO DE IDENTIDADE")
    print("\nEsta etapa irá:")
    print("  • Renomear o computador")
    print("  • Ingressar a máquina no domínio")
    print("  • REQUER REINICIALIZAÇÃO após conclusão\n")
    
    # --- Coleta de dados ---
    novo_nome = input("Novo nome da máquina: ").strip()
    if not novo_nome:
        print("[ERRO] O nome da máquina não pode ser vazio.")
        return False
    
    dominio = input(f"Domínio [{CONFIG['default_domain']}]: ").strip()
    if not dominio:
        dominio = CONFIG['default_domain']
    
    usuario_admin = input("Usuário Admin do Domínio (ex: DOMINIO\\admin): ").strip()
    if not usuario_admin:
        print("[ERRO] O usuário administrador é obrigatório.")
        return False
    
    # --- Confirmação ---
    print("\n" + "-" * 50)
    print("RESUMO DA OPERAÇÃO:")
    print(f"  Novo Nome: {novo_nome}")
    print(f"  Domínio:   {dominio}")
    print(f"  Usuário:   {usuario_admin}")
    print("-" * 50)
    
    if not confirm_action("Confirma as configurações acima?"):
        print("Operação cancelada.")
        return False
    
    logger.info(f"Configurando identidade: {novo_nome} -> {dominio}")
    
    # --- Script PowerShell ---
    ps_script = f'''
$cred = Get-Credential -Message "Credenciais de {usuario_admin}" -UserName "{usuario_admin}"
if ($null -eq $cred) {{
    Write-Error "Credenciais não fornecidas."
    exit 1
}}

try {{
    Rename-Computer -NewName "{novo_nome}" -Force -ErrorAction Stop
    Write-Host "[OK] Computador renomeado para: {novo_nome}"
}} catch {{
    Write-Error "Falha ao renomear: $_"
    exit 1
}}

try {{
    Add-Computer -DomainName "{dominio}" -Credential $cred -Force -ErrorAction Stop
    Write-Host "[OK] Máquina adicionada ao domínio: {dominio}"
}} catch {{
    Write-Error "Falha ao ingressar no domínio: $_"
    exit 1
}}

Write-Host ""
Write-Host "=========================================="
Write-Host " CONFIGURAÇÃO CONCLUÍDA!"
Write-Host " A máquina precisa ser REINICIADA."
Write-Host "=========================================="
'''
    
    print_step("Executando comandos PowerShell...")
    print("(Uma janela de credenciais será exibida)")
    
    return_code, stdout, stderr = run_powershell(ps_script, capture_output=False)
    
    if return_code != 0:
        logger.error(f"Falha na configuração. Código: {return_code}")
        print(f"\n[ERRO] Código: {return_code}")
        if stderr:
            print(f"Detalhes: {stderr}")
        return False
    
    logger.success(f"Identidade configurada: {novo_nome}@{dominio}")
    
    # --- Reinicialização ---
    print("")
    if confirm_action("Deseja REINICIAR a máquina agora?"):
        logger.info("Reinicialização solicitada.")
        print("\nReiniciando em 5 segundos...")
        run_powershell("shutdown /r /t 5 /c 'Reinicialização pós-ingresso no domínio'")
    else:
        print("\n[AVISO] Reinicie a máquina manualmente para aplicar as alterações.")
    
    return True
