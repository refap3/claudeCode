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

    try:
        with InputHandler() as input_handler:
            while running:
                frame_start = time.time()

                # Handle input (non-blocking)
                key = input_handler.get_key()
                if key:
                    key_lower = key.lower()

                    if key == ' ':
                        # Pause/play
                        paused = not paused
                    elif key_lower == 'q' or key == '\x1b':
                        # Quit
                        running = False
                    elif key_lower == 'r':
                        # Reset to initial state
                        if initial_grid:
                            grid = initial_grid.copy()
                            generation = 0
                    elif key_lower == 'c':
                        # Clear grid
                        grid.clear()
                        generation = 0
                    elif key_lower == 'n' and paused:
                        # Step one generation when paused
                        grid.step()
                        generation += 1
                    elif key == '+' or key == '=':
                        # Increase speed
                        target_fps = min(target_fps + 2, 60)
                        frame_time = 1.0 / target_fps
                    elif key == '-' or key == '_':
                        # Decrease speed
                        target_fps = max(target_fps - 2, 1)
                        frame_time = 1.0 / target_fps
                    elif key.isdigit() and key != '0':
                        # Load pattern by number
                        pattern_list = sorted(PATTERNS.keys())
                        pattern_idx = int(key) - 1
                        if pattern_idx < len(pattern_list):
                            pattern_name = pattern_list[pattern_idx]
                            pattern = get_pattern(pattern_name)
                            grid.clear()
                            center_x = args.width // 2
                            center_y = args.height // 2
                            grid.place_pattern(pattern, center_x, center_y)
                            initial_grid = grid.copy()
                            generation = 0

                # Update game state (if not paused)
                if not paused:
                    grid.step()
                    generation += 1

                # Render frame
                renderer.render(grid, generation, target_fps, paused)

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
