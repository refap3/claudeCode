# Racing Game - Quick Start Guide

## Installation

No installation needed! Just Python 3 with curses (standard on Unix/macOS).

```bash
cd /Users/rainers/claudeExperiments/racing
python3 racing_game.py
```

## Controls

| Key | Action |
|-----|--------|
| ↑ | Accelerate forward |
| ↓ | Brake / Reverse |
| ← | Turn left |
| → | Turn right |
| Space | Pause / Unpause |
| Q | Quit game |

## Gameplay

### Objective
Complete laps around the oval track as fast as possible.

### How to Play
1. **Accelerate** with ↑ arrow to start moving
2. **Turn** with ← → arrows to navigate the oval
3. **Stay on track** (between the `|` edges)
4. **Complete laps** by:
   - Driving through left side (checkpoint)
   - Crossing finish line on right side

### Screen Layout

```
┌─────────────────────────────────────┐
│       |===|         ← Far distance  │
│      |=====|                         │
│     |=======|                        │
│    |=========|       ← Track ahead   │
│   |===========|                      │
│  |=============|     ← Near distance │
│                                      │
│   _______________                    │
│  /               \   ← Dashboard     │
│ | RACING SIMULATOR|                  │
│  \_______________/                   │
├──────────────────────────────────────┤
│ Speed: 2.3  Time: 12.45s  Laps: 1   │ ← HUD
│ Last Lap: 13.22s  Best Lap: 12.45s  │
│ Controls: ↑↓←→ Space Q              │
└──────────────────────────────────────┘
```

### Visual Elements

| Symbol | Meaning |
|--------|---------|
| `=` | Road surface (on track) |
| `\|` | Track edges / barriers |
| Green road | You're on track ✓ |
| Red road | You're off track! ✗ |
| `\|` pattern | Finish line ahead |

### Tips

1. **Start slow** - Get a feel for the controls first
2. **Smooth turns** - Don't overcorrect
3. **Stay centered** - Middle of track is safest
4. **Watch the edges** - Track narrows at distance
5. **Use friction** - Let go of gas to slow naturally
6. **Practice** - Track gets easier with each lap

### Track Layout

The track is an oval with:
- **Right side**: Start/finish line
- **Top**: Curved turn
- **Left side**: Checkpoint (must pass for lap to count)
- **Bottom**: Curved turn back to finish

### Lap Completion

To complete a lap:
1. Start at finish line (right side)
2. Drive around left side (triggers checkpoint)
3. Return to finish line
4. Your lap time is recorded!

### HUD Information

- **Speed**: Current velocity (0.0 - 3.0)
- **Time**: Total race time
- **Laps**: Number of completed laps
- **Status**: ON TRACK or OFF TRACK!
- **Last Lap**: Previous lap time
- **Best Lap**: Fastest lap time

## Common Issues

### "Can't see track curves"
- Track curves left/right as you drive the oval
- Look for horizontal shifts in the `|` edges
- The track shifts more on the turns

### "Keep hitting walls"
- Start slower with less acceleration
- Turn more gradually
- Look further ahead (top of screen)
- Practice makes perfect!

### "Terminal too small"
- Resize terminal to at least 80x24
- Larger terminals give better view
- Full screen recommended

### "Game runs slow"
- Normal target is 30 FPS
- Close other terminal processes
- Try smaller terminal size

## Advanced Techniques

### Speed Control
```
Max speed:     ↑↑↑↑↑↑↑↑   (full throttle)
Cruising:      ↑___↑___   (pulse throttle)
Braking:       ___↓↓↓___  (brake before turn)
```

### Racing Line
```
Optimal path through oval:

      Start wide →  |==========|
                   |============|
     Apex inside → |============|
                   |============|
       Exit wide → |==========|
```

### Lap Strategy
1. **First lap**: Learn track, find limits
2. **Second lap**: Push harder, find racing line
3. **Later laps**: Optimize for best time

## Testing

Before playing, you can run tests:

```bash
# Basic tests
python3 test_game.py

# Detailed renderer tests
python3 test_renderer.py
```

## Documentation

- `README_FIRSTPERSON.md` - How the rendering works
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `VISUAL_COMPARISON.md` - Before/after comparison
- `CLAUDE.md` - Developer documentation

## Having Fun!

The goal is to **beat your best lap time**. The track is simple, but mastering it takes practice.

**Good luck, and enjoy the race!** 🏎️💨
