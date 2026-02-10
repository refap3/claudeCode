#!/usr/bin/env python3
"""
Terminal Racing Game - Top-down arcade racer
Controls: Arrow keys to drive, Space to pause, Q to quit
"""

import sys
import math
import time
from dataclasses import dataclass
from typing import Optional

# Configure Windows console for UTF-8 output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Platform-specific imports
if sys.platform != 'win32':
    import select
    import termios
    import tty


@dataclass
class Car:
    """Player car with position, velocity, and rotation"""
    x: float
    y: float
    vx: float = 0.0  # velocity x
    vy: float = 0.0  # velocity y
    angle: float = 0.0  # radians, 0 = right, pi/2 = down
    speed: float = 0.0

    MAX_SPEED = 3.0
    ACCELERATION = 0.3
    BRAKE_FORCE = 0.4
    TURN_SPEED = 0.15
    FRICTION = 0.94


class Track:
    """Oval racing track with boundaries"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # Oval parameters - scale based on terminal size
        self.outer_radius_x = max(30, width // 2 - 5)
        self.outer_radius_y = max(15, height // 2 - 3)
        self.inner_radius_x = max(15, width // 2 - 15)
        self.inner_radius_y = max(8, height // 2 - 10)

        # Starting line position
        self.start_x = self.center_x + self.outer_radius_x - 5
        self.start_y = self.center_y

        # Lap tracking
        self.checkpoint_passed = False

    def is_on_track(self, x: float, y: float) -> bool:
        """Check if position is within track boundaries"""
        # Normalize to center
        dx = x - self.center_x
        dy = y - self.center_y

        # Calculate distance from center using ellipse formula
        outer_dist = (dx * dx) / (self.outer_radius_x * self.outer_radius_x) + \
                     (dy * dy) / (self.outer_radius_y * self.outer_radius_y)
        inner_dist = (dx * dx) / (self.inner_radius_x * self.inner_radius_x) + \
                     (dy * dy) / (self.inner_radius_y * self.inner_radius_y)

        return inner_dist >= 1.0 and outer_dist <= 1.0


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
                    # Special key - wait for second byte with retry logic
                    second_byte = None
                    for _ in range(10):  # Try up to 10 times (10ms total)
                        if msvcrt.kbhit():
                            second_byte = msvcrt.getch()
                            break
                        time.sleep(0.001)  # Wait 1ms between tries

                    if second_byte is not None:
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
                    # If second byte never arrived, ignore the key
                    return None
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


class TopDownRenderer:
    """Renders the racing game from a top-down (bird's eye) perspective"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Character buffer for efficient rendering
        self.buffer = [[' ' for _ in range(width)] for _ in range(height)]

    def clear_screen(self):
        """Clear the terminal screen using ANSI escape codes."""
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()

    def move_cursor_home(self):
        """Move cursor to home position without clearing screen."""
        sys.stdout.write('\033[H')
        sys.stdout.flush()

    def get_car_character(self, angle: float) -> str:
        """Get directional arrow character based on car angle"""
        # Normalize angle to 0-2π
        angle = angle % (2 * math.pi)

        # Convert to degrees for easier comparison
        degrees = math.degrees(angle)

        # Map angle to 8 directional arrows
        if degrees < 22.5 or degrees >= 337.5:
            return '►'  # Right
        elif degrees < 67.5:
            return '◢'  # Down-right
        elif degrees < 112.5:
            return '▼'  # Down
        elif degrees < 157.5:
            return '◣'  # Down-left
        elif degrees < 202.5:
            return '◄'  # Left
        elif degrees < 247.5:
            return '◤'  # Up-left
        elif degrees < 292.5:
            return '▲'  # Up
        else:
            return '◥'  # Up-right

    def render(self, car: Car, track: Track, game_state: dict):
        """
        Render the top-down view of the track and car.

        Args:
            car: Car instance with position and angle
            track: Track instance with boundaries
            game_state: Dictionary with race_time, laps_completed, etc.
        """
        # Clear buffer
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = ' '

        # Draw track boundaries
        # Draw outer boundary
        for angle_deg in range(0, 360, 2):
            rad = math.radians(angle_deg)
            x = int(track.center_x + track.outer_radius_x * math.cos(rad))
            y = int(track.center_y + track.outer_radius_y * math.sin(rad))
            if 0 <= y < self.height and 0 <= x < self.width:
                self.buffer[y][x] = '#'

        # Draw inner boundary
        for angle_deg in range(0, 360, 2):
            rad = math.radians(angle_deg)
            x = int(track.center_x + track.inner_radius_x * math.cos(rad))
            y = int(track.center_y + track.inner_radius_y * math.sin(rad))
            if 0 <= y < self.height and 0 <= x < self.width:
                self.buffer[y][x] = '#'

        # Draw start/finish line (horizontal, on right side of track)
        finish_y = track.start_y
        # Calculate x range from inner to outer radius on right side
        finish_x_start = int(track.center_x + track.inner_radius_x)
        finish_x_end = int(track.center_x + track.outer_radius_x)
        if 0 <= finish_y < self.height:
            for x in range(finish_x_start, finish_x_end + 1):
                if 0 <= x < self.width:
                    self.buffer[finish_y][x] = '='

        # Draw car
        car_x = int(car.x)
        car_y = int(car.y)
        if 0 <= car_y < self.height and 0 <= car_x < self.width:
            car_char = self.get_car_character(car.angle)
            self.buffer[car_y][car_x] = car_char

        # Move cursor to home
        self.move_cursor_home()

        # Build output
        lines = []

        # Render buffer
        for row in self.buffer:
            lines.append(''.join(row))

        # Add separator
        lines.append('=' * self.width)

        # Add HUD
        speed = game_state.get('speed', 0.0)
        race_time = game_state.get('race_time', 0.0)
        laps = game_state.get('laps_completed', 0)
        last_lap = game_state.get('last_lap_time')
        best_lap = game_state.get('best_lap_time')
        off_track = game_state.get('off_track', False)
        paused = game_state.get('paused', False)

        # Main stats line
        status_line = f"Speed: {speed:.1f} | Time: {race_time:.2f}s | Laps: {laps}"
        if off_track:
            status_line += " | OFF TRACK!"
        if paused:
            status_line += " | PAUSED"
        lines.append(status_line)

        # Lap times line
        lap_times = []
        if last_lap is not None:
            lap_times.append(f"Last Lap: {last_lap:.2f}s")
        if best_lap is not None:
            lap_times.append(f"Best: {best_lap:.2f}s")
        if lap_times:
            lines.append(' | '.join(lap_times))
        else:
            lines.append('')

        # Controls
        lines.append('')
        lines.append('Controls: Arrow Keys=Drive | Space=Pause | Q=Quit')

        # Print entire frame at once
        sys.stdout.write('\n'.join(lines))
        sys.stdout.flush()


class Game:
    """Main game controller"""

    def __init__(self, width: int = 100, height: int = 50):
        self.width = width
        self.height = height

        # Game objects
        self.track = Track(width, height)
        self.renderer = TopDownRenderer(width, height)

        # Start car on the right side of the track, between inner and outer boundaries
        track_width = (self.track.outer_radius_x - self.track.inner_radius_x) / 2
        start_x = self.track.center_x + self.track.inner_radius_x + track_width

        self.car = Car(
            x=start_x,
            y=self.track.center_y,
            angle=math.pi / 2  # Start facing down (following the track)
        )

        # Game state
        self.running = True
        self.paused = False
        self.race_time = 0.0
        self.start_time = time.time()
        self.laps_completed = 0
        self.current_lap_start = 0.0
        self.best_lap_time = None
        self.last_lap_time = None
        self.off_track = False

        # Verify car starts on track
        self.off_track = not self.track.is_on_track(self.car.x, self.car.y)
        if self.off_track:
            # Force car to proper position if initial check fails
            self.car.x = self.track.center_x + (self.track.outer_radius_x + self.track.inner_radius_x) / 2
            self.car.y = self.track.center_y
            self.off_track = not self.track.is_on_track(self.car.x, self.car.y)

    def check_lap_completion(self):
        """Check if car crossed finish line"""
        # Simple checkpoint system
        car_x = self.car.x - self.track.center_x

        # Check if passed through left half (checkpoint)
        if car_x < 0 and not self.track.checkpoint_passed:
            self.track.checkpoint_passed = True

        # Check if crossed finish line from left side
        if car_x > self.track.outer_radius_x - 10 and self.track.checkpoint_passed:
            if abs(self.car.y - self.track.start_y) < 5:
                # Lap completed!
                self.laps_completed += 1
                lap_time = self.race_time - self.current_lap_start
                self.last_lap_time = lap_time

                if self.best_lap_time is None or lap_time < self.best_lap_time:
                    self.best_lap_time = lap_time

                self.current_lap_start = self.race_time
                self.track.checkpoint_passed = False

    def update_physics(self, dt: float):
        """Update car physics"""
        if self.paused:
            return

        # Apply friction
        self.car.vx *= self.car.FRICTION
        self.car.vy *= self.car.FRICTION

        # Update position
        new_x = self.car.x + self.car.vx
        new_y = self.car.y + self.car.vy

        # Check collision with track boundaries
        if self.track.is_on_track(new_x, new_y):
            # Can move to new position - update and clear off-track
            self.car.x = new_x
            self.car.y = new_y
            self.off_track = False
        else:
            # Hit wall - reduce speed significantly and bounce back
            self.car.vx *= -0.3
            self.car.vy *= -0.3
            self.off_track = True

        # Calculate speed
        self.car.speed = math.sqrt(self.car.vx ** 2 + self.car.vy ** 2)

        # Update race time
        self.race_time = time.time() - self.start_time

        # Check for lap completion
        self.check_lap_completion()

    def handle_input(self, input_handler: InputHandler):
        """Handle keyboard input"""
        key = input_handler.get_key()

        if key is None:
            return

        if key == ' ':
            self.paused = not self.paused
            if not self.paused:
                # Adjust start time to account for pause
                self.start_time = time.time() - self.race_time
            return

        if self.paused:
            return

        if key == '\x1b[A':  # Up arrow
            # Accelerate in current direction
            self.car.vx += math.cos(self.car.angle) * self.car.ACCELERATION
            self.car.vy += math.sin(self.car.angle) * self.car.ACCELERATION

            # Clamp to max speed
            speed = math.sqrt(self.car.vx ** 2 + self.car.vy ** 2)
            if speed > self.car.MAX_SPEED:
                self.car.vx = (self.car.vx / speed) * self.car.MAX_SPEED
                self.car.vy = (self.car.vy / speed) * self.car.MAX_SPEED

        elif key == '\x1b[B':  # Down arrow
            # Brake/Reverse
            self.car.vx -= math.cos(self.car.angle) * self.car.BRAKE_FORCE
            self.car.vy -= math.sin(self.car.angle) * self.car.BRAKE_FORCE

        elif key == '\x1b[D':  # Left arrow
            # Turn left (counterclockwise)
            self.car.angle -= self.car.TURN_SPEED

        elif key == '\x1b[C':  # Right arrow
            # Turn right (clockwise)
            self.car.angle += self.car.TURN_SPEED

        elif key in ('q', 'Q', '\x1b'):  # Q or ESC
            self.running = False

    def draw(self):
        """Render everything in top-down view"""
        game_state = {
            'speed': self.car.speed,
            'race_time': self.race_time,
            'laps_completed': self.laps_completed,
            'last_lap_time': self.last_lap_time,
            'best_lap_time': self.best_lap_time,
            'off_track': self.off_track,
            'paused': self.paused,
        }
        self.renderer.render(self.car, self.track, game_state)

    def run(self):
        """Main game loop"""
        # Clear screen once at start
        self.renderer.clear_screen()

        with InputHandler() as input_handler:
            last_time = time.time()
            target_fps = 30
            frame_time = 1.0 / target_fps

            while self.running:
                current_time = time.time()
                dt = current_time - last_time

                # Handle input
                self.handle_input(input_handler)

                # Update physics
                self.update_physics(dt)

                # Render
                self.draw()

                # Frame rate limiting
                elapsed = time.time() - current_time
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)

                last_time = current_time


def main():
    """Entry point"""
    try:
        game = Game(width=100, height=50)
        game.run()
    except KeyboardInterrupt:
        print("\n\nGame ended. Thanks for playing!")


if __name__ == "__main__":
    main()
