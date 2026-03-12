import threading
import time
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

console = Console()

class LoadingAnimation:
    """A loading animation with customizable text and spinner."""
    
    def __init__(self, text: str = "Thinking", spinner_style: str = "dots"):
        self.text = text
        self.spinner = Spinner(spinner_style, text=text)
        self.live = None
        self._running = False
        self._thread = None
    
    def start(self):
        """Start the loading animation in a separate thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the loading animation."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.1)
        if self.live:
            self.live.stop()
    
    def _animate(self):
        """Internal method to run the animation."""
        try:
            with Live(self.spinner, console=console, refresh_per_second=10) as live:
                self.live = live
                while self._running:
                    time.sleep(0.1)
        except Exception:
            # Handle any exceptions gracefully
            pass

def show_loading_animation(text: str = "Thinking", duration: float = None):
    """
    Show a loading animation with the specified text.
    
    Args:
        text: The text to display with the spinner
        duration: Optional duration in seconds. If None, animation runs until manually stopped.
    
    Returns:
        LoadingAnimation instance that can be stopped manually
    """
    animation = LoadingAnimation(text)
    animation.start()
    
    if duration:
        time.sleep(duration)
        animation.stop()
    
    return animation

def with_loading_animation(text: str = "Thinking"):
    """
    Decorator to add loading animation to any function.
    
    Args:
        text: The text to display during loading
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            animation = LoadingAnimation(text)
            animation.start()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                animation.stop()
        return wrapper
    return decorator
