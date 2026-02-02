# Racing Game - First-Person View Implementation

## What Changed

The racing game has been converted from a top-down view to a first-person perspective, similar to classic arcade racers like OutRun.

## New Architecture

### FirstPersonRenderer Class

A new `FirstPersonRenderer` class (lines 101-230) handles all first-person perspective rendering:

**Key Methods:**
- `calculate_future_position(car, distance)` - Projects a point ahead of the car
- `find_track_boundaries(track, center_x, center_y, perpendicular_angle)` - Ray-traces left/right to find track edges
- `calculate_lateral_offset(track, car, future_x, future_y)` - Determines how much the track curves
- `render_track_slice(win, screen_y, ...)` - Draws one horizontal line of the track
- `render_view(win, car, track, ...)` - Main rendering loop
- `render_dashboard(win, ...)` - Draws the car dashboard at bottom

## How It Works

### Perspective Rendering

The screen is divided into horizontal slices from top to bottom:
- **Top rows** = Far distance (narrow, compressed perspective)
- **Middle rows** = Medium distance
- **Bottom rows** = Near distance (wider)

For each row:
1. Calculate distance ahead using perspective formula
2. Project that point in world space ahead of the car
3. Find track boundaries at that point (ray-trace left/right)
4. Apply perspective scaling (closer = wider)
5. Calculate lateral offset (track curves left/right)
6. Draw: `[off-road] | [track surface] | [off-road]`

### Track Curvature

The track curves based on the car's position on the oval:
- Calculates angle from future position to track center
- Compares to car's heading angle
- Perpendicular component determines left/right shift
- Creates the visual effect of the track bending

### Visual Elements

- Track surface: `=` characters (road texture)
- Track edges: `|` characters (barriers)
- Finish line: Alternating `|` pattern when near start/finish
- Dashboard: ASCII art car dashboard at bottom
- HUD: Speed, time, laps, status at bottom

## Physics & Input

All existing physics and input systems remain unchanged:
- Car physics (velocity, friction, acceleration)
- Collision detection
- Lap tracking
- Input handling

Only the rendering has changed.

## Running the Game

```bash
python3 racing_game.py
```

**Controls:**
- Arrow keys: Drive (up=accelerate, down=brake, left/right=turn)
- Space: Pause
- Q: Quit

## Parameters to Tune

In `FirstPersonRenderer.__init__()`:
- `min_distance` (5.0): Nearest visible distance
- `max_distance` (100.0): Farthest visible distance
- `num_slices` (30): Number of scan lines (affects detail)

In `calculate_lateral_offset()`:
- Lateral offset scale (15.0): Controls how much track curves

In `render_track_slice()`:
- Visual characters: road_char, edge_char
- Colors: Adjust curses color pairs

## Implementation Details

### Perspective Math

```python
# Distance calculation
t = row / view_height  # 0 at top, 1 at bottom
distance = min_distance + (max_distance - min_distance) * (1 - t)

# Perspective scaling
perspective_scale = min_distance / distance
```

Objects get wider as they get closer (smaller distance = larger scale).

### Track Boundary Detection

Ray-tracing perpendicular to car direction:
```python
# Search left
test_x = center_x + cos(angle - π/2) * dist
test_y = center_y + sin(angle - π/2) * dist
if not track.is_on_track(test_x, test_y): found_boundary
```

### Lateral Offset (Curvature)

```python
# Angle from future position to track center
to_center_angle = atan2(center_y - future_y, center_x - future_x)

# Compare to car heading
angle_diff = to_center_angle - car.angle

# Perpendicular component = lateral shift
lateral_offset = sin(angle_diff) * scale
```

## Known Limitations

- Track must be convex (oval works, complex shapes may not)
- Terminal size affects view quality (larger = better)
- Perspective simplified (doesn't account for vertical angles)
- Ray-tracing is basic (can be optimized for complex tracks)

## Testing

Basic tests can be run with:
```bash
python3 test_game.py
```

This verifies imports and basic functionality without launching the full game.
