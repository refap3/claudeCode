# Conway's Game of Life

A terminal-based implementation of Conway's Game of Life in Python with interactive controls and visualization.

## Features

- Fast NumPy-based grid computation
- Terminal visualization with ANSI codes
- Interactive keyboard controls
- Multiple classic patterns (glider, blinker, pulsar, etc.)
- Adjustable speed and grid size
- Random initialization option
- Toroidal grid wrapping

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Or install numpy directly:

```bash
pip install numpy
```

## Usage

### Basic Usage

Run with default settings (200x60 grid, gosper_glider_gun pattern):

```bash
python main.py
```

### Command-Line Options

```bash
python main.py [OPTIONS]

Options:
  -w, --width WIDTH        Grid width (default: 200)
  -H, --height HEIGHT      Grid height (default: 60)
  --fps FPS                Frames per second (default: 10)
  -p, --pattern PATTERN    Initial pattern name
  -r, --random             Random initialization
  --density DENSITY        Density for random init (0.0-1.0, default: 0.3)
  -h, --help               Show help message
```

### Examples

Run with a specific pattern:

```bash
python main.py --pattern gosper_glider_gun --width 60 --height 40
```

Run with random initialization:

```bash
python main.py --random --width 80 --height 40 --fps 15
```

Run with custom density:

```bash
python main.py --random --density 0.4 --width 60 --height 30
```

Start with diehard methuselah (dies after 130 generations):

```bash
python main.py --pattern diehard --fps 5
```

## Interactive Controls

While the simulation is running:

- **SPACE**: Pause/play the simulation
- **N**: Step to next generation (when paused)
- **R**: Reset to initial state
- **C**: Clear the grid
- **+/-**: Increase/decrease speed
- **1-9**: Load patterns by number:
  1. acorn
  2. diehard
  3. glider
  4. gosper_glider_gun
  5. lwss
  6. pulsar
  7. queen_bee_shuttle
  8. r_pentomino
  9. switch_engine
- **Q** or **ESC**: Quit

## Available Patterns

### Spaceships (Moving Patterns)
- **glider**: Small spaceship that moves diagonally
- **lwss**: Lightweight spaceship (moves horizontally)

### Glider Guns (Pattern Generators)
- **gosper_glider_gun**: Classic Gosper glider gun (creates gliders infinitely)

### Oscillators (Repeating Patterns)
- **pulsar**: Beautiful 3-period oscillator
- **queen_bee_shuttle**: Period 30 oscillator with gliders bouncing between two sides

### Infinite Growth
- **switch_engine**: Creates infinite growth - keeps expanding forever!

### Methuselahs (Long-Lived Evolvers)
- **r_pentomino**: Stabilizes after 1103 generations
- **acorn**: Stabilizes after 5206 generations
- **diehard**: Dies completely after 130 generations (rare!)

## How It Works

Conway's Game of Life is a cellular automaton with simple rules:

1. Any live cell with 2-3 live neighbors survives
2. Any dead cell with exactly 3 live neighbors becomes alive
3. All other cells die or stay dead

Despite these simple rules, the Game of Life exhibits complex emergent behavior with patterns that oscillate, move, and interact in fascinating ways.

## Implementation Details

- **Grid**: NumPy 2D array for efficient vectorized operations
- **Neighbor counting**: Uses `np.roll()` to create shifted copies and sum neighbors
- **Rendering**: ANSI escape codes for terminal output
- **Input**: Non-blocking keyboard input with cross-platform support
- **Boundary**: Toroidal wrapping (edges wrap around)

## Performance

The implementation uses NumPy for vectorized operations, providing excellent performance:

- 200x60 grid (default): 20+ FPS
- 100x100 grid: 20+ FPS
- 200x200 grid: 10+ FPS

## Project Structure

```
life/
├── game_of_life/
│   ├── __init__.py      # Package initialization
│   ├── grid.py          # Grid data structure and Game of Life rules
│   ├── renderer.py      # Terminal rendering
│   ├── patterns.py      # Predefined patterns
│   └── controls.py      # Input handling
├── main.py              # Entry point with game loop
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## License

Public domain. Do whatever you want with it.

## Credits

Conway's Game of Life was invented by mathematician John Horton Conway in 1970.
