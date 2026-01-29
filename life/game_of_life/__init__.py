"""Conway's Game of Life implementation with terminal visualization."""

from .grid import GameGrid
from .renderer import TerminalRenderer
from .patterns import PATTERNS, get_pattern

__all__ = ['GameGrid', 'TerminalRenderer', 'PATTERNS', 'get_pattern']
