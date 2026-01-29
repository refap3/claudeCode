"""Predefined patterns for Conway's Game of Life."""

# Pattern definitions: list of (row, col) coordinates for alive cells
PATTERNS = {
    'glider': [
        (0, 1),
        (1, 2),
        (2, 0), (2, 1), (2, 2)
    ],
    'lwss': [  # Lightweight spaceship
        (0, 1), (0, 4),
        (1, 0),
        (2, 0), (2, 4),
        (3, 0), (3, 1), (3, 2), (3, 3)
    ],
    'pulsar': [
        # Top section
        (0, 2), (0, 3), (0, 4), (0, 8), (0, 9), (0, 10),
        (2, 0), (2, 5), (2, 7), (2, 12),
        (3, 0), (3, 5), (3, 7), (3, 12),
        (4, 0), (4, 5), (4, 7), (4, 12),
        (5, 2), (5, 3), (5, 4), (5, 8), (5, 9), (5, 10),
        # Bottom section
        (7, 2), (7, 3), (7, 4), (7, 8), (7, 9), (7, 10),
        (8, 0), (8, 5), (8, 7), (8, 12),
        (9, 0), (9, 5), (9, 7), (9, 12),
        (10, 0), (10, 5), (10, 7), (10, 12),
        (12, 2), (12, 3), (12, 4), (12, 8), (12, 9), (12, 10)
    ],
    'gosper_glider_gun': [  # Gosper glider gun
        # Left square
        (4, 0), (4, 1),
        (5, 0), (5, 1),
        # Left part
        (4, 10), (3, 11), (5, 11),
        (2, 12), (6, 12), (2, 13), (6, 13),
        (3, 15), (4, 16), (5, 15),
        (4, 17),
        (2, 14), (6, 14),
        # Right square
        (4, 20), (4, 21),
        (3, 20), (3, 21),
        (2, 22), (5, 22),
        (1, 24), (2, 24), (5, 24), (6, 24),
        # Far right
        (2, 34), (2, 35),
        (3, 34), (3, 35)
    ],
    'r_pentomino': [  # Methuselah - stabilizes after 1103 generations
        (0, 1), (0, 2),
        (1, 0), (1, 1),
        (2, 1)
    ],
    'diehard': [  # Dies completely after 130 generations
        (0, 6),
        (1, 0), (1, 1),
        (2, 1), (2, 5), (2, 6), (2, 7)
    ],
    'acorn': [  # Methuselah - stabilizes after 5206 generations
        (0, 1),
        (1, 3),
        (2, 0), (2, 1), (2, 4), (2, 5), (2, 6)
    ],
}


def get_pattern(name):
    """
    Get a pattern by name.

    Args:
        name: Pattern name (case-insensitive)

    Returns:
        List of (row, col) tuples or None if pattern not found
    """
    return PATTERNS.get(name.lower())


def list_patterns():
    """Return a list of available pattern names."""
    return sorted(PATTERNS.keys())
