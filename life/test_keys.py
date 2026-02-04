#!/usr/bin/env python3
"""Test script to see what escape sequences arrow keys send."""

import sys
import termios
import tty
from game_of_life.controls import InputHandler

print("Press arrow keys to see their escape sequences.")
print("Press 'q' to quit.\n")

try:
    with InputHandler() as input_handler:
        while True:
            key = input_handler.get_key()
            if key:
                if key.lower() == 'q':
                    break
                # Show the key representation
                print(f"Key: {repr(key)} | Length: {len(key)} | Bytes: {key.encode('unicode_escape').decode('ascii')}")
                sys.stdout.flush()
except KeyboardInterrupt:
    pass
finally:
    print("\nDone!")
