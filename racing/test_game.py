#!/usr/bin/env python3
"""Quick test to verify the game runs without errors"""

import sys
import curses

# Test import
try:
    from racing_game import Game, Car, Track, FirstPersonRenderer
    print("✓ All classes imported successfully")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test FirstPersonRenderer instantiation
try:
    renderer = FirstPersonRenderer()
    print("✓ FirstPersonRenderer created successfully")
except Exception as e:
    print(f"✗ FirstPersonRenderer error: {e}")
    sys.exit(1)

# Test basic methods
try:
    car = Car(x=50, y=50, angle=0)
    future_x, future_y = renderer.calculate_future_position(car, 10)
    print(f"✓ calculate_future_position works: ({future_x:.1f}, {future_y:.1f})")
except Exception as e:
    print(f"✗ Method error: {e}")
    sys.exit(1)

print("\n✓ All basic tests passed! The game should work.")
print("Run: python3 racing_game.py")
