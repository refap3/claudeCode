# Claude Code Experiments

A collection of terminal-based Python games and simulations created with Claude Code.

## Projects

### 🎮 [Racing Game](./racing)

A terminal-based first-person arcade racing game (like OutRun) with physics-based car movement on an oval track.

- First-person perspective rendering with track curvature
- Real-time physics simulation with velocity, acceleration, and friction
- Lap timing and tracking system
- Arrow key controls with intuitive handling
- Curses-based terminal rendering

**Quick start:**
```bash
cd racing
python3 racing_game.py
```

### 🔬 [Conway's Game of Life](./life)

A terminal implementation of Conway's Game of Life with interactive controls and visualization.

- Fast NumPy-based grid computation
- Multiple classic patterns (gliders, oscillators, spaceships, and more)
- Interactive keyboard controls for real-time manipulation
- Adjustable speed and grid size

**Quick start:**
```bash
cd life
pip install -r requirements.txt
python main.py
```

### 🚀 [Space Shooter](./space)

A classic arcade-style space shooter game with dynamic difficulty scaling.

- Progressive difficulty that increases as lives decrease
- Lives system with miss tracking (5 misses = 1 life lost)
- Dynamic enemy spawn rates and speeds
- Score tracking and game over screen
- Built with Pygame

**Quick start:**
```bash
cd space
pip install pygame
python3 space3.py
```

## Requirements

- Python 3.x
- For racing game: curses library (standard on Unix/macOS, requires windows-curses on Windows)
- For Game of Life: numpy
- For space shooter: pygame

## License

Public domain. Do whatever you want with these projects.
