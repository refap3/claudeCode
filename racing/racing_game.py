#!/usr/bin/env python3
"""
Terminal Racing Game - Top-down arcade racer
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
        """Render everything"""
        self.stdscr.clear()

        # Draw track
        self.track.draw(self.stdscr)

        # Draw car (simple representation)
        car_x = int(self.car.x)
        car_y = int(self.car.y)

        if 0 <= car_y < self.height - 1 and 0 <= car_x < self.width:
            # Draw car body (red if off-track, cyan if on-track)
            try:
                car_color = curses.color_pair(5) if self.off_track else curses.color_pair(2)
                self.stdscr.addch(car_y, car_x, 'O', car_color | curses.A_BOLD)

                # Draw direction indicator with better visibility
                front_x = int(car_x + math.cos(self.car.angle) * 2)
                front_y = int(car_y + math.sin(self.car.angle) * 2)
                if 0 <= front_y < self.height - 1 and 0 <= front_x < self.width:
                    # Choose direction arrow based on angle
                    angle_deg = (math.degrees(self.car.angle) % 360)
                    if 45 <= angle_deg < 135:
                        arrow = 'v'
                    elif 135 <= angle_deg < 225:
                        arrow = '<'
                    elif 225 <= angle_deg < 315:
                        arrow = '^'
                    else:
                        arrow = '>'
                    self.stdscr.addch(front_y, front_x, arrow, curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass

        # Draw HUD
        hud_y = self.height - 4
        try:
            self.stdscr.addstr(hud_y, 2, f"Time: {self.race_time:.2f}s", curses.color_pair(4))
            self.stdscr.addstr(hud_y + 1, 2, f"Laps: {self.laps_completed}", curses.color_pair(4))
            self.stdscr.addstr(hud_y, self.width - 30, f"Speed: {self.car.speed:.2f}", curses.color_pair(4))

            # Debug info with collision detection details
            angle_deg = int(math.degrees(self.car.angle) % 360)
            on_track_status = "ON TRACK" if not self.off_track else "OFF TRACK"
            debug_color = curses.color_pair(4) if not self.off_track else curses.color_pair(5)

            # Calculate distances for debugging
            dx = self.car.x - self.track.center_x
            dy = self.car.y - self.track.center_y
            outer_dist = (dx * dx) / (self.track.outer_radius_x * self.track.outer_radius_x) + \
                        (dy * dy) / (self.track.outer_radius_y * self.track.outer_radius_y)
            inner_dist = (dx * dx) / (self.track.inner_radius_x * self.track.inner_radius_x) + \
                        (dy * dy) / (self.track.inner_radius_y * self.track.inner_radius_y)

            self.stdscr.addstr(hud_y + 1, 2, f"{on_track_status} | Angle: {angle_deg}° | Pos:({int(self.car.x)},{int(self.car.y)})", debug_color)

            if self.last_lap_time:
                self.stdscr.addstr(hud_y + 2, self.width - 30, f"Last: {self.last_lap_time:.2f}s", curses.color_pair(4))

            if self.best_lap_time:
                self.stdscr.addstr(hud_y + 3, self.width - 30, f"Best: {self.best_lap_time:.2f}s", curses.color_pair(3))

            # Track dimensions and collision debug
            # Show first line for first 5 seconds
            if self.race_time < 5.0:
                self.stdscr.addstr(hud_y + 3, 2, f"Terminal: {self.width}x{self.height} | Track Inner={self.track.inner_radius_x}x{self.track.inner_radius_y} Outer={self.track.outer_radius_x}x{self.track.outer_radius_y}", curses.color_pair(1))

            # Always show collision distances
            if self.race_time < 10.0:
                dx = self.car.x - self.track.center_x
                dy = self.car.y - self.track.center_y
                outer_dist = (dx * dx) / (self.track.outer_radius_x * self.track.outer_radius_x) + \
                            (dy * dy) / (self.track.outer_radius_y * self.track.outer_radius_y)
                inner_dist = (dx * dx) / (self.track.inner_radius_x * self.track.inner_radius_x) + \
                            (dy * dy) / (self.track.inner_radius_y * self.track.inner_radius_y)
                collision_text = f"Collision: inner={inner_dist:.2f} (need >=1.0) outer={outer_dist:.2f} (need <=1.0)"
                collision_color = curses.color_pair(4) if (inner_dist >= 1.0 and outer_dist <= 1.0) else curses.color_pair(5)
                self.stdscr.addstr(self.height - 1, 2, collision_text, collision_color)

            # Instructions
            self.stdscr.addstr(hud_y + 2, 2, "Arrows: Drive | Space: Pause | Q: Quit", curses.color_pair(1))

            if self.paused:
                pause_msg = "*** PAUSED ***"
                self.stdscr.addstr(self.height // 2, self.width // 2 - len(pause_msg) // 2,
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
