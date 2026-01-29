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

    def render(self, grid, generation, fps, paused=False):
        """
        Render the grid to the terminal.

        Args:
            grid: GameGrid instance
            generation: Current generation number
            fps: Current frames per second
            paused: Whether the simulation is paused
        """
        self.clear_screen()

        # Build frame as string buffer for efficient rendering
        lines = []

        # Title
        lines.append("=" * (grid.width + 2))
        lines.append(" Conway's Game of Life ".center(grid.width + 2))
        lines.append("=" * (grid.width + 2))
        lines.append("")

        # Grid visualization
        for row in grid.grid:
            line = ''.join(self.alive_char if cell else self.dead_char for cell in row)
            lines.append(f"|{line}|")

        lines.append("=" * (grid.width + 2))
        lines.append("")

        # Status line
        status = f"Generation: {generation} | Population: {grid.get_population()} | FPS: {fps:.1f}"
        if paused:
            status += " | PAUSED"
        lines.append(status)
        lines.append("")

        # Controls footer
        lines.append("Controls:")
        lines.append("  [SPACE] Pause/Play  [N] Next (when paused)  [R] Reset  [C] Clear  [X] Random")
        lines.append("  [+/-] Speed  [1-9] Load pattern  [Q/ESC] Quit")

        # Print entire frame at once
        sys.stdout.write('\n'.join(lines))
        sys.stdout.flush()
