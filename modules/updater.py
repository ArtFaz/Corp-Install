"""
Módulo responsável pelo mecanismo de auto-update da ferramenta.
Verifica novas versões em um diretório de rede e, se o usuário aceitar,
aplica a atualização via script intermediário após o encerramento.
"""
import os
import sys
import json
import time
import shutil
import subprocess
from typing import Optional, Dict

from packaging import version
from config import CONFIG, VERSION
from utils.logger import get_logger
from utils.console import console, confirm_action

def get_remote_version_info() -> Optional[Dict]:
    """
    Busca as informações de versão mais recentes no repositório da rede.
    Falha silenciosamente se a rede estiver indisponível.
    """
    update_dir = getattr(CONFIG, "update_network_dir", None)
    if not update_dir:
        return None

    try:
        if not os.path.exists(update_dir):
            return None

        version_file = os.path.join(update_dir, "version.json")
        if not os.path.exists(version_file):
            return None

        with open(version_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, PermissionError):
        return None

def check_for_updates() -> None:
    """
    Verifica se há uma versão mais nova disponível na rede.
    Se houver, pergunta ao usuário se deseja atualizar.
    """
    # Apenas executa em binário compilado (.exe)
    if not getattr(sys, 'frozen', False):
        return

    remote_info = get_remote_version_info()
    if not remote_info:
        return

    try:
        remote_ver_str = remote_info.get("latest_version")
        exe_filename = remote_info.get("exe_filename")

        if not remote_ver_str or not exe_filename:
            return

        current_v = version.parse(VERSION)
        remote_v = version.parse(remote_ver_str)

        if remote_v > current_v:
            _prompt_and_update(remote_ver_str, exe_filename)
    except Exception:
        pass


def _prompt_and_update(remote_ver_str: str, exe_filename: str) -> None:
    """
    Exibe a notificação de update e pergunta ao usuário se deseja atualizar.
    Se aceitar, baixa o novo executável e agenda a substituição via batch.
    """
    logger = get_logger()
    update_dir = CONFIG.update_network_dir
    remote_exe_path = os.path.join(update_dir, exe_filename)

    if not os.path.exists(remote_exe_path):
        return

    # Notifica e pergunta
    console.print()
    console.print(f"[bold accent]✨ Nova versão {remote_ver_str} disponível![/]")
    console.print(f"[dim]   Versão atual: v{VERSION}  →  Nova: v{remote_ver_str}[/]")
    console.print()

    if not confirm_action("Deseja atualizar agora?"):
        console.print("[dim]  Atualização ignorada.[/]")
        return

    # Cópia da rede para disco local (TEMP)
    temp_dir = os.environ.get("TEMP", r"C:\Temp")
    local_temp_exe = os.path.join(temp_dir, f"update_{int(time.time())}.exe")
    bat_path = os.path.join(temp_dir, f"updater_{int(time.time())}.bat")

    try:
        console.print("[dim]  Baixando atualização da rede...[/]")
        shutil.copy2(remote_exe_path, local_temp_exe)
    except Exception as e:
        logger.error(f"Falha na cópia do update: {e}")
        return

    current_exe_path = sys.executable

    # Batch simples: espera o processo fechar, substitui o exe, limpa
    bat_content = f'''@echo off
title Atualizando Provisionador...
echo.
echo Aguardando o programa fechar...
timeout /t 3 /nobreak > nul

copy /y "{local_temp_exe}" "{current_exe_path}" > nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 3 /nobreak > nul
    copy /y "{local_temp_exe}" "{current_exe_path}" > nul 2>&1
)

del /q "{local_temp_exe}" 2>nul
echo.
echo Atualizacao concluida! Reabra o Provisionador.
timeout /t 3 /nobreak > nul
del "%~f0"
'''
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
    except Exception as e:
        logger.error(f"Falha ao criar script de atualização: {e}")
        return

    # Dispara o batch em segundo plano
    subprocess.Popen(
        ["cmd.exe", "/c", bat_path],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    # Informa o usuário e encerra
    console.print()
    console.print(f"[bold accent]  ✅ Atualização v{remote_ver_str} preparada![/]")
    console.print(f"[bold]  O programa será fechado agora.[/]")
    console.print(f"[dim]  Reabra o Provisionador após a janela de atualização fechar.[/]")
    console.print()
    time.sleep(2)

    os._exit(0)
