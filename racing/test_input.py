#!/usr/bin/env python3
"""Test input handler to debug arrow key issues"""

import sys
import time

# Configure Windows console for UTF-8 output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    import msvcrt

print("Arrow Key Debug Test")
print("=" * 50)
print("Press arrow keys to test detection")
print("Press 'q' to quit")
print()

key_counts = {'up': 0, 'down': 0, 'left': 0, 'right': 0}

while True:
    if sys.platform == 'win32':
        if msvcrt.kbhit():
            first_byte = msvcrt.getch()

            # Check for quit
            if first_byte == b'q':
                break

            # Check for special keys
            if first_byte in (b'\xe0', b'\x00'):
                print(f"First byte: {first_byte.hex()}", end=" -> ")

                # Wait for second byte with retry
                second_byte = None
                for attempt in range(10):
                    if msvcrt.kbhit():
                        second_byte = msvcrt.getch()
                        print(f"Second byte: {second_byte.hex()} (attempt {attempt+1})", end=" -> ")
                        break
                    time.sleep(0.001)

                if second_byte is None:
                    print("TIMEOUT - no second byte!")
                    continue

                # Map to arrow key
                arrow_map = {
                    b'H': 'UP',
                    b'P': 'DOWN',
                    b'M': 'RIGHT',
                    b'K': 'LEFT',
                }

                if second_byte in arrow_map:
                    direction = arrow_map[second_byte]
                    key_counts[direction.lower()] += 1
                    print(f"{direction} (total: {key_counts[direction.lower()]})")
                else:
                    print(f"Unknown key code: {second_byte.hex()}")
            else:
                print(f"Regular key: {first_byte}")

    time.sleep(0.01)

print()
print("=" * 50)
print("Final counts:")
for direction, count in key_counts.items():
    print(f"  {direction.upper()}: {count}")
