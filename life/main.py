#!/usr/bin/env python3
"""Conway's Game of Life - Main entry point."""

import argparse
import time
import sys

from game_of_life import GameGrid, TerminalRenderer, PATTERNS, get_pattern
from game_of_life.controls import InputHandler


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Conway's Game of Life with terminal visualization"
    )
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=200,
        help='Grid width (default: 200)'
    )
    parser.add_argument(
        '-H', '--height',
        type=int,
        default=60,
        help='Grid height (default: 60)'
    )
    parser.add_argument(
        '--fps',
        type=float,
        default=10.0,
        help='Frames per second (default: 10)'
    )
    parser.add_argument(
        '-p', '--pattern',
        type=str,
        help=f'Initial pattern name. Available: {", ".join(sorted(PATTERNS.keys()))}'
    )
    parser.add_argument(
        '-r', '--random',
        action='store_true',
        help='Random initialization'
    )
    parser.add_argument(
        '--density',
        type=float,
        default=0.3,
        help='Density for random initialization (0.0 to 1.0, default: 0.3)'
    )
    return parser.parse_args()


def main():
    """Main game loop."""
    args = parse_args()

    # Initialize game components
    grid = GameGrid(args.width, args.height)
    renderer = TerminalRenderer()
    initial_grid = None

    # Initialize grid based on arguments
    if args.pattern:
        pattern = get_pattern(args.pattern)
        if pattern:
            # Center the pattern
            center_x = args.width // 2
            center_y = args.height // 2
            grid.place_pattern(pattern, center_x, center_y)
            initial_grid = grid.copy()
        else:
            print(f"Error: Pattern '{args.pattern}' not found.")
            print(f"Available patterns: {', '.join(sorted(PATTERNS.keys()))}")
            sys.exit(1)
    elif args.random:
        grid.randomize(args.density)
        initial_grid = grid.copy()
    else:
        # Default: place a gosper glider gun
        center_x = args.width // 2
        center_y = args.height // 2
        grid.place_pattern(get_pattern('gosper_glider_gun'), center_x, center_y)
        initial_grid = grid.copy()

    # Game state
    generation = 0
    paused = False
    running = True
    target_fps = args.fps
    frame_time = 1.0 / target_fps

    # Placement mode state
    placement_mode = False
    placement_pattern = None
    placement_x = args.width // 2
    placement_y = args.height // 2

    # Key buffer for detecting multi-character escape sequences
    key_buffer = ""
    last_key_time = time.time()

    try:
        with InputHandler() as input_handler:
            while running:
                frame_start = time.time()

                # Handle input (non-blocking)
                key = input_handler.get_key()

                # Accumulate keys in buffer for multi-character sequences
                current_time = time.time()
                if key:
                    # Reset buffer if too much time has passed (0.2 seconds)
                    if current_time - last_key_time > 0.2:
                        key_buffer = ""
                    key_buffer += key
                    last_key_time = current_time

                    # Keep buffer from growing too large
                    if len(key_buffer) > 5:
                        key_buffer = key_buffer[-5:]

                # Detect complete arrow sequences in buffer
                arrow_detected = False
                if placement_mode:
                    if '\x1b[A' in key_buffer or key_buffer.endswith('[A'):  # Up arrow
                        placement_y = (placement_y - 1) % args.height
                        key_buffer = ""
                        arrow_detected = True
                    elif '\x1b[B' in key_buffer or key_buffer.endswith('[B'):  # Down arrow
                        placement_y = (placement_y + 1) % args.height
                        key_buffer = ""
                        arrow_detected = True
                    elif '\x1b[C' in key_buffer or key_buffer.endswith('[C'):  # Right arrow
                        placement_x = (placement_x + 1) % args.width
                        key_buffer = ""
                        arrow_detected = True
                    elif '\x1b[D' in key_buffer or key_buffer.endswith('[D'):  # Left arrow
                        placement_x = (placement_x - 1) % args.width
                        key_buffer = ""
                        arrow_detected = True

                # Process individual keys only if we didn't detect an arrow
                if key and not arrow_detected:
                    key_lower = key.lower()

                    # Handle placement mode inputs
                    if placement_mode:
                        if key in ('\n', '\r'):  # Enter - confirm placement
                            grid.place_pattern(placement_pattern, placement_x, placement_y)
                            initial_grid = grid.copy()
                            placement_mode = False
                            key_buffer = ""
                        elif key_lower == 'q':  # Allow quit during placement
                            running = False
                        elif key == '\x1b' and len(key_buffer) == 1:  # ESC only if alone
                            # Wait a bit to see if it's part of arrow sequence
                            pass  # Do nothing, wait for next keys
                        # Ignore other keys in placement mode
                    else:
                        # Normal mode inputs
                        if key == ' ':
                            # Pause/play
                            paused = not paused
                            key_buffer = ""
                        elif key_lower == 'q':
                            # Quit
                            running = False
                        elif key == '\x1b' and '\x1b[' not in key_buffer:
                            # ESC to quit (but only if not part of arrow sequence)
                            # Wait briefly to ensure it's not an arrow key
                            if len(key_buffer) == 1 and current_time - last_key_time > 0.15:
                                running = False
                                key_buffer = ""
                        elif key_lower == 'r':
                            # Reset to initial state
                            if initial_grid:
                                grid = initial_grid.copy()
                                generation = 0
                            key_buffer = ""
                        elif key_lower == 'c':
                            # Clear grid
                            grid.clear()
                            generation = 0
                            key_buffer = ""
                        elif key_lower == 'x':
                            # Randomize grid
                            grid.randomize(args.density)
                            initial_grid = grid.copy()
                            generation = 0
                            key_buffer = ""
                        elif key_lower == 'n' and paused:
                            # Step one generation when paused
                            grid.step()
                            generation += 1
                            key_buffer = ""
                        elif key == '+' or key == '=':
                            # Increase speed
                            target_fps = min(target_fps + 2, 60)
                            frame_time = 1.0 / target_fps
                            key_buffer = ""
                        elif key == '-' or key == '_':
                            # Decrease speed
                            target_fps = max(target_fps - 2, 1)
                            frame_time = 1.0 / target_fps
                            key_buffer = ""
                        elif key.isdigit() and key != '0':
                            # Enter placement mode
                            pattern_list = sorted(PATTERNS.keys())
                            pattern_idx = int(key) - 1
                            if pattern_idx < len(pattern_list):
                                pattern_name = pattern_list[pattern_idx]
                                placement_pattern = get_pattern(pattern_name)
                                placement_x = args.width // 2
                                placement_y = args.height // 2
                                placement_mode = True
                                key_buffer = ""

                # Update game state (if not paused and not in placement mode)
                if not paused and not placement_mode:
                    grid.step()
                    generation += 1

                # Render frame
                renderer.render(grid, generation, target_fps, paused,
                               placement_mode, placement_pattern, placement_x, placement_y)

                # Maintain frame rate
                elapsed = time.time() - frame_start
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)

    except KeyboardInterrupt:
        pass
    finally:
        # Clean up
        renderer.clear_screen()
        print("Thanks for playing Conway's Game of Life!")


if __name__ == '__main__':
    main()
