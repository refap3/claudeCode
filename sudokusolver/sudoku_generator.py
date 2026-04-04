#!/usr/bin/env python3
"""
sudoku_generator.py — Sudoku Puzzle Generator

Generates valid Sudoku puzzles at a target difficulty tier using
randomised backtracking for solution generation and human-strategy
rating (via sudoku_tutor.py) for difficulty classification.

Difficulty tiers mirror those in sudoku_tutor.py:
  Tier 0 — Really Easy : Full House and Naked Single only
  Tier 1 — Beginner    : Full House, Naked Single, Hidden Single
  Tier 2 — Intermediate: Naked/Hidden Pairs/Triples/Quads,
                          Pointing Pairs, Box-Line Reduction
  Tier 3 — Advanced    : X-Wing, Swordfish, Y-Wing, XYZ-Wing, Simple Coloring
  Tier 4 — Expert      : Unique Rectangle, W-Wing, Skyscraper,
                          2-String Kite, BUG+1
"""

import random
import time
from copy import deepcopy
from typing import Optional

from sudoku_tutor import Grid, Step, ALL_STRATEGIES

# ─────────────────────────────────────────────────────────────────────────────
# Tier mapping: strategy name → difficulty tier (1=easiest, 4=hardest)
# ─────────────────────────────────────────────────────────────────────────────

STRATEGY_TIER = {
    "Full House": 1, "Naked Single": 1, "Hidden Single": 1,
    "Naked Pair": 2, "Hidden Pair": 2, "Naked Triple": 2, "Hidden Triple": 2,
    "Naked Quad": 2, "Hidden Quad": 2, "Pointing Pairs": 2, "Box-Line Reduction": 2,
    "X-Wing": 3, "Swordfish": 3, "Y-Wing": 3, "XYZ-Wing": 3, "Simple Coloring": 3,
    "Unique Rectangle": 4, "W-Wing": 4, "Skyscraper": 4, "2-String Kite": 4, "BUG+1": 4,
}

# Target empty-cell ranges per tier.  These are tuned empirically and act as
# a soft guide; the uniqueness constraint is always the hard stop.
# Note: maintaining a unique solution caps out at ~55-59 holes in practice,
# so tiers 2-4 share a similar range; difficulty comes from the strategy
# needed, not from hole count alone.
_EMPTY_RANGE = {
    0: (25, 36),   # Really Easy: few holes, Full House / Naked Single only
    1: (35, 50),
    2: (48, 57),
    3: (48, 57),
    4: (48, 57),
}

# Strategy names that qualify as tier-0 (really easy)
_TIER0_STRATEGY_NAMES = {"Full House", "Naked Single"}


# ─────────────────────────────────────────────────────────────────────────────
# Solution Generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_solution(seed: int | None = None) -> list[list[int]]:
    """Generate a complete valid Sudoku solution using randomised backtracking.

    Parameters
    ----------
    seed:
        Optional RNG seed for reproducible puzzles.

    Returns
    -------
    A 9×9 list of ints (1–9), representing a fully-filled, valid Sudoku grid.
    """
    rng = random.Random(seed)
    grid = [[0] * 9 for _ in range(9)]

    def _is_valid(r: int, c: int, d: int) -> bool:
        # Check row
        if d in grid[r]:
            return False
        # Check column
        if any(grid[rr][c] == d for rr in range(9)):
            return False
        # Check 3×3 box
        br, bc = (r // 3) * 3, (c // 3) * 3
        for dr in range(3):
            for dc in range(3):
                if grid[br + dr][bc + dc] == d:
                    return False
        return True

    def _backtrack(pos: int) -> bool:
        if pos == 81:
            return True
        r, c = divmod(pos, 9)
        digits = list(range(1, 10))
        rng.shuffle(digits)
        for d in digits:
            if _is_valid(r, c, d):
                grid[r][c] = d
                if _backtrack(pos + 1):
                    return True
                grid[r][c] = 0
        return False

    _backtrack(0)
    return grid


# ─────────────────────────────────────────────────────────────────────────────
# Unique-Solution Check
# ─────────────────────────────────────────────────────────────────────────────

# Precomputed peer indices for each cell (flat index 0-80)
_PEERS: list[list[int]] = []
def _build_peers() -> None:
    for i in range(81):
        r, c = divmod(i, 9)
        ps: set[int] = set()
        ps.update(r * 9 + cc for cc in range(9))
        ps.update(rr * 9 + c for rr in range(9))
        br, bc = (r // 3) * 3, (c // 3) * 3
        ps.update((br + dr) * 9 + (bc + dc) for dr in range(3) for dc in range(3))
        ps.discard(i)
        _PEERS.append(sorted(ps))
_build_peers()

_ALL_BITS = (1 << 9) - 1  # bits 0-8 = digits 1-9


def _has_unique_solution(grid: list[list[int]]) -> bool:
    """Return True iff the puzzle has exactly one solution.

    Uses constraint propagation (naked-single chain elimination) + MRV
    branching.  Works on a flat 81-element bitset array for cache efficiency.
    Each bit i in cands[pos] represents digit (i+1) being possible.
    """
    # All cells start with all 9 digits possible
    cands = [_ALL_BITS] * 81
    count = [0]

    def _eliminate(state: list[int], pos: int, bit: int) -> bool:
        """Remove digit (bit) from cell pos, chaining naked-single propagation."""
        if not (state[pos] & bit):
            return True  # already gone
        state[pos] ^= bit
        n = bin(state[pos]).count('1')
        if n == 0:
            return False  # contradiction
        if n == 1:
            # Naked single — eliminate this digit from all peers
            only = state[pos]
            for peer in _PEERS[pos]:
                if not _eliminate(state, peer, only):
                    return False
        return True

    def _assign(state: list[int], pos: int, bit: int) -> bool:
        """Fix pos to digit (bit) by eliminating all other candidates."""
        other = state[pos] & ~bit
        b = other
        while b:
            lsb = b & -b
            b &= b - 1
            if not _eliminate(state, pos, lsb):
                return False
        return True

    def _solve(state: list[int]) -> bool:
        # MRV: find unfixed cell with fewest candidates
        best_pos = -1
        best_n = 10
        for i in range(81):
            n = bin(state[i]).count('1')
            if n > 1 and n < best_n:
                best_pos, best_n = i, n
                if n == 2:
                    break
        if best_pos == -1:
            count[0] += 1
            return count[0] >= 2

        b = state[best_pos]
        while b:
            lsb = b & -b
            b &= b - 1
            snap = state[:]
            if _assign(snap, best_pos, lsb) and _solve(snap):
                return True
        return False

    # Assign all given digits, propagating constraints
    for pos in range(81):
        r, c = divmod(pos, 9)
        d = grid[r][c]
        if d:
            if not _assign(cands, pos, 1 << (d - 1)):
                return False  # invalid puzzle

    _solve(cands)
    return count[0] == 1


# ─────────────────────────────────────────────────────────────────────────────
# Difficulty Rater
# ─────────────────────────────────────────────────────────────────────────────

def _rate_difficulty(values: list[list[int]]) -> int:
    """Rate puzzle difficulty by simulating human-strategy solving.

    Applies ALL_STRATEGIES in order (hardest tried last only when easier ones
    are exhausted) until the puzzle is solved or no strategy fires.

    Returns
    -------
    int
        The highest tier of any strategy used, 1–4.
        Returns 0 if the puzzle cannot be solved by the implemented strategies
        (i.e. it requires bifurcation / trial-and-error).
    """
    grid = Grid(values)
    max_tier = 0

    while not grid.is_solved():
        found = False
        for name, fn in ALL_STRATEGIES:
            step = fn(grid)
            if step is not None:
                tier = STRATEGY_TIER.get(step.strategy, STRATEGY_TIER.get(name, 0))
                if tier > max_tier:
                    max_tier = tier
                grid.apply_step(step)
                found = True
                break  # restart strategy loop from the easiest strategy
        if not found:
            return 0  # stuck — unsolvable by human strategies

    return max_tier


def _is_tier0(values: list[list[int]]) -> bool:
    """Return True iff the puzzle is solvable using only Full House and Naked Single.

    These are the two simplest strategies: a cell either is the last empty in
    its house (Full House) or has exactly one remaining candidate (Naked Single).
    No candidate-elimination reasoning is required.
    """
    grid = Grid(values)
    tier0_fns = [(name, fn) for name, fn in ALL_STRATEGIES
                 if name in _TIER0_STRATEGY_NAMES]
    while not grid.is_solved():
        found = False
        for name, fn in tier0_fns:
            step = fn(grid)
            if step is not None:
                grid.apply_step(step)
                found = True
                break
        if not found:
            return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Puzzle Generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_puzzle(
    target_tier: int = 2,
    max_attempts: int = 200,
    seed: int | None = None,
    time_limit_s: float = 12.0,
) -> Optional[list[list[int]]]:
    """Generate a Sudoku puzzle at the requested difficulty tier.

    Algorithm
    ---------
    1. Generate a complete, random solution.
    2. Collect all 81 cells in a random order.
    3. Remove cells one by one; after each removal verify that the puzzle
       still has a unique solution.  Skip cells whose removal would create
       multiple solutions.
    4. Stop the removal loop when either:
         a. Every cell has been visited, or
         b. The number of empty cells reaches the upper bound for the tier.
    5. Rate the resulting puzzle.  Accept it when the rated tier is within
       ±1 of the target, or when target_tier >= 4 and the puzzle needs brute
       force (rated 0).
    6. Retry until *max_attempts* exhausted or *time_limit_s* elapsed.
       Returns the closest-match puzzle found so far if time runs out.

    Parameters
    ----------
    target_tier:
        Desired difficulty, 0–4.  Tier 0 produces really-easy puzzles
        solvable by Full House and Naked Single alone.
    max_attempts:
        Maximum number of generation attempts.
    seed:
        Optional RNG seed.  Each attempt uses a derived seed so results are
        reproducible while still varying across attempts.
    time_limit_s:
        Wall-clock seconds before the function returns whatever best candidate
        it has found so far (or None if nothing viable was produced).

    Returns
    -------
    A 9×9 list of ints (0 = empty cell), or None if generation failed.
    """
    rng = random.Random(seed)
    empty_min, empty_max = _EMPTY_RANGE.get(target_tier, (45, 55))
    deadline = time.monotonic() + time_limit_s
    best_candidate: Optional[list[list[int]]] = None
    best_distance = 999

    for attempt in range(max_attempts):
        if time.monotonic() >= deadline:
            break

        # Derive a per-attempt seed so each attempt explores a different space
        attempt_seed = rng.randint(0, 2**31 - 1)
        solution = generate_solution(seed=attempt_seed)

        # Start with the full solution; we will punch holes in it
        puzzle = [row[:] for row in solution]

        # Random cell removal order
        attempt_rng = random.Random(attempt_seed)
        cells = list(range(81))
        attempt_rng.shuffle(cells)

        empty_count = 0
        for pos in cells:
            if time.monotonic() >= deadline:
                break
            r, c = divmod(pos, 9)
            saved = puzzle[r][c]
            puzzle[r][c] = 0

            if _has_unique_solution(puzzle):
                empty_count += 1
                if empty_count >= empty_max:
                    break  # hit the upper bound for this tier
            else:
                # Restore — removing this cell breaks uniqueness
                puzzle[r][c] = saved

        # Only proceed if we have at least the minimum number of empty cells
        if empty_count < empty_min:
            continue

        # Rate the puzzle
        if target_tier == 0:
            acceptable = _is_tier0(puzzle)
            tier = 0 if acceptable else 1
        else:
            tier = _rate_difficulty(puzzle)
            # Accept criteria:
            #   - Exact tier match, or within ±1
            #   - For tier-4 target: also accept unsolvable-by-strategies (tier==0)
            acceptable = (
                abs(tier - target_tier) <= 1
                or (target_tier >= 4 and tier == 0)
            )

        if acceptable:
            return puzzle

        # Keep the closest-rated candidate in case we hit the time limit
        distance = abs(tier - target_tier)
        if distance < best_distance:
            best_distance = distance
            best_candidate = [row[:] for row in puzzle]

    # Time/attempts exhausted — return best candidate found (may be off by a tier)
    return best_candidate


# ─────────────────────────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    tier = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"Generating tier-{tier} puzzle (seed={seed}) …")
    puzzle = generate_puzzle(target_tier=tier, max_attempts=100, seed=seed)

    if puzzle is None:
        print("Failed to generate a puzzle within 100 attempts.")
        sys.exit(1)

    empty = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] == 0)
    if tier == 0:
        rated_str = "0 (Really Easy)" if _is_tier0(puzzle) else "1+ (not pure tier-0)"
    else:
        rated = _rate_difficulty(puzzle)
        rated_str = str(rated)
    print(f"  Empty cells : {empty}")
    print(f"  Rated tier  : {rated_str}")
    print()
    for row in puzzle:
        print(" ".join(str(d) if d else "." for d in row))
