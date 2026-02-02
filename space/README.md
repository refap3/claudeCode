# Space Shooter

A classic arcade-style space shooter game built with Pygame featuring dynamic difficulty scaling.

## Description

Control a spaceship (▲) and defend against waves of enemies (▼) descending from above. The game features progressive difficulty that increases as you lose lives, making it more challenging as the stakes get higher.

## Requirements

- Python 3.x
- Pygame library

Install Pygame:
```bash
pip install pygame
```

## Running the Game

```bash
python3 space3.py
```

## Controls

- **Left/Right Arrow Keys**: Move spaceship horizontally
- **Space**: Shoot bullets
- **Close Window**: Quit game

## Game Mechanics

### Objective
Shoot down enemy ships before they reach the bottom of the screen. Each destroyed enemy earns you 10 points.

### Lives System
- Start with 3 lives
- Each life allows up to 5 misses (enemies reaching the bottom)
- When you accumulate 5 misses, you lose 1 life and the miss counter resets
- Game ends when all lives are lost

### Dynamic Difficulty
The game automatically adjusts difficulty based on your remaining lives:

- **3 Lives**: Normal difficulty
  - Enemy spawn rate: 1000ms
  - Enemy speed: 1x

- **2 Lives**: Increased difficulty
  - Enemy spawn rate: 750ms
  - Enemy speed: 1.5x

- **1 Life**: Maximum difficulty
  - Enemy spawn rate: 500ms
  - Enemy speed: 2x

### Scoring
- Each enemy destroyed: +10 points
- Your final score is displayed on the game over screen

## Visual Design

- **Player**: White triangle (▲)
- **Enemies**: Red inverted triangle (▼)
- **Bullets**: Yellow dot (•)
- **Background**: Black space

## Game Over

When all lives are exhausted, the game displays:
- "GAME OVER" message
- Your final score
- Press any key to exit
