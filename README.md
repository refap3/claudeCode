# Claude Code Experiments

A collection of terminal-based Python games and simulations created with Claude Code.

## Projects

### 🎮 [Racing Game](./racing)

A terminal-based arcade racing game with physics-based car movement on an oval track.

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

## Requirements

- Python 3.x
- For racing game: curses library (standard on Unix/macOS, requires windows-curses on Windows)
- For Game of Life: numpy

## License

Public domain. Do whatever you want with these projects.
