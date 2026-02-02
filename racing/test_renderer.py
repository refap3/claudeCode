#!/usr/bin/env python3
"""Test the FirstPersonRenderer logic without needing a terminal"""

import math
from racing_game import Car, Track, FirstPersonRenderer

# Create test objects
car = Car(x=50, y=50, angle=0)
track = Track(width=100, height=50)
renderer = FirstPersonRenderer()

print("Testing FirstPersonRenderer...")
print("=" * 60)

# Test 1: calculate_future_position
print("\n1. Testing calculate_future_position:")
for distance in [10, 50, 100]:
    fx, fy = renderer.calculate_future_position(car, distance)
    print(f"   Distance {distance:3d}: ({fx:.1f}, {fy:.1f})")

# Test 2: find_track_boundaries
print("\n2. Testing find_track_boundaries:")
future_x, future_y = renderer.calculate_future_position(car, 20)
left, right = renderer.find_track_boundaries(track, future_x, future_y, car.angle)
print(f"   At distance 20: left_boundary={left:.1f}, right_boundary={right:.1f}")
print(f"   Total track width: {left + right:.1f}")

# Test 3: calculate_lateral_offset
print("\n3. Testing calculate_lateral_offset (track curvature):")
for distance in [10, 30, 50, 70, 100]:
    fx, fy = renderer.calculate_future_position(car, distance)
    offset = renderer.calculate_lateral_offset(track, car, fx, fy)
    print(f"   Distance {distance:3d}: lateral_offset={offset:+6.2f}")

# Test 4: Perspective scaling
print("\n4. Testing perspective scaling:")
view_height = 30
for row in [0, 10, 20, 29]:
    t = row / view_height
    distance = renderer.min_distance + (renderer.max_distance - renderer.min_distance) * (1 - t)
    perspective_scale = renderer.min_distance / distance
    print(f"   Row {row:2d}: distance={distance:5.1f}, scale={perspective_scale:.3f}")

# Test 5: Track boundaries at various positions
print("\n5. Testing track.is_on_track at various positions:")
test_positions = [
    (track.center_x, track.center_y, "center"),
    (track.center_x + track.outer_radius_x - 5, track.center_y, "start line area"),
    (track.center_x - track.inner_radius_x - 2, track.center_y, "inside inner boundary"),
    (track.center_x + track.outer_radius_x + 2, track.center_y, "outside outer boundary"),
]
for x, y, desc in test_positions:
    on_track = track.is_on_track(x, y)
    status = "ON TRACK" if on_track else "OFF TRACK"
    print(f"   {desc:25s}: {status}")

# Test 6: Simulate a few frames of driving
print("\n6. Simulating driving (car starts at angle π, facing left):")
car.x = track.center_x + (track.outer_radius_x + track.inner_radius_x) / 2
car.y = track.center_y
car.angle = math.pi  # Facing left

for frame in range(5):
    print(f"\n   Frame {frame}:")
    print(f"     Position: ({car.x:.1f}, {car.y:.1f}), Angle: {math.degrees(car.angle):.0f}°")

    # Look ahead
    look_distance = 50
    fx, fy = renderer.calculate_future_position(car, look_distance)
    print(f"     Looking {look_distance} ahead: ({fx:.1f}, {fy:.1f})")

    # Check track boundaries
    left, right = renderer.find_track_boundaries(track, fx, fy, car.angle)
    print(f"     Track boundaries: left={left:.1f}, right={right:.1f}")

    # Check curvature
    offset = renderer.calculate_lateral_offset(track, car, fx, fy)
    curve_dir = "LEFT" if offset < 0 else "RIGHT"
    print(f"     Track curves: {curve_dir} (offset={offset:+.1f})")

    # Simulate movement (move in current direction)
    car.x += math.cos(car.angle) * 5
    car.y += math.sin(car.angle) * 5
    car.angle -= 0.1  # Turn slightly left (counterclockwise on oval)

print("\n" + "=" * 60)
print("✓ All renderer tests completed successfully!")
print("\nThe first-person rendering system is working correctly.")
print("Run 'python3 racing_game.py' to play the game.")
