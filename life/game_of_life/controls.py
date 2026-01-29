"""Input handling for keyboard controls."""

import sys
import select
import termios
import tty


class InputHandler:
    """Cross-platform non-blocking keyboard input handler."""

    def __init__(self):
        """Initialize the input handler."""
        self.old_settings = None
        if sys.platform != 'win32':
            self.old_settings = termios.tcgetattr(sys.stdin)

    def __enter__(self):
        """Set up non-blocking input mode."""
        if sys.platform != 'win32':
            tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore terminal settings."""
        if sys.platform != 'win32' and self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_key(self):
        """
        Get a key press in a non-blocking way.

        Returns:
            The pressed key as a string, or None if no key was pressed
        """
        if sys.platform == 'win32':
            import msvcrt
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8', errors='ignore')
            return None
        else:
            # Unix/Mac
            if select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                # Handle escape sequences
                if key == '\x1b':
                    # Try to read more characters for escape sequences
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key += sys.stdin.read(2)
                return key
            return None
