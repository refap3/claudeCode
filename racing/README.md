# Terminal Racing Game

A fast-paced arcade racing game that runs in your terminal! Race around an oval track from a top-down perspective, compete for lap times, and master the physics-based driving.

## Features

- 🏎️ **Physics-based driving** - Realistic acceleration, braking, and momentum
- 🏁 **Lap timing** - Track your best and last lap times
- 👀 **Top-down view** - See the entire track from a bird's eye perspective
- 🎮 **Simple controls** - Drive with arrow keys
- 🖥️ **Cross-platform** - Works on Windows, macOS, and Linux
- 📦 **Minimal dependencies** - Standard library only (Windows needs `pip install windows-curses`)

## Quick Start

```bash
python racing_game.py
```

That's it! No installation required.

## Controls

| Key | Action |
|-----|--------|
| ↑ | Accelerate forward |
| ↓ | Brake / Reverse |
| ← | Turn left |
| → | Turn right |
| Space | Pause / Unpause |
| Q | Quit game |

## How to Play

1. **Start the game** - Your car (▼) starts on the right side of the track at the finish line, facing down
2. **Accelerate** - Press the up arrow to build speed in the direction you're facing
3. **Steer** - Use left/right arrows to turn and navigate the oval track
4. **Complete laps** - Drive counter-clockwise: down → left → up → right → finish!
5. **Beat your time** - Try to set the fastest lap time!

## Game View

```
                    #############
                 ###             ###
               ##                   ##
              #                       #     Track boundary (#)
             #                         #
             #  =====▼=====            #    Your car (▼) + Finish line (=)
             #                         #
              #                       #
               ##                   ##
                 ###             ###
                    #############
====================================
Speed: 2.5 | Time: 15.34s | Laps: 2
Last Lap: 12.45s | Best: 11.23s
```

## Tips

- **Take corners smoothly** - Don't accelerate through tight turns
- **Use the whole track** - The track is wide, use all available space
- **Watch your speed** - Going too fast makes turning harder
- **Practice the racing line** - Find the optimal path around the oval
- **Don't hit the walls** - Collisions will slow you down significantly

## Requirements

- Python 3.x
- Terminal with UTF-8 support (for arrow characters)
- Minimum terminal size: 100x55 characters (recommended)
- Windows only: `pip install windows-curses`

## Technical Details

- Runs at 30 FPS
- Physics-based velocity system with friction
- Elliptical track boundaries with collision detection
- Two-phase checkpoint system prevents lap count exploits
- Cross-platform input handling (msvcrt on Windows, termios on Unix)

## Credits

Built with Python and ANSI terminal codes. No external dependencies required.

Enjoy the race! 🏁
