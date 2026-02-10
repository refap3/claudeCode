"""Input handling for keyboard controls."""

import sys

# Platform-specific imports
if sys.platform != 'win32':
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
                first_byte = msvcrt.getch()
                # Check for special keys (arrow keys, function keys, etc.)
                if first_byte in (b'\xe0', b'\x00'):
                    # Special key - read the next byte
                    if msvcrt.kbhit():
                        second_byte = msvcrt.getch()
                        # Map Windows arrow key codes to Unix-style escape sequences
                        arrow_map = {
                            b'H': '\x1b[A',  # Up arrow
                            b'P': '\x1b[B',  # Down arrow
                            b'M': '\x1b[C',  # Right arrow
                            b'K': '\x1b[D',  # Left arrow
                        }
                        if second_byte in arrow_map:
                            return arrow_map[second_byte]
                        return second_byte.decode('utf-8', errors='ignore')
                return first_byte.decode('utf-8', errors='ignore')
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
