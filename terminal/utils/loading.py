from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

console = Console()


class LoadingAnimation:
    def __init__(self, text: str = "Thinking"):
        self.live = Live(Spinner("dots", text=text), console=console, refresh_per_second=10)

    def start(self):
        self.live.start()

    def stop(self):
        self.live.stop()
