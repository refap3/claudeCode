#!/usr/bin/env python3
"""Test track width rendering"""

import math
from racing_game import Car, Track, FirstPersonRenderer

# Create test objects
car = Car(x=50, y=25, angle=0)
track = Track(width=100, height=50)
renderer = FirstPersonRenderer()

print("Track Width Visualization Test")
print("=" * 80)

# Simulate various distances and show track width in screen characters
screen_width = 80
view_height = 30

print(f"\nScreen width: {screen_width} characters")
print(f"Track width scale: {renderer.track_width_scale}x")
print()

print("Distance | Perspective | World Width | Screen Width | Visualization")
print("-" * 80)

for row in [0, 5, 10, 15, 20, 25, 29]:
    t = row / view_height
    distance = renderer.min_distance + (renderer.max_distance - renderer.min_distance) * (1 - t)

    # Calculate future position
    future_x, future_y = renderer.calculate_future_position(car, distance)

    # Get track boundaries
    left_dist, right_dist = renderer.find_track_boundaries(track, future_x, future_y, car.angle)

    # Apply perspective scaling
    perspective_scale = renderer.min_distance / distance

    # Calculate screen width
    screen_left = left_dist * perspective_scale * renderer.track_width_scale
    screen_right = right_dist * perspective_scale * renderer.track_width_scale
    total_screen_width = int(screen_left + screen_right)

    # Create visualization
    world_width = left_dist + right_dist
    viz_chars = min(total_screen_width, 30)
    viz = '|' + '=' * viz_chars + '|'

    print(f"{distance:5.1f}   | {perspective_scale:5.3f}     | {world_width:5.1f}       | {total_screen_width:4d}         | {viz}")

print()
print("✓ Track should now be visible with widths ranging from ~2-30 characters")
print("  Far distance: narrow (compressed perspective)")
print("  Near distance: wide (full width)")
