# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a terminal-based racing game written in Python using ANSI escape codes. It's a top-down arcade racer with physics-based car movement on an oval track.

## Running the Game

```bash
python racing_game.py
```

Requirements:
- Python 3.x only (no external dependencies)
- Works on Windows, macOS, and Linux

Game Controls:
- Arrow keys: Drive the car (up=accelerate, down=brake, left/right=turn)
- Space: Pause/unpause
- Q: Quit

## Code Architecture

### Main Components

The game is organized into five main classes in `racing_game.py`:

1. **Car** (dataclass, lines 26-39)
   - Represents the player's vehicle with position, velocity, and rotation
   - Physics constants: MAX_SPEED, ACCELERATION, BRAKE_FORCE, TURN_SPEED, FRICTION
   - Angle is in radians: 0 = right, π/2 = down, π = left, 3π/2 = up
   - Starts facing down (π/2) on the right side of the track at the finish line

2. **Track** (lines 42-76)
   - Manages the oval racing track with inner/outer elliptical boundaries
   - Track dimensions scale based on terminal size
   - Key method:
     - `is_on_track(x, y)`: Uses ellipse formula to check if position is within track boundaries
   - Lap tracking uses checkpoint system (must pass through left half before crossing finish line)

3. **InputHandler** (lines 79-137)
   - Cross-platform non-blocking keyboard input handler
   - Uses msvcrt on Windows, termios/tty on Unix/Mac
   - Handles arrow keys by mapping platform-specific codes to unified escape sequences
   - Context manager for clean resource management

4. **TopDownRenderer** (lines 140-277)
   - Renders the racing game from a bird's eye (top-down) perspective
   - Uses character buffer (2D array) for efficient rendering
   - Key methods:
     - `get_car_character(angle)`: Maps car angle to directional arrow (▲ ▼ ◄ ► ◢ ◣ ◤ ◥)
     - `render(car, track, game_state)`: Main rendering method
   - Visual elements:
     - Track boundaries: `#` characters for inner and outer ellipses
     - Car: Directional Unicode arrows based on heading
     - Finish line: `|` characters
     - HUD: Speed, time, laps, and lap times below track

5. **Game** (lines 280-462)
   - Main game controller orchestrating all components
   - Manages game state: race_time, laps_completed, best_lap_time, paused, off_track
   - Key methods:
     - `handle_input(input_handler)`: Processes keyboard input and applies forces to car
     - `update_physics(dt)`: Updates car position, applies friction, detects collisions
     - `check_lap_completion()`: Two-phase checkpoint system to detect valid lap completions
     - `draw()`: Uses TopDownRenderer to render view with HUD
     - `run()`: Main game loop running at 30 FPS with InputHandler context manager

### Physics System

The car uses velocity-based physics (lines 343-375):
- Velocity (vx, vy) is updated by acceleration/braking in the current angle direction
- Friction is applied each frame (multiplied by FRICTION constant: 0.94)
- Collision with track boundaries reverses velocity and reduces speed
- Speed is calculated as magnitude of velocity vector: sqrt(vx² + vy²)
- Physics runs at 30 FPS in the main game loop

### Collision Detection

Track boundaries use ellipse distance formula (lines 64-76):
- Inner boundary: distance must be >= 1.0
- Outer boundary: distance must be <= 1.0
- Formula: (dx²/rx²) + (dy²/ry²) where dx/dy are distances from center, rx/ry are radii

### Lap Completion Logic

Two-phase checkpoint system (lines 320-341):
1. Car must pass through left half of track (x < center_x) to set checkpoint flag
2. Then cross finish line on right side (x > outer_radius_x - 10, near start_y) to complete lap
3. Prevents false lap detection from driving backwards across finish line

## Rendering System (Top-Down View)

The game uses character buffer rendering to create a bird's eye view:

### Rendering Algorithm
1. Clear character buffer (2D array of spaces)
2. Draw track boundaries by sampling ellipse points at 2-degree intervals
3. Draw finish line as horizontal line spanning track width on right side
4. Draw car as directional arrow at current position
5. Output buffer to terminal using ANSI cursor positioning (no screen clearing)

### Car Direction Arrows

The car is rendered using Unicode arrows that match its heading (8 directions):
- `►` Right (0°)
- `◢` Down-right (45°)
- `▼` Down (90°)
- `◣` Down-left (135°)
- `◄` Left (180°)
- `◤` Up-left (225°)
- `▲` Up (270°)
- `◥` Up-right (315°)

### Visual Elements
- Track boundaries: `#` characters (both inner and outer ellipses)
- Car: Directional arrows (8 Unicode arrow characters)
- Finish line: `=` characters (horizontal line spanning track width on right side)
- Road surface: Empty space inside track
- HUD: Text display below track showing speed, time, laps

### Screen Layout
```
[100x50 character buffer showing entire track from above]
====================================
Speed: X.X | Time: XX.XXs | Laps: X
Last Lap: XX.XXs | Best: XX.XXs

Controls: Arrow Keys=Drive | Space=Pause | Q=Quit
```

## Platform Compatibility

### Windows UTF-8 Setup
- Lines 14-16 reconfigure stdout to UTF-8 encoding for Unicode arrow characters
- Essential for rendering directional arrows on Windows console

### Cross-Platform Input
- Windows: Uses msvcrt for non-blocking keyboard input
  - Arrow keys produce two-byte sequences (`\xe0` + key code)
  - Mapped to Unix-style escape sequences for unified handling
- Unix/Mac: Uses termios/tty with select for non-blocking input
  - Arrow keys already use escape sequences

### Terminal Requirements
- Minimum terminal size: 100x55 characters (recommended)
- UTF-8 support for directional arrow characters
- ANSI escape code support for cursor positioning

## Modifying Physics

To adjust game feel, modify these constants in the Car class (lines 35-39):
- MAX_SPEED: Maximum velocity magnitude (default: 3.0)
- ACCELERATION: Force applied per frame when accelerating (default: 0.3)
- BRAKE_FORCE: Force applied per frame when braking (default: 0.4)
- TURN_SPEED: Radians rotated per frame when turning (default: 0.15)
- FRICTION: Velocity multiplier per frame (default: 0.94, < 1.0 = friction, closer to 1.0 = more slippery)
