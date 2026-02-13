"""Logger com saída colorida no console."""
import os
import datetime
from pathlib import Path


class Logger:
    """Logging de ações do provisionamento com visual premium."""

    def __init__(self, log_dir: str = None):
        if log_dir is None:
            log_dir = r"C:\ProvisioningLogs"

        self.log_dir = Path(log_dir)
        self.log_file = None
        self._ensure_log_dir()
        self._create_log_file()

    def _ensure_log_dir(self):
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            self.log_dir = Path(os.environ.get('TEMP', '/tmp'))

    def _create_log_file(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        hostname = os.environ.get('COMPUTERNAME', 'unknown')
        self.log_file = self.log_dir / f"provisioning_{hostname}_{timestamp}.log"

    def _write(self, level: str, message: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}\n"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception:
            pass

    def info(self, message: str):
        from utils.console import print_info
        self._write("INFO", message)
        print_info(message)

    def success(self, message: str):
        from utils.console import print_success
        self._write("SUCCESS", message)
        print_success(message)

    def warning(self, message: str):
        from utils.console import print_warning
        self._write("WARNING", message)
        print_warning(message)

    def error(self, message: str):
        from utils.console import print_error
        self._write("ERROR", message)
        print_error(message)

    def get_log_path(self) -> str:
        return str(self.log_file)


_logger = None


def get_logger() -> Logger:
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger

