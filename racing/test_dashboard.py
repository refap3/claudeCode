#!/usr/bin/env python3
"""Test the car dashboard/cockpit visualization"""

from racing_game import Car

# Create a car
car = Car(x=50, y=50, angle=0, speed=2.5)

# Simulate the dashboard display
screen_width = 80
hood_width = min(60, screen_width - 4)

print("Car Dashboard/Cockpit Visualization")
print("=" * screen_width)
print()

# Top of hood (narrow, far from driver)
top_width = hood_width // 3
print(" " * ((screen_width - top_width) // 2) + "█" * top_width)

# Hood getting wider (approaching driver)
for i in range(1, 4):
    width = top_width + (hood_width - top_width) * i // 3
    print(" " * ((screen_width - width) // 2) + "▓" * width)

# Dashboard/windshield frame
frame_width = min(hood_width + 20, screen_width - 2)
left_margin = (screen_width - frame_width) // 2

# Instrument cluster
speed_display = f"[SPD:{car.speed:.1f}]"
print(" " * left_margin + "╔" + "═" * (frame_width - 2) + "╗")
print(" " * left_margin + "║" + speed_display.center(frame_width - 2) + "║")

print()
print("=" * screen_width)
print("\nThis is what appears at the bottom of the screen, showing:")
print("  - Car hood (█ and ▓ blocks) extending from your viewpoint")
print("  - Gets wider as it comes toward you (perspective)")
print("  - Dashboard frame with speed display")
print("\n✓ You're now sitting IN the car looking forward!")
