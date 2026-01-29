# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a terminal-based racing game written in Python using the curses library. It's a top-down arcade racer with physics-based car movement on an oval track.

## Running the Game

```bash
python3 racing_game.py
```

Requirements:
- Python 3.x
- curses library (standard library on Unix/macOS, requires windows-curses on Windows)

Game Controls:
- Arrow keys: Drive the car (up=accelerate, down=brake, left/right=turn)
- Space: Pause/unpause
- Q: Quit

## Code Architecture

### Main Components

The game is organized into three main classes in `racing_game.py`:

1. **Car** (dataclass, lines 14-29)
   - Represents the player's vehicle with position, velocity, and rotation
   - Physics constants: MAX_SPEED, ACCELERATION, BRAKE_FORCE, TURN_SPEED, FRICTION
   - Angle is in radians: 0 = right, π/2 = down, π = left, 3π/2 = up

2. **Track** (lines 31-99)
   - Manages the oval racing track with inner/outer elliptical boundaries
   - Track dimensions scale based on terminal size
   - Key methods:
     - `is_on_track(x, y)`: Uses ellipse formula to check if position is within track boundaries
     - `draw(win)`: Renders track boundaries and finish line
   - Lap tracking uses checkpoint system (must pass through left half before crossing finish line)

3. **Game** (lines 101-371)
   - Main game controller orchestrating all components
   - Manages game state: race_time, laps_completed, best_lap_time, paused, off_track
   - Key methods:
     - `handle_input()`: Processes keyboard input and applies forces to car
     - `update_physics(dt)`: Updates car position, applies friction, detects collisions
     - `check_lap_completion()`: Two-phase checkpoint system to detect valid lap completions
     - `draw()`: Renders track, car, and HUD with debug information
     - `run()`: Main game loop running at 30 FPS

### Physics System

The car uses velocity-based physics (lines 176-208):
- Velocity (vx, vy) is updated by acceleration/braking in the current angle direction
- Friction is applied each frame (multiplied by FRICTION constant)
- Collision with track boundaries reverses velocity and reduces speed
- Speed is calculated as magnitude of velocity vector

### Collision Detection

Track boundaries use ellipse distance formula (lines 53-65):
- Inner boundary: distance must be >= 1.0
- Outer boundary: distance must be <= 1.0
- Formula: (dx²/rx²) + (dy²/ry²) where dx/dy are distances from center, rx/ry are radii

### Lap Completion Logic

Two-phase checkpoint system (lines 153-174):
1. Car must pass through left half of track (x < center_x) to set checkpoint flag
2. Then cross finish line on right side (x > outer_radius_x - 10, near start_y) to complete lap
3. Prevents false lap detection from driving backwards across finish line

## Terminal/Curses Specifics

- Game requires minimum terminal size for proper track rendering
- Uses curses color pairs (1=track, 2=car, 3=finish line, 4=HUD, 5=off-track warning)
- HUD displays debug info for first 10 seconds of gameplay
- Car rendered as 'O' with directional arrow (>, v, <, ^) based on angle
- Non-blocking input via `stdscr.nodelay(True)`

## Modifying Physics

To adjust game feel, modify these constants in the Car class (lines 24-28):
- MAX_SPEED: Maximum velocity magnitude
- ACCELERATION: Force applied per frame when accelerating
- BRAKE_FORCE: Force applied per frame when braking
- TURN_SPEED: Radians rotated per frame when turning
- FRICTION: Velocity multiplier per frame (< 1.0 = friction, closer to 1.0 = more slippery)
