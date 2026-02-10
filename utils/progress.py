"""Feedback visual dinâmico: spinner, barra de progresso, transições."""
import sys
import time
import threading
import itertools
from utils.colors import Colors


class Spinner:
    """Spinner animado em thread separada. Uso como context manager."""

    def __init__(self, message: str = "", style: str = "dots"):
        self.message = message
        self._running = False
        self._thread = None

        styles = {
            "dots":   ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "line":   ["|", "/", "-", "\\"],
            "pulse":  ["●", "◉", "○", "◉"],
            "arrow":  ["▹▹▹", "▸▹▹", "▹▸▹", "▹▹▸"],
            "blocks": ["░", "▒", "▓", "█", "▓", "▒"],
        }
        self._frames = styles.get(style, styles["dots"])

    def _spin(self):
        cycle = itertools.cycle(self._frames)
        while self._running:
            frame = next(cycle)
            sys.stdout.write(f"\r    {Colors.PRIMARY}{frame}{Colors.RESET} {self.message}")
            sys.stdout.flush()
            time.sleep(0.08)
        sys.stdout.write(f"\r{' ' * (len(self.message) + 10)}\r")
        sys.stdout.flush()

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


class ProgressBar:
    """Barra de progresso inline com porcentagem e tempo decorrido."""

    def __init__(self, total: int, label: str = "", bar_width: int = 25):
        self.total = total
        self.label = label
        self.bar_width = bar_width
        self.current = 0
        self._start_time = time.time()

    def update(self, current: int, detail: str = ""):
        self.current = current
        pct = current / self.total if self.total > 0 else 0
        filled = int(pct * self.bar_width)
        empty = self.bar_width - filled

        if pct >= 1.0:
            bar_color = Colors.SUCCESS
        elif pct >= 0.5:
            bar_color = Colors.PRIMARY
        else:
            bar_color = Colors.CYAN

        bar = f"{bar_color}{'█' * filled}{Colors.SURFACE}{'░' * empty}{Colors.RESET}"
        pct_text = f"{int(pct * 100):3d}%"
        counter = f"{Colors.MUTED}[{current}/{self.total}]{Colors.RESET}"
        elapsed = time.time() - self._start_time
        time_text = f"{Colors.MUTED}{elapsed:.0f}s{Colors.RESET}"
        detail_text = f" {Colors.MUTED}{detail}{Colors.RESET}" if detail else ""

        sys.stdout.write(f"\r    {bar} {pct_text} {counter} {time_text}{detail_text}   ")
        sys.stdout.flush()

    def finish(self, message: str = ""):
        elapsed = time.time() - self._start_time
        sys.stdout.write(f"\r{' ' * 120}\r")
        sys.stdout.flush()

        label = message or "Concluído"
        print(f"    {Colors.SUCCESS}✓{Colors.RESET} {label} {Colors.MUTED}[{elapsed:.0f}s]{Colors.RESET}")


def smooth_transition(message: str = "Carregando...", duration: float = 0.4):
    """Animação braille de transição entre telas."""
    frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    end_time = time.time() + duration
    cycle = itertools.cycle(frames)

    while time.time() < end_time:
        frame = next(cycle)
        sys.stdout.write(f"\r    {Colors.PRIMARY}{frame}{Colors.RESET} {Colors.MUTED}{message}{Colors.RESET}")
        sys.stdout.flush()
        time.sleep(0.05)

    sys.stdout.write(f"\r{' ' * (len(message) + 10)}\r")
    sys.stdout.flush()


def show_celebration():
    """ASCII art celebratório ao final da instalação."""
    r = Colors.RESET
    g = Colors.SUCCESS

    lines = [
        "",
        f"    {g}★  ★  ★  ★  ★  ★  ★  ★  ★{r}",
        "",
        f"    {Colors.GRAD_1}  ██████╗ ██╗  ██╗{r}",
        f"    {Colors.GRAD_2}  ██╔═══██╗██║ ██╔╝{r}",
        f"    {Colors.GRAD_3}  ██║   ██║█████╔╝ {r}",
        f"    {Colors.GRAD_4}  ██║   ██║██╔═██╗ {r}",
        f"    {Colors.GRAD_5}  ╚██████╔╝██║  ██╗{r}",
        f"    {Colors.PRIMARY}   ╚═════╝ ╚═╝  ╚═╝{r}",
        "",
        f"    {Colors.SUCCESS}Todas as etapas concluídas com sucesso!{r}",
        f"    {Colors.MUTED}A máquina está pronta para uso.{r}",
        "",
        f"    {g}★  ★  ★  ★  ★  ★  ★  ★  ★{r}",
        "",
    ]

    for line in lines:
        print(line)
        time.sleep(0.05)


def show_summary_card(title: str, items: list, elapsed: float = None):
    """
    Card de sumário final.

    items: lista de tuplas (label, status, detail)
           status: ok | warn | error | skip
    """
    from utils.common import get_terminal_width

    width = get_terminal_width() - 4
    c = Colors.SURFACE
    r = Colors.RESET
    sc = Colors.SUCCESS

    status_icons = {
        "ok":    f"{Colors.SUCCESS}✓{r}",
        "warn":  f"{Colors.WARN}⚠{r}",
        "error": f"{Colors.DANGER}✗{r}",
        "skip":  f"{Colors.MUTED}○{r}",
    }

    print("")
    print(f"  {sc}╔{'═' * (width - 2)}╗{r}")

    pad = (width - len(title) - 4) // 2
    print(f"  {sc}║{r}{' ' * pad}  {Colors.BOLD}{sc}{title}{r}{' ' * (width - len(title) - pad - 4)}{sc}║{r}")
    print(f"  {sc}╠{'═' * (width - 2)}╣{r}")

    for label, status, detail in items:
        icon = status_icons.get(status, status_icons["ok"])
        detail_text = f" {Colors.MUTED}— {detail}{r}" if detail else ""
        clean_len = len(f"  {label}  {detail if detail else ''}")
        dots_count = max(2, width - clean_len - 12)
        dots = f"{Colors.SURFACE}{'·' * dots_count}{r}"
        print(f"  {sc}║{r}  {icon} {label} {dots}{detail_text}  {sc}║{r}")

    if elapsed is not None:
        print(f"  {sc}╠{'═' * (width - 2)}╣{r}")
        time_str = f"Tempo total: {elapsed:.0f}s"
        time_pad = width - len(time_str) - 4
        print(f"  {sc}║{r}  {Colors.MUTED}⏱ {time_str}{r}{' ' * max(time_pad - 2, 1)}{sc}║{r}")

    print(f"  {sc}╚{'═' * (width - 2)}╝{r}")
    print("")
