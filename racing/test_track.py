#!/usr/bin/env python3
"""Test track boundary detection"""

import math
from racing_game import Car, Track

# Create track with same dimensions as game
width, height = 100, 50
track = Track(width, height)

print("Track Dimensions:")
print(f"  Center: ({track.center_x}, {track.center_y})")
print(f"  Outer radius: ({track.outer_radius_x}, {track.outer_radius_y})")
print(f"  Inner radius: ({track.inner_radius_x}, {track.inner_radius_y})")
print(f"  Track width: {track.outer_radius_x - track.inner_radius_x}")
print()

# Calculate starting position (same as Game.__init__)
track_width = (track.outer_radius_x - track.inner_radius_x) / 2
start_x = track.center_x + track.inner_radius_x + track_width
start_y = track.center_y

print("Car Starting Position:")
print(f"  Position: ({start_x}, {start_y})")
print()

# Create car
car = Car(x=start_x, y=start_y, angle=math.pi / 2)

# Test if starting position is on track
on_track = track.is_on_track(car.x, car.y)
print(f"Is car on track? {on_track}")

# Calculate distances for debugging
dx = car.x - track.center_x
dy = car.y - track.center_y
outer_dist = (dx * dx) / (track.outer_radius_x * track.outer_radius_x) + \
             (dy * dy) / (track.outer_radius_y * track.outer_radius_y)
inner_dist = (dx * dx) / (track.inner_radius_x * track.inner_radius_x) + \
             (dy * dy) / (track.inner_radius_y * track.inner_radius_y)

print()
print("Distance Calculations:")
print(f"  dx: {dx}, dy: {dy}")
print(f"  Outer distance: {outer_dist:.4f} (must be <= 1.0)")
print(f"  Inner distance: {inner_dist:.4f} (must be >= 1.0)")
print()

# Test positions around the starting point
print("Testing nearby positions:")
for offset in [-2, -1, 0, 1, 2]:
    test_x = start_x + offset
    test_y = start_y
    on_track = track.is_on_track(test_x, test_y)
    dx = test_x - track.center_x
    inner = (dx * dx) / (track.inner_radius_x * track.inner_radius_x)
    outer = (dx * dx) / (track.outer_radius_x * track.outer_radius_x)
    print(f"  ({test_x:.1f}, {test_y:.1f}): {on_track} (inner={inner:.3f}, outer={outer:.3f})")
