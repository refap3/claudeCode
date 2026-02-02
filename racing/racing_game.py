#!/usr/bin/env python3
"""
Terminal Racing Game - First-person arcade racer
Controls: Arrow keys to drive, Space to pause
"""

import curses
import math
import time
from dataclasses import dataclass
from typing import Tuple


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

    def draw(self, win):
        """Draw the track boundaries"""
        # Draw outer boundary
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            x = int(self.center_x + self.outer_radius_x * math.cos(rad))
            y = int(self.center_y + self.outer_radius_y * math.sin(rad))
            if 0 <= y < self.height - 1 and 0 <= x < self.width:
                try:
                    win.addch(y, x, '#', curses.color_pair(1))
                except curses.error:
                    pass

        # Draw inner boundary
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            x = int(self.center_x + self.inner_radius_x * math.cos(rad))
            y = int(self.center_y + self.inner_radius_y * math.sin(rad))
            if 0 <= y < self.height - 1 and 0 <= x < self.width:
                try:
                    win.addch(y, x, '#', curses.color_pair(1))
                except curses.error:
                    pass

        # Draw start/finish line
        for i in range(-2, 3):
            y = self.start_y + i
            if 0 <= y < self.height - 1:
                try:
                    win.addch(y, self.start_x, '|', curses.color_pair(3))
                except curses.error:
                    pass


class FirstPersonRenderer:
    """Renders the racing game from a first-person perspective"""

    def __init__(self):
        # Rendering parameters
        self.min_distance = 5.0
        self.max_distance = 100.0
        self.num_slices = 30  # Number of horizontal scan lines
        self.track_width_scale = 3.0  # Scale factor for track width visibility

        # Visual characters
        self.road_char = '='
        self.wall_char = '█'
        self.edge_char = '|'

    def calculate_future_position(self, car: Car, distance: float) -> Tuple[float, float]:
        """Calculate position ahead of car at given distance"""
        future_x = car.x + math.cos(car.angle) * distance
        future_y = car.y + math.sin(car.angle) * distance
        return future_x, future_y

    def find_track_boundaries(self, track: Track, center_x: float, center_y: float,
                            perpendicular_angle: float, max_search: float = 50.0) -> Tuple[float, float]:
        """Find left and right track boundaries at a given point

        For oval tracks, calculate actual track width based on geometry
        rather than ray-tracing from potentially off-center positions.
        """
        # Calculate track width at this position based on track geometry
        # The oval track has constant width: (outer_radius - inner_radius)
        dx = center_x - track.center_x
        dy = center_y - track.center_y

        # Calculate angle from track center to this position
        angle_to_pos = math.atan2(dy, dx)

        # Calculate distances from track center to inner and outer boundaries at this angle
        # Using ellipse formula: r(θ) for an ellipse
        outer_dist = math.sqrt(
            (track.outer_radius_x * math.cos(angle_to_pos)) ** 2 +
            (track.outer_radius_y * math.sin(angle_to_pos)) ** 2
        )
        inner_dist = math.sqrt(
            (track.inner_radius_x * math.cos(angle_to_pos)) ** 2 +
            (track.inner_radius_y * math.sin(angle_to_pos)) ** 2
        )

        # Track width at this angle
        track_width = outer_dist - inner_dist

        # Distance from center of position to each edge (symmetric)
        half_width = track_width / 2.0

        return half_width, half_width

    def calculate_lateral_offset(self, track: Track, car: Car, future_x: float, future_y: float) -> float:
        """Calculate how much the track curves left/right at future position"""
        # Find the angle to track center from future position
        to_center_x = track.center_x - future_x
        to_center_y = track.center_y - future_y

        # Calculate angle difference
        track_center_angle = math.atan2(to_center_y, to_center_x)
        angle_diff = track_center_angle - car.angle

        # Normalize to -pi to pi
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        # The lateral offset is the perpendicular component
        return math.sin(angle_diff) * 15.0

    def render_track_slice(self, win, screen_y: int, screen_width: int,
                          left_wall_x: int, right_wall_x: int,
                          is_on_track: bool, is_finish_line: bool = False):
        """Render a single horizontal slice of the track"""
        if screen_y < 0 or screen_y >= curses.LINES - 5:
            return

        try:
            # Choose colors
            wall_color = curses.color_pair(1)
            road_color = curses.color_pair(4) if is_on_track else curses.color_pair(5)
            finish_color = curses.color_pair(3)

            # Clamp boundaries to screen
            left_wall_x = max(0, min(screen_width - 1, left_wall_x))
            right_wall_x = max(0, min(screen_width - 1, right_wall_x))

            # Ensure left is actually left of right
            if left_wall_x > right_wall_x:
                left_wall_x, right_wall_x = right_wall_x, left_wall_x

            # Draw the slice
            for x in range(screen_width):
                if x < left_wall_x:
                    # Left off-road
                    win.addch(screen_y, x, ' ')
                elif x == left_wall_x:
                    # Left wall
                    win.addch(screen_y, x, self.edge_char, wall_color)
                elif x < right_wall_x:
                    # Track surface
                    if is_finish_line and screen_y % 2 == 0:
                        win.addch(screen_y, x, '|', finish_color)
                    else:
                        win.addch(screen_y, x, self.road_char, road_color)
                elif x == right_wall_x:
                    # Right wall
                    win.addch(screen_y, x, self.edge_char, wall_color)
                else:
                    # Right off-road
                    win.addch(screen_y, x, ' ')
        except curses.error:
            pass

    def render_view(self, win, car: Car, track: Track, screen_width: int, screen_height: int):
        """Render the first-person view of the track"""
        view_height = screen_height - 10  # Leave room for dashboard and HUD

        # Render each horizontal slice from top (far) to bottom (near)
        for row in range(view_height):
            # Calculate distance for this row (top = far, bottom = near)
            t = row / view_height  # 0 at top, 1 at bottom
            distance = self.min_distance + (self.max_distance - self.min_distance) * (1 - t)

            # Calculate future position at this distance
            future_x, future_y = self.calculate_future_position(car, distance)

            # Check if this position is on the track
            on_track_at_distance = track.is_on_track(future_x, future_y)

            # Calculate track boundaries at this distance
            left_dist, right_dist = self.find_track_boundaries(track, future_x, future_y, car.angle)

            # Apply perspective scaling (things get wider as they get closer)
            perspective_scale = self.min_distance / distance

            # Calculate lateral offset (track curving left/right)
            lateral_offset = self.calculate_lateral_offset(track, car, future_x, future_y)
            lateral_offset_pixels = int(lateral_offset * perspective_scale)

            # Calculate screen positions for track edges
            center_x = screen_width // 2 + lateral_offset_pixels
            left_wall_screen = int(center_x - left_dist * perspective_scale * self.track_width_scale)
            right_wall_screen = int(center_x + right_dist * perspective_scale * self.track_width_scale)

            # Check if this is near the finish line
            is_finish = abs(future_x - track.start_x) < 3 and abs(future_y - track.start_y) < 3

            # Render this slice
            self.render_track_slice(win, row, screen_width, left_wall_screen, right_wall_screen,
                                   on_track_at_distance, is_finish)

    def render_dashboard(self, win, screen_width: int, screen_height: int, car: Car):
        """Render car dashboard/cockpit at bottom of screen"""
        dashboard_y = screen_height - 8

        # Car hood/cockpit design - more visible
        hood_width = min(60, screen_width - 4)

        # Create the hood lines
        dashboard = []

        # Top of hood (narrow, far from driver)
        top_width = hood_width // 3
        top_line = " " * ((screen_width - top_width) // 2) + "█" * top_width
        dashboard.append(top_line)

        # Hood getting wider
        for i in range(1, 4):
            width = top_width + (hood_width - top_width) * i // 3
            line = " " * ((screen_width - width) // 2) + "▓" * width
            dashboard.append(line)

        # Dashboard/windshield frame
        frame_width = min(hood_width + 20, screen_width - 2)
        left_margin = (screen_width - frame_width) // 2

        # Instrument cluster
        speed_display = f"[SPD:{car.speed:.1f}]"
        dashboard.append(" " * left_margin + "╔" + "═" * (frame_width - 2) + "╗")
        dashboard.append(" " * left_margin + "║" + speed_display.center(frame_width - 2) + "║")

        try:
            for i, line in enumerate(dashboard):
                y = dashboard_y + i
                if y < screen_height - 3:
                    win.addstr(y, 0, line[:screen_width], curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass


class Game:
    """Main game controller"""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()

        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Track
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Car
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Finish line
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # HUD
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)    # Off-track

        # Game objects
        self.track = Track(self.width, self.height - 5)
        self.renderer = FirstPersonRenderer()

        # Start car on the right side of the track, between inner and outer boundaries
        track_width = (self.track.outer_radius_x - self.track.inner_radius_x) / 2
        start_x = self.track.center_x + self.track.inner_radius_x + track_width

        self.car = Car(
            x=start_x,
            y=self.track.center_y,
            angle=math.pi  # Start facing left (into the track)
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

        # Input
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)

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
            self.car.x = new_x
            self.car.y = new_y
            self.off_track = False
        else:
            # Hit wall - stop the car
            self.car.vx *= -0.5
            self.car.vy *= -0.5
            self.car.speed *= 0.3
            self.off_track = True

        # Calculate speed
        self.car.speed = math.sqrt(self.car.vx ** 2 + self.car.vy ** 2)

        # Update race time
        self.race_time = time.time() - self.start_time

        # Check for lap completion
        self.check_lap_completion()

    def handle_input(self):
        """Handle keyboard input"""
        try:
            key = self.stdscr.getch()

            if key == ord(' '):
                self.paused = not self.paused
                if not self.paused:
                    # Adjust start time to account for pause
                    self.start_time = time.time() - self.race_time
                return

            if self.paused:
                return

            if key == curses.KEY_UP:
                # Accelerate in current direction
                self.car.vx += math.cos(self.car.angle) * self.car.ACCELERATION
                self.car.vy += math.sin(self.car.angle) * self.car.ACCELERATION

                # Clamp to max speed
                speed = math.sqrt(self.car.vx ** 2 + self.car.vy ** 2)
                if speed > self.car.MAX_SPEED:
                    self.car.vx = (self.car.vx / speed) * self.car.MAX_SPEED
                    self.car.vy = (self.car.vy / speed) * self.car.MAX_SPEED

            elif key == curses.KEY_DOWN:
                # Brake/Reverse
                self.car.vx -= math.cos(self.car.angle) * self.car.BRAKE_FORCE
                self.car.vy -= math.sin(self.car.angle) * self.car.BRAKE_FORCE

            elif key == curses.KEY_LEFT:
                # Turn left (counterclockwise)
                self.car.angle -= self.car.TURN_SPEED

            elif key == curses.KEY_RIGHT:
                # Turn right (clockwise)
                self.car.angle += self.car.TURN_SPEED

            elif key == ord('q') or key == ord('Q'):
                self.running = False

        except curses.error:
            pass

    def draw(self):
        """Render everything in first-person view"""
        self.stdscr.clear()

        # Render first-person view of the track
        self.renderer.render_view(self.stdscr, self.car, self.track, self.width, self.height)

        # Render car dashboard at bottom
        self.renderer.render_dashboard(self.stdscr, self.width, self.height, self.car)

        # Draw HUD
        hud_y = self.height - 3
        try:
            # Main stats
            self.stdscr.addstr(hud_y, 2, f"Speed: {self.car.speed:.1f}", curses.color_pair(4))
            self.stdscr.addstr(hud_y, 20, f"Time: {self.race_time:.2f}s", curses.color_pair(4))
            self.stdscr.addstr(hud_y, 40, f"Laps: {self.laps_completed}", curses.color_pair(4))

            # Status indicator
            angle_deg = int(math.degrees(self.car.angle) % 360)
            on_track_status = "ON TRACK" if not self.off_track else "OFF TRACK!"
            debug_color = curses.color_pair(4) if not self.off_track else curses.color_pair(5)
            self.stdscr.addstr(hud_y, 60, on_track_status, debug_color | curses.A_BOLD)

            # Lap times
            hud_y2 = self.height - 2
            if self.last_lap_time:
                self.stdscr.addstr(hud_y2, 2, f"Last Lap: {self.last_lap_time:.2f}s", curses.color_pair(4))

            if self.best_lap_time:
                self.stdscr.addstr(hud_y2, 30, f"Best Lap: {self.best_lap_time:.2f}s", curses.color_pair(3))

            # Instructions
            instructions = "Arrows: Drive | Space: Pause | Q: Quit"
            self.stdscr.addstr(hud_y2, self.width - len(instructions) - 2, instructions, curses.color_pair(1))

            # Pause overlay
            if self.paused:
                pause_msg = "*** PAUSED ***"
                pause_y = self.height // 2
                self.stdscr.addstr(pause_y, self.width // 2 - len(pause_msg) // 2,
                                 pause_msg, curses.color_pair(3) | curses.A_BOLD)
        except curses.error:
            pass

        self.stdscr.refresh()

    def run(self):
        """Main game loop"""
        last_time = time.time()
        target_fps = 30
        frame_time = 1.0 / target_fps

        while self.running:
            current_time = time.time()
            dt = current_time - last_time

            # Handle input
            self.handle_input()

            # Update physics
            self.update_physics(dt)

            # Render
            self.draw()

            # Frame rate limiting
            elapsed = time.time() - current_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

            last_time = current_time


def main(stdscr):
    """Entry point for curses"""
    game = Game(stdscr)
    game.run()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nGame ended. Thanks for playing!")
