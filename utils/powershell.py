"""Wrapper para execução de comandos PowerShell."""
import subprocess
from typing import Tuple


def run_powershell(command: str, capture_output: bool = True) -> Tuple[int, str, str]:
    """Executa um comando PowerShell e retorna (return_code, stdout, stderr)."""
    full_command = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command", command
    ]
    
    try:
        if capture_output:
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(full_command)
            return result.returncode, "", ""
    except FileNotFoundError:
        return -1, "", "PowerShell não encontrado."
    except Exception as e:
        return -1, "", str(e)


def run_powershell_script(script_path: str) -> Tuple[int, str, str]:
    """Executa um arquivo de script PowerShell (.ps1)."""
    command = f"& '{script_path}'"
    return run_powershell(command)
