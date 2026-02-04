# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a terminal-based implementation of Conway's Game of Life in Python. It features fast NumPy-based grid computation, ANSI terminal rendering, and interactive keyboard controls.

## Running the Application

Run the game with default settings:
```bash
python main.py
```

Run with specific pattern and grid size:
```bash
python main.py --pattern gosper_glider_gun --width 60 --height 40
```

Run with random initialization:
```bash
python main.py --random --density 0.3 --width 80 --height 40
```

## Dependencies

Install dependencies:
```bash
pip install -r requirements.txt
```

The only external dependency is `numpy>=1.20.0`.

## Architecture

The codebase follows a modular architecture with clear separation of concerns:

### Core Components

- **`game_of_life/grid.py`**: Contains `GameGrid` class that manages the 2D NumPy grid and implements the Game of Life rules using vectorized operations. The `step()` method uses `np.roll()` to efficiently count neighbors by creating 8 shifted copies of the grid and summing them.

- **`game_of_life/renderer.py`**: Contains `TerminalRenderer` class that handles all terminal output using ANSI escape codes. Builds frames as string buffers for efficient rendering.

- **`game_of_life/patterns.py`**: Defines all predefined patterns as lists of `(row, col)` tuples in the `PATTERNS` dictionary. Includes spaceships, oscillators, methuselahs, and infinite growth patterns.

- **`game_of_life/controls.py`**: Contains `InputHandler` context manager that provides non-blocking keyboard input with cross-platform support (Unix/Mac using `termios`/`tty`/`select`, Windows using `msvcrt`).

- **`main.py`**: Entry point with the game loop. Handles command-line argument parsing, initializes components, manages game state (generation count, pause state, FPS), and orchestrates the render-input-update cycle.

### Key Design Patterns

- **Toroidal Grid**: The grid uses wrap-around boundaries where edges connect to opposite sides (implemented via NumPy's `roll()` and modulo arithmetic).

- **Vectorized Operations**: All grid updates use NumPy's vectorized operations for performance - no Python loops over cells.

- **Non-blocking Input**: The `InputHandler` uses platform-specific APIs to read keyboard input without blocking the game loop.

- **State Management**: The game maintains both current grid state and initial grid state (for reset functionality).

## Adding New Patterns

To add a new pattern, add an entry to the `PATTERNS` dictionary in `game_of_life/patterns.py`:

```python
'pattern_name': [
    (row1, col1),
    (row2, col2),
    # ... more coordinates
]
```

Coordinates are relative to the placement position (typically the center of the grid).
