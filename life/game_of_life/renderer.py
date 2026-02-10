"""Terminal rendering with ANSI codes."""

import sys


class TerminalRenderer:
    """Renders the Game of Life grid to the terminal."""

    def __init__(self, alive_char='█', dead_char=' '):
        """
        Initialize the renderer.

        Args:
            alive_char: Character to represent alive cells
            dead_char: Character to represent dead cells
        """
        self.alive_char = alive_char
        self.dead_char = dead_char

    def clear_screen(self):
        """Clear the terminal screen using ANSI escape codes."""
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()

    def move_cursor_home(self):
        """Move cursor to home position without clearing screen."""
        sys.stdout.write('\033[H')
        sys.stdout.flush()

    def render(self, grid, generation, fps, paused=False,
               placement_mode=False, placement_pattern=None, placement_x=0, placement_y=0):
        """
        Render the grid to the terminal.

        Args:
            grid: GameGrid instance
            generation: Current generation number
            fps: Current frames per second
            paused: Whether the simulation is paused
            placement_mode: Whether in pattern placement mode
            placement_pattern: Pattern to preview (if in placement mode)
            placement_x: X position of pattern preview
            placement_y: Y position of pattern preview
        """
        # Move cursor to home instead of clearing to reduce flicker
        self.move_cursor_home()

        # Build frame as string buffer for efficient rendering
        lines = []

        # Title
        lines.append("=" * (grid.width + 2))
        lines.append(" Conway's Game of Life ".center(grid.width + 2))
        lines.append("=" * (grid.width + 2))
        lines.append("")

        # Create preview grid if in placement mode
        display_grid = grid
        if placement_mode and placement_pattern:
            display_grid = grid.copy()
            display_grid.place_pattern(placement_pattern, placement_x, placement_y)

        # Grid visualization
        for row in display_grid.grid:
            line = ''.join(self.alive_char if cell else self.dead_char for cell in row)
            lines.append(f"|{line}|")

        lines.append("=" * (grid.width + 2))
        lines.append("")

        # Status line
        if placement_mode:
            status = "PLACEMENT MODE - Use arrows to move, [ENTER] to place, [ESC] to cancel"
        else:
            status = f"Generation: {generation} | Population: {grid.get_population()} | FPS: {fps:.1f}"
            if paused:
                status += " | PAUSED"
        lines.append(status)
        lines.append("")

        # Controls footer
        lines.append("Controls:")
        lines.append("  [SPACE] Pause/Play  [N] Next (when paused)  [R] Reset  [C] Clear  [X] Random")
        lines.append("  [+/-] Speed  [1-9] Select pattern (position with arrows, [ENTER] confirm)  [Q/ESC] Quit")

        # Print entire frame at once
        sys.stdout.write('\n'.join(lines))
        sys.stdout.flush()
