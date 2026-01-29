"""Grid data structure and Game of Life rules implementation."""

import numpy as np


class GameGrid:
    """Grid for Conway's Game of Life with vectorized NumPy operations."""

    def __init__(self, width, height, wrap=True):
        """
        Initialize the grid.

        Args:
            width: Grid width
            height: Grid height
            wrap: Whether to use toroidal wrapping (edges wrap around)
        """
        self.width = width
        self.height = height
        self.wrap = wrap
        self.grid = np.zeros((height, width), dtype=int)

    def step(self):
        """Apply Game of Life rules for one generation."""
        neighbors = np.zeros_like(self.grid, dtype=int)

        # Sum all 8 neighbors using rolled copies
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                rolled = np.roll(np.roll(self.grid, dx, axis=0), dy, axis=1)
                neighbors += rolled

        # Apply rules: birth (dead + 3 neighbors) or survival (alive + 2-3 neighbors)
        birth = (self.grid == 0) & (neighbors == 3)
        survival = (self.grid == 1) & ((neighbors == 2) | (neighbors == 3))

        self.grid = (birth | survival).astype(int)

    def place_pattern(self, pattern, x, y):
        """
        Place a pattern on the grid at the specified position.

        Args:
            pattern: List of (row, col) tuples representing alive cells
            x: Starting x coordinate (column)
            y: Starting y coordinate (row)
        """
        for dy, dx in pattern:
            row = (y + dy) % self.height
            col = (x + dx) % self.width
            if 0 <= row < self.height and 0 <= col < self.width:
                self.grid[row, col] = 1

    def randomize(self, density=0.3):
        """
        Fill grid with random alive cells.

        Args:
            density: Probability of a cell being alive (0.0 to 1.0)
        """
        self.grid = (np.random.random((self.height, self.width)) < density).astype(int)

    def clear(self):
        """Clear the grid (set all cells to dead)."""
        self.grid.fill(0)

    def get_population(self):
        """Return the number of alive cells."""
        return np.sum(self.grid)

    def copy(self):
        """Create a copy of the current grid state."""
        new_grid = GameGrid(self.width, self.height, self.wrap)
        new_grid.grid = self.grid.copy()
        return new_grid
