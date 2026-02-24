#!/usr/bin/env python3
"""
sudoku_gui.py — Pygame GUI for the Sudoku Tutor

Provides a windowed interface for sudoku_tutor.py with:
  • 9×9 grid with candidate (pencilmark) display
  • Step-by-step navigation with strategy highlighting
  • Puzzle input mode with live conflict detection
  • Auto-play mode

Usage:
    python sudoku_gui.py [puzzle_file]

Keys (solve mode):
    SPACE / RIGHT    — next step
    LEFT / BACKSPACE — previous step
    A                — toggle auto-play
    C                — toggle candidate display
    R                — reset to step 0
    I                — enter input mode
    ESC              — quit

Keys (input mode):
    1–9              — set digit
    0 / DEL          — clear cell
    Arrow keys       — move selection
    X                — clear all cells
    ENTER            — solve the entered puzzle
    ESC              — cancel / return to solve mode
"""

import sys
from copy import deepcopy

import pygame

from sudoku_tutor import (
    Grid, Step, ALL_STRATEGIES, DEFAULT_PUZZLE, read_puzzle,
)

# ─────────────────────────────────────────────────────────────────────────────
# Layout constants
# ─────────────────────────────────────────────────────────────────────────────

MARGIN    = 16
CELL_SIZE = 64
GRID_PX   = 576          # 9 × 64
PANEL_W   = 320
BTN_H     = 38

GRID_X  = MARGIN                          # 16
GRID_Y  = MARGIN                          # 16
PANEL_X = GRID_X + GRID_PX + MARGIN       # 608
BTN_Y   = GRID_Y + GRID_PX + MARGIN       # 608

WIN_W = PANEL_X + PANEL_W + MARGIN        # 944
WIN_H = BTN_Y + BTN_H + MARGIN            # 662

SUBCELL_W = CELL_SIZE // 3                # 21
SUBCELL_H = CELL_SIZE // 3                # 21

# ─────────────────────────────────────────────────────────────────────────────
# Colours
# ─────────────────────────────────────────────────────────────────────────────

C_BG           = (240, 240, 235)
C_GIVEN_BG     = (215, 228, 248)
C_GIVEN_FG     = ( 10,  40, 120)
C_SOLVED_FG    = ( 30,  30,  30)
C_CAND_FG      = (120, 120, 120)
C_ELIM_CAND    = (220,  60,  60)
C_PLACE_BG     = (160, 240, 160)
C_ELIM_BG      = (255, 220, 180)
C_HOUSE_BG     = (255, 252, 200)
C_SELECTED     = (190, 220, 255)
C_CONFLICT_BG  = (255, 155, 155)   # cell involved in a rule violation
C_GRID_THIN    = ( 80,  80,  80)
C_GRID_THICK   = ( 20,  20,  20)
C_PANEL_BG     = (255, 255, 255)
C_PANEL_LINE   = (200, 200, 200)
C_BTN          = ( 70, 130, 180)
C_BTN_HOVER    = (100, 160, 210)
C_BTN_ON       = ( 60, 150,  60)
C_BTN_ON_HOV   = ( 80, 180,  80)
C_BTN_DANGER   = (180,  60,  60)
C_BTN_DANGER_H = (210,  80,  80)
C_BTN_TEXT     = (255, 255, 255)
C_WARN         = (200,  60,  60)
C_OK           = (  0, 140,  60)
C_ACCENT       = (180,  80,   0)
C_BRUTE_FG     = (120,  50, 180)   # purple — brute-forced digits

# ─────────────────────────────────────────────────────────────────────────────
# Strategy → tier mapping
# ─────────────────────────────────────────────────────────────────────────────

STRATEGY_TIER: dict[str, int] = {
    "Full House":         1,
    "Naked Single":       1,
    "Hidden Single":      1,
    "Naked Pair":         2,
    "Hidden Pair":        2,
    "Naked Triple":       2,
    "Hidden Triple":      2,
    "Naked Quad":         2,
    "Hidden Quad":        2,
    "Pointing Pairs":     2,
    "Box-Line Reduction": 2,
    "X-Wing":             3,
    "Swordfish":          3,
    "Y-Wing":             3,
    "XYZ-Wing":           3,
    "Simple Coloring":    3,
}

# ─────────────────────────────────────────────────────────────────────────────
# Button bar definition
# ─────────────────────────────────────────────────────────────────────────────

BUTTONS = [
    {"id": "prev",  "label": "< PREV"},
    {"id": "next",  "label": "NEXT >"},
    {"id": "auto",  "label": "> AUTO",  "toggle": True},
    {"id": "reset", "label": "RESET"},
    {"id": "cands", "label": "CANDS",   "toggle": True},
    {"id": "input", "label": "INPUT",   "toggle": True},
    {"id": "clear", "label": "CLEAR",   "danger": True},
    {"id": "save",  "label": "SAVE"},
    {"id": "load",  "label": "LOAD"},
]


# ─────────────────────────────────────────────────────────────────────────────
# Brute-force backtracking solver
# ─────────────────────────────────────────────────────────────────────────────

def _bt_candidates(grid: list[list[int]], r: int, c: int) -> set[int]:
    used: set[int] = set()
    for cc in range(9): used.add(grid[r][cc])
    for rr in range(9): used.add(grid[rr][c])
    br, bc = (r // 3) * 3, (c // 3) * 3
    for dr in range(3):
        for dc in range(3):
            used.add(grid[br + dr][bc + dc])
    return set(range(1, 10)) - used


def _bt_solve(grid: list[list[int]]) -> list[list[int]] | None:
    """Backtracking solver with MRV heuristic. Returns solved grid or None."""
    best_r, best_c, best_cands = -1, -1, None
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                cands = _bt_candidates(grid, r, c)
                if not cands:
                    return None   # dead end
                if best_cands is None or len(cands) < len(best_cands):
                    best_r, best_c, best_cands = r, c, cands
                    if len(best_cands) == 1:
                        break
        if best_cands and len(best_cands) == 1:
            break
    if best_r == -1:
        return grid   # all cells filled → solved
    for d in sorted(best_cands):   # type: ignore[arg-type]
        grid[best_r][best_c] = d
        result = _bt_solve([row[:] for row in grid])
        if result is not None:
            return result
        grid[best_r][best_c] = 0
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Board validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_board(values: list[list[int]]) -> set[tuple[int, int]]:
    """
    Return the set of cells that violate Sudoku rules (duplicate digit in a
    row, column, or box).  An empty set means the board is consistent.
    """
    conflicts: set[tuple[int, int]] = set()

    # Rows
    for r in range(9):
        seen: dict[int, int] = {}
        for c in range(9):
            v = values[r][c]
            if v:
                if v in seen:
                    conflicts.add((r, c))
                    conflicts.add((r, seen[v]))
                else:
                    seen[v] = c

    # Columns
    for c in range(9):
        seen = {}
        for r in range(9):
            v = values[r][c]
            if v:
                if v in seen:
                    conflicts.add((r, c))
                    conflicts.add((seen[v], c))
                else:
                    seen[v] = r

    # Boxes
    for box in range(9):
        seen_cell: dict[int, tuple[int, int]] = {}
        for r, c in Grid.cells_of_box(box):
            v = values[r][c]
            if v:
                if v in seen_cell:
                    conflicts.add((r, c))
                    conflicts.add(seen_cell[v])
                else:
                    seen_cell[v] = (r, c)

    return conflicts


# ─────────────────────────────────────────────────────────────────────────────
# Font loader
# ─────────────────────────────────────────────────────────────────────────────

def _load_fonts() -> dict:
    """Try common monospace fonts, fall back to pygame default."""
    mono_names = ["menlo", "couriernew", "andalemono", "dejavusansmono", "monospace"]
    mono = None
    for name in mono_names:
        f = pygame.font.match_font(name)
        if f:
            mono = f
            break

    def make(size, bold=False):
        if mono:
            return pygame.font.Font(mono, size)
        return pygame.font.Font(None, size + 6)

    return {
        "digit":       make(34, bold=True),
        "cand":        make(13),
        "panel_title": make(18, bold=True),
        "panel_body":  make(13),
        "btn":         make(14, bold=True),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main application
# ─────────────────────────────────────────────────────────────────────────────

class SudokuApp:
    """Pygame Sudoku tutor GUI."""

    def __init__(self, puzzle_file: str | None = None):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Sudoku Tutor")
        self.clock = pygame.time.Clock()
        self.fonts = _load_fonts()

        # ── Solver state ──────────────────────────────────────────────────────
        self.initial_values: list[list[int]] = []
        self.grid_states:    list[Grid]      = []   # len = len(steps) + 1
        self.steps:          list[Step]      = []
        self.step_idx:       int             = 0
        self.highlight:      dict            = {}   # (r,c) → "place"/"elim"/"house"
        self.elim_set:       set             = set()
        self.conflict_cells: set             = set()   # (r,c) pairs with rule violations
        self.show_candidates: bool           = True
        self.auto_play:      bool            = False
        self.auto_interval:  int             = 1000
        self.auto_timer:     int             = 0
        self.stuck:          bool            = False
        self.brute_force_grid: list[list[int]] | None = None   # set after brute force

        # ── UI state ──────────────────────────────────────────────────────────
        self.mode:         str              = "solve"
        self.input_values: list[list[int]] | None = None
        self.selected:     tuple | None    = None

        self.btn_rects: dict = {}
        self._compute_btn_rects()

        if puzzle_file:
            vals = read_puzzle(puzzle_file)
            if vals:
                print(f"Loaded: {puzzle_file}")
                self.load_puzzle(vals)
            else:
                print(f"Could not read '{puzzle_file}', using default puzzle.")
                self.load_puzzle(DEFAULT_PUZZLE)
        else:
            vals = read_puzzle("sd0.txt")
            if vals:
                print("Loaded: sd0.txt")
                self.load_puzzle(vals)
            else:
                print("Using built-in default puzzle.")
                self.load_puzzle(DEFAULT_PUZZLE)

    # ──────────────────────────────────────────────────────────────────────────
    # Layout helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _compute_btn_rects(self):
        n = len(BUTTONS)
        available = WIN_W - 2 * MARGIN
        gap = 4
        btn_w = (available - gap * (n - 1)) // n
        x = MARGIN
        for btn in BUTTONS:
            self.btn_rects[btn["id"]] = pygame.Rect(x, BTN_Y, btn_w, BTN_H)
            x += btn_w + gap

    def _cell_rect(self, r: int, c: int) -> pygame.Rect:
        return pygame.Rect(
            GRID_X + c * CELL_SIZE,
            GRID_Y + r * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Puzzle loading & step computation
    # ──────────────────────────────────────────────────────────────────────────

    def load_puzzle(self, values: list[list[int]]):
        self.initial_values = [row[:] for row in values]
        self.compute_all_steps()
        self.go_to_step(0)

    def compute_all_steps(self):
        """Compute all solution steps.  Validates the board before and after
        every step; stops with stuck=True on any rule violation."""
        self.steps = []
        self.stuck = False

        # ── Validate initial puzzle ───────────────────────────────────────────
        init_conflicts = validate_board(self.initial_values)
        if init_conflicts:
            self.conflict_cells = init_conflicts
            self.grid_states = [Grid(self.initial_values)]
            self.stuck = True
            n = len(init_conflicts)
            print(f"Invalid puzzle: {n} cell(s) violate Sudoku rules. "
                  "Correct them before solving.")
            return

        self.conflict_cells = set()
        self.brute_force_grid = None
        grid = Grid(self.initial_values)
        self.grid_states = [deepcopy(grid)]

        while not grid.is_solved():
            step = None
            for _, fn in ALL_STRATEGIES:
                step = fn(grid)
                if step:
                    break
            if step is None:
                self.stuck = True
                break

            self.steps.append(step)
            grid.apply_step(step)

            # ── Consistency check after every step ───────────────────────────
            conflicts = validate_board(grid.values)
            if conflicts:
                self.conflict_cells = conflicts
                self.grid_states.append(deepcopy(grid))
                self.stuck = True
                print(f"Inconsistency introduced at step {len(self.steps)}: "
                      f"{len(conflicts)} conflicting cell(s). "
                      "The initial puzzle may have multiple solutions or be unsolvable.")
                break

            self.grid_states.append(deepcopy(grid))

        msg = "STUCK — no further strategy found." if self.stuck else "Solved!"
        print(f"Computed {len(self.steps)} steps. {msg}")

    # ──────────────────────────────────────────────────────────────────────────
    # Navigation
    # ──────────────────────────────────────────────────────────────────────────

    def go_to_step(self, idx: int):
        self.brute_force_grid = None   # any navigation clears brute-force view
        self.step_idx = max(0, min(idx, len(self.steps)))
        if self.step_idx > 0:
            step = self.steps[self.step_idx - 1]
            self.highlight = self._build_highlight(step)
            self.elim_set  = {(r, c, d) for r, c, d in step.eliminations}
        else:
            self.highlight = {}
            self.elim_set  = set()
        # Re-check consistency for the now-displayed grid state
        self.conflict_cells = validate_board(
            self.grid_states[self.step_idx].values)

    def _build_highlight(self, step: Step) -> dict:
        h: dict = {}
        if step.house_type and step.house_index >= 0:
            if step.house_type == "row":
                cells = [(step.house_index, c) for c in range(9)]
            elif step.house_type == "col":
                cells = [(r, step.house_index) for r in range(9)]
            else:
                cells = Grid.cells_of_box(step.house_index)
            for rc in cells:
                h[rc] = "house"
        for r, c, _d in step.eliminations:
            if h.get((r, c)) in (None, "house"):
                h[(r, c)] = "elim"
        for r, c, _d in step.placements:
            h[(r, c)] = "place"
        return h

    # ──────────────────────────────────────────────────────────────────────────
    # Drawing
    # ──────────────────────────────────────────────────────────────────────────

    def draw(self):
        self.screen.fill(C_BG)
        self.draw_grid()
        self.draw_panel()
        self.draw_buttons()
        pygame.display.flip()

    # ── Grid & cells ──────────────────────────────────────────────────────────

    def draw_grid(self):
        for r in range(9):
            for c in range(9):
                self.draw_cell(r, c)
        for i in range(10):
            thick = (i % 3 == 0)
            color = C_GRID_THICK if thick else C_GRID_THIN
            width = 2 if thick else 1
            y = GRID_Y + i * CELL_SIZE
            pygame.draw.line(self.screen, color,
                             (GRID_X, y), (GRID_X + GRID_PX, y), width)
            x = GRID_X + i * CELL_SIZE
            pygame.draw.line(self.screen, color,
                             (x, GRID_Y), (x, GRID_Y + GRID_PX), width)

    def draw_cell(self, r: int, c: int):
        rect = self._cell_rect(r, c)

        # ── Brute-force view (no highlights, no candidates) ───────────────────
        if self.brute_force_grid is not None and self.mode == "solve":
            last = self.grid_states[-1]
            bf_v = self.brute_force_grid[r][c]
            bg = C_GIVEN_BG if last.givens[r][c] else C_BG
            pygame.draw.rect(self.screen, bg, rect)
            if bf_v:
                # given = dark blue, strategy-solved = black, brute-forced = purple
                if last.givens[r][c]:
                    color = C_GIVEN_FG
                elif last.values[r][c] != 0:
                    color = C_SOLVED_FG
                else:
                    color = C_BRUTE_FG
                surf = self.fonts["digit"].render(str(bf_v), True, color)
                self.screen.blit(surf, surf.get_rect(center=rect.center))
            return

        # ── Background ────────────────────────────────────────────────────────
        if self.mode == "input":
            # Conflict overrides everything (live feedback while typing)
            if (r, c) in self.conflict_cells:
                bg = C_CONFLICT_BG
            elif self.selected == (r, c):
                bg = C_SELECTED
            elif self.input_values[r][c] != 0:   # type: ignore[index]
                bg = C_GIVEN_BG
            else:
                bg = C_BG
        else:
            grid = self.grid_states[self.step_idx]
            # Conflict overrides step highlights so errors are always visible
            if (r, c) in self.conflict_cells:
                bg = C_CONFLICT_BG
            else:
                tag = self.highlight.get((r, c))
                if tag == "place":
                    bg = C_PLACE_BG
                elif tag == "elim":
                    bg = C_ELIM_BG
                elif tag == "house":
                    bg = C_HOUSE_BG
                elif self.selected == (r, c):
                    bg = C_SELECTED
                elif grid.givens[r][c]:
                    bg = C_GIVEN_BG
                else:
                    bg = C_BG

        pygame.draw.rect(self.screen, bg, rect)

        # ── Content ───────────────────────────────────────────────────────────
        if self.mode == "input":
            v = self.input_values[r][c]   # type: ignore[index]
            if v != 0:
                surf = self.fonts["digit"].render(str(v), True, C_GIVEN_FG)
                self.screen.blit(surf, surf.get_rect(center=rect.center))
        else:
            grid = self.grid_states[self.step_idx]
            v = grid.values[r][c]
            if v != 0:
                color = C_GIVEN_FG if grid.givens[r][c] else C_SOLVED_FG
                surf = self.fonts["digit"].render(str(v), True, color)
                self.screen.blit(surf, surf.get_rect(center=rect.center))
            elif self.show_candidates:
                self.draw_candidates(r, c, rect)

    def draw_candidates(self, r: int, c: int, cell_rect: pygame.Rect):
        grid = self.grid_states[self.step_idx]
        current_cands = grid.candidates[r][c]
        prev_cands: set = set()
        if self.step_idx > 0:
            prev_cands = self.grid_states[self.step_idx - 1].candidates[r][c]

        for d in range(1, 10):
            dr = (d - 1) // 3
            dc = (d - 1) % 3
            cx = cell_rect.x + dc * SUBCELL_W + SUBCELL_W // 2
            cy = cell_rect.y + dr * SUBCELL_H + SUBCELL_H // 2

            in_current  = d in current_cands
            was_in_prev = d in prev_cands
            is_elim     = (r, c, d) in self.elim_set

            if in_current:
                surf = self.fonts["cand"].render(str(d), True, C_CAND_FG)
                self.screen.blit(surf, surf.get_rect(centerx=cx, centery=cy))
            elif is_elim and was_in_prev:
                surf = self.fonts["cand"].render(str(d), True, C_ELIM_CAND)
                self.screen.blit(surf, surf.get_rect(centerx=cx, centery=cy))

    # ── Info panel ────────────────────────────────────────────────────────────

    def draw_panel(self):
        panel_rect = pygame.Rect(PANEL_X, GRID_Y, PANEL_W, GRID_PX)
        pygame.draw.rect(self.screen, C_PANEL_BG, panel_rect)
        pygame.draw.rect(self.screen, C_GRID_THIN, panel_rect, 1)

        x = PANEL_X + 10
        y = GRID_Y + 10
        max_w = PANEL_W - 20

        surf = self.fonts["panel_title"].render("SUDOKU TUTOR", True, C_GIVEN_FG)
        self.screen.blit(surf, (x, y))
        y += surf.get_height() + 6
        pygame.draw.line(self.screen, C_PANEL_LINE,
                         (PANEL_X + 6, y), (PANEL_X + PANEL_W - 6, y), 1)
        y += 8

        if self.mode == "input":
            self._draw_panel_input_mode(x, y, max_w)
            return

        # ── Brute-force result panel ──────────────────────────────────────────
        if self.brute_force_grid is not None:
            surf = self.fonts["panel_title"].render("BRUTE FORCE", True, C_BRUTE_FG)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 6
            for line in (
                "Puzzle solved by backtracking.",
                "",
                "Purple digits were filled by",
                "the brute-force algorithm.",
                "",
                "No step-by-step explanation",
                "is available for these cells.",
                "",
                "Press PREV to go back to the",
                "last human-strategy step.",
            ):
                if not line:
                    y += 4
                    continue
                surf = self.fonts["panel_body"].render(line, True, C_SOLVED_FG)
                self.screen.blit(surf, (x, y))
                y += surf.get_height() + 2
            return

        total = len(self.steps)
        surf = self.fonts["panel_body"].render(
            f"Step {self.step_idx} / {total}", True, C_SOLVED_FG)
        self.screen.blit(surf, (x, y))
        y += surf.get_height() + 6

        # Show board conflict error (invalid initial puzzle or solver bug)
        if self.conflict_cells:
            n = len(self.conflict_cells)
            surf = self.fonts["panel_body"].render(
                f"CONFLICT: {n} cell(s) violate rules!", True, C_WARN)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 4
            if self.step_idx == 0:
                surf = self.fonts["panel_body"].render(
                    "Fix the puzzle in INPUT mode.", True, C_CAND_FG)
                self.screen.blit(surf, (x, y))
            return

        if self.step_idx == 0:
            if self.stuck:
                # Stuck immediately — no human strategy applied at all
                surf = self.fonts["panel_body"].render(
                    "STUCK! No strategy found.", True, C_WARN)
                self.screen.blit(surf, (x, y))
                y += surf.get_height() + 6
                surf = self.fonts["panel_body"].render(
                    "Press NEXT to try brute force.", True, C_CAND_FG)
                self.screen.blit(surf, (x, y))
            else:
                for line in ("Initial puzzle.", "", "SPACE / NEXT to advance.",
                             "C = toggle candidates"):
                    if not line:
                        y += 4
                        continue
                    surf = self.fonts["panel_body"].render(line, True, C_CAND_FG)
                    self.screen.blit(surf, (x, y))
                    y += surf.get_height() + 2
            return

        step = self.steps[self.step_idx - 1]

        if self.stuck and self.step_idx == total:
            surf = self.fonts["panel_body"].render(
                "STUCK! No strategy found.", True, C_WARN)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 2
            surf = self.fonts["panel_body"].render(
                "Press NEXT to try brute force.", True, C_CAND_FG)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 6

        surf = self.fonts["panel_title"].render(step.strategy, True, (60, 100, 180))
        self.screen.blit(surf, (x, y))
        y += surf.get_height() + 2

        tier = STRATEGY_TIER.get(step.strategy, "?")
        surf = self.fonts["panel_body"].render(f"Tier {tier}", True, C_CAND_FG)
        self.screen.blit(surf, (x, y))
        y += surf.get_height() + 8

        if step.placements:
            surf = self.fonts["panel_body"].render("Placed:", True, (0, 140, 0))
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 2
            for r, c, d in step.placements:
                surf = self.fonts["panel_body"].render(
                    f"  R{r+1}C{c+1} = {d}", True, C_SOLVED_FG)
                self.screen.blit(surf, (x, y))
                y += surf.get_height() + 1

        if step.eliminations:
            y += 4
            surf = self.fonts["panel_body"].render("Eliminated:", True, C_ACCENT)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 2
            by_cell: dict = {}
            for r, c, d in step.eliminations:
                by_cell.setdefault((r, c), []).append(d)
            items = list(by_cell.items())
            for (r, c), ds in items[:6]:
                txt = f"  R{r+1}C{c+1}: {{{','.join(str(d) for d in sorted(ds))}}}"
                surf = self.fonts["panel_body"].render(txt, True, C_SOLVED_FG)
                self.screen.blit(surf, (x, y))
                y += surf.get_height() + 1
            if len(items) > 6:
                surf = self.fonts["panel_body"].render(
                    f"  …+{len(items)-6} more", True, C_CAND_FG)
                self.screen.blit(surf, (x, y))
                y += surf.get_height() + 1

        y += 8
        pygame.draw.line(self.screen, C_PANEL_LINE,
                         (PANEL_X + 6, y), (PANEL_X + PANEL_W - 6, y), 1)
        y += 6
        self._draw_text_wrapped(step.explanation, x, y, max_w,
                                self.fonts["panel_body"], C_SOLVED_FG)

    def _draw_panel_input_mode(self, x: int, y: int, max_w: int):
        surf = self.fonts["panel_body"].render("INPUT MODE", True, C_ACCENT)
        self.screen.blit(surf, (x, y))
        y += surf.get_height() + 6

        # Live validity indicator
        if self.conflict_cells:
            n = len(self.conflict_cells)
            msg = f"  {n} conflict(s) — fix before solving"
            surf = self.fonts["panel_body"].render(msg, True, C_WARN)
        else:
            surf = self.fonts["panel_body"].render("  Board is valid", True, C_OK)
        self.screen.blit(surf, (x, y))
        y += surf.get_height() + 10

        pygame.draw.line(self.screen, C_PANEL_LINE,
                         (PANEL_X + 6, y), (PANEL_X + PANEL_W - 6, y), 1)
        y += 8

        for text, color in [
            ("1–9   set digit",        C_SOLVED_FG),
            ("0 / Del   clear cell",   C_SOLVED_FG),
            ("Arrows   move",          C_SOLVED_FG),
            ("X   clear all cells",    C_SOLVED_FG),
            ("Enter   solve",          C_SOLVED_FG),
            ("ESC   cancel",           C_SOLVED_FG),
        ]:
            surf = self.fonts["panel_body"].render(text, True, color)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 3

    def _draw_text_wrapped(self, text: str, x: int, y: int,
                           max_w: int, font, color) -> int:
        words = text.split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if font.size(test)[0] <= max_w:
                line = test
            else:
                if line:
                    surf = font.render(line, True, color)
                    self.screen.blit(surf, (x, y))
                    y += surf.get_height() + 1
                line = word
        if line:
            surf = font.render(line, True, color)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 1
        return y

    # ── Button bar ────────────────────────────────────────────────────────────

    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        for btn in BUTTONS:
            bid   = btn["id"]
            rect  = self.btn_rects[bid]
            hover = rect.collidepoint(mouse_pos)

            is_on = (bid == "auto"  and self.auto_play) or \
                    (bid == "cands" and self.show_candidates) or \
                    (bid == "input" and self.mode == "input")
            is_danger = btn.get("danger", False)

            if is_on:
                bg = C_BTN_ON_HOV if hover else C_BTN_ON
            elif is_danger:
                bg = C_BTN_DANGER_H if hover else C_BTN_DANGER
            else:
                bg = C_BTN_HOVER if hover else C_BTN

            pygame.draw.rect(self.screen, bg, rect, border_radius=5)
            surf = self.fonts["btn"].render(btn["label"], True, C_BTN_TEXT)
            self.screen.blit(surf, surf.get_rect(center=rect.center))

    # ──────────────────────────────────────────────────────────────────────────
    # Event handling
    # ──────────────────────────────────────────────────────────────────────────

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if not self.handle_key(event):
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
        return True

    def handle_key(self, event) -> bool:
        if self.mode == "solve":
            if event.key in (pygame.K_RIGHT, pygame.K_SPACE):
                if (self.stuck and self.step_idx == len(self.steps)
                        and self.brute_force_grid is None):
                    self._offer_brute_force()
                else:
                    self.go_to_step(self.step_idx + 1)
            elif event.key in (pygame.K_LEFT, pygame.K_BACKSPACE):
                self.go_to_step(self.step_idx - 1)
            elif event.key == pygame.K_a:
                self.auto_play = not self.auto_play
                self.auto_timer = 0
            elif event.key == pygame.K_c:
                self.show_candidates = not self.show_candidates
            elif event.key == pygame.K_r:
                self.auto_play = False
                self.go_to_step(0)
            elif event.key == pygame.K_i:
                self.enter_input_mode()
            elif event.key == pygame.K_ESCAPE:
                return False

        elif self.mode == "input":
            if event.key == pygame.K_ESCAPE:
                self.exit_input_mode(solve=False)
            elif event.key == pygame.K_RETURN:
                self.exit_input_mode(solve=True)
            elif event.key == pygame.K_x:
                self._clear_all_input()
            elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                if self.selected:
                    r, c = self.selected
                    self.input_values[r][c] = 0     # type: ignore[index]
                    self._update_input_conflicts()
            elif event.unicode in ("0",):
                if self.selected:
                    r, c = self.selected
                    self.input_values[r][c] = 0     # type: ignore[index]
                    self._update_input_conflicts()
            elif event.unicode.isdigit() and event.unicode != "0":
                if self.selected:
                    r, c = self.selected
                    self.input_values[r][c] = int(event.unicode)  # type: ignore[index]
                    self._update_input_conflicts()
                    # Auto-advance selection
                    nc = c + 1
                    nr = r
                    if nc > 8:
                        nc = 0
                        nr = min(r + 1, 8)
                    self.selected = (nr, nc)
            elif event.key == pygame.K_UP:
                if self.selected:
                    r, c = self.selected
                    self.selected = (max(0, r - 1), c)
            elif event.key == pygame.K_DOWN:
                if self.selected:
                    r, c = self.selected
                    self.selected = (min(8, r + 1), c)
            elif event.key == pygame.K_LEFT:
                if self.selected:
                    r, c = self.selected
                    self.selected = (r, max(0, c - 1))
            elif event.key == pygame.K_RIGHT:
                if self.selected:
                    r, c = self.selected
                    self.selected = (r, min(8, c + 1))

        return True

    def handle_click(self, pos: tuple):
        for btn in BUTTONS:
            if self.btn_rects[btn["id"]].collidepoint(pos):
                self._handle_button(btn["id"])
                return
        gx = pos[0] - GRID_X
        gy = pos[1] - GRID_Y
        if 0 <= gx < GRID_PX and 0 <= gy < GRID_PX:
            self.selected = (gy // CELL_SIZE, gx // CELL_SIZE)

    def _handle_button(self, bid: str):
        if bid == "prev":
            self.go_to_step(self.step_idx - 1)
        elif bid == "next":
            if (self.stuck and self.step_idx == len(self.steps)
                    and self.brute_force_grid is None):
                self._offer_brute_force()
            else:
                self.go_to_step(self.step_idx + 1)
        elif bid == "auto":
            self.auto_play = not self.auto_play
            self.auto_timer = 0
        elif bid == "reset":
            self.auto_play = False
            self.go_to_step(0)
        elif bid == "cands":
            self.show_candidates = not self.show_candidates
        elif bid == "input":
            if self.mode == "solve":
                self.enter_input_mode()
            else:
                self.exit_input_mode(solve=True)
        elif bid == "clear":
            if self.mode == "input":
                self._clear_all_input()
            else:
                self.enter_input_mode()
                self._clear_all_input()
        elif bid == "save":
            self._prompt_save_file()
        elif bid == "load":
            self._prompt_load_file()

    # ──────────────────────────────────────────────────────────────────────────
    # Input mode
    # ──────────────────────────────────────────────────────────────────────────

    def enter_input_mode(self):
        self.mode = "input"
        self.input_values = [row[:] for row in self.initial_values]
        self.selected = (0, 0)
        self.auto_play = False
        self._update_input_conflicts()

    def exit_input_mode(self, solve: bool = True):
        if solve and self.input_values is not None:
            if self.conflict_cells:
                # Don't accept an invalid puzzle
                print("Cannot solve: board has conflicts. "
                      "Fix the highlighted cells first.")
                return
            self.initial_values = [row[:] for row in self.input_values]
            self.mode = "solve"
            self.selected = None
            self.input_values = None
            self.compute_all_steps()
            self.go_to_step(0)
        else:
            self.mode = "solve"
            self.selected = None
            self.input_values = None
            # Restore conflict state from the current solve-mode grid
            self.conflict_cells = validate_board(
                self.grid_states[self.step_idx].values)

    def _clear_all_input(self):
        """Zero all cells in input mode."""
        if self.input_values is not None:
            self.input_values = [[0] * 9 for _ in range(9)]
            self.conflict_cells = set()

    def _update_input_conflicts(self):
        """Recompute conflicts from input_values (called after every edit)."""
        if self.input_values is not None:
            self.conflict_cells = validate_board(self.input_values)

    # ──────────────────────────────────────────────────────────────────────────
    # Brute-force offer
    # ──────────────────────────────────────────────────────────────────────────

    def _offer_brute_force(self):
        ok = self._confirm_dialog(
            "Solver is stuck",
            "No human strategy applies to the remaining cells.\n\n"
            "Run brute-force backtracking?\n"
            "A solution will be shown but with no step-by-step explanation.",
        )
        if ok:
            self._run_brute_force()

    def _run_brute_force(self):
        start = self.grid_states[-1].values
        result = _bt_solve([row[:] for row in start])
        if result is None:
            self._confirm_dialog("No solution", "This puzzle has no solution.")
        else:
            self.brute_force_grid = result

    def _confirm_dialog(self, title: str, message: str) -> bool:
        """
        Yes / No modal dialog.  Returns True on Yes / Enter, False on No / ESC.
        Snapshots the screen once so there is no background flicker.
        """
        DW, DH = 460, 160
        dx = (WIN_W - DW) // 2
        dy = (WIN_H - DH) // 2

        self.draw()
        background = self.screen.copy()
        dim = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 110))
        background.blit(dim, (0, 0))

        yes_rect = pygame.Rect(dx + DW - 94,  dy + DH - 40, 80, 28)
        no_rect  = pygame.Rect(dx + DW - 184, dy + DH - 40, 80, 28)

        while True:
            self.clock.tick(30)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_RETURN, pygame.K_y):
                        return True
                    elif ev.key in (pygame.K_ESCAPE, pygame.K_n):
                        return False
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if yes_rect.collidepoint(ev.pos):
                        return True
                    if no_rect.collidepoint(ev.pos):
                        return False

            self.screen.blit(background, (0, 0))
            box_rect = pygame.Rect(dx, dy, DW, DH)
            pygame.draw.rect(self.screen, C_PANEL_BG, box_rect, border_radius=6)
            pygame.draw.rect(self.screen, C_GRID_THICK, box_rect, 2, border_radius=6)

            surf = self.fonts["panel_title"].render(title, True, C_GIVEN_FG)
            self.screen.blit(surf, (dx + 14, dy + 10))

            self._draw_text_wrapped(message, dx + 14, dy + 38,
                                    DW - 28, self.fonts["panel_body"], C_SOLVED_FG)

            mouse = pygame.mouse.get_pos()
            for rect, label, base in (
                (yes_rect, "Yes", C_BTN_ON),
                (no_rect,  "No",  C_BTN),
            ):
                r, g, b = base
                bg = (min(r+20,255), min(g+20,255), min(b+20,255)) \
                     if rect.collidepoint(mouse) else base
                pygame.draw.rect(self.screen, bg, rect, border_radius=4)
                s = self.fonts["btn"].render(label, True, C_BTN_TEXT)
                self.screen.blit(s, s.get_rect(center=rect.center))

            pygame.display.flip()

    # ──────────────────────────────────────────────────────────────────────────
    # File I/O — in-GUI dialogs
    # ──────────────────────────────────────────────────────────────────────────

    def _text_dialog(self, title: str, default: str = "") -> str | None:
        """
        Modal text-input overlay rendered entirely inside the pygame window.
        Snapshots the current frame once so nothing underneath redraws (no flicker).
        Returns the trimmed string on Enter / OK, or None on ESC / Cancel.
        """
        DW, DH = 480, 130
        dx = (WIN_W - DW) // 2
        dy = (WIN_H - DH) // 2

        # Capture the current screen once — used as static background
        self.draw()
        background = self.screen.copy()
        dim = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 110))
        background.blit(dim, (0, 0))

        text = default
        cursor_on = True
        cursor_ms = 0

        ok_rect     = pygame.Rect(dx + DW - 92,  dy + DH - 40, 80, 28)
        cancel_rect = pygame.Rect(dx + DW - 182, dy + DH - 40, 80, 28)

        while True:
            dt = self.clock.tick(30)
            cursor_ms += dt
            if cursor_ms >= 500:
                cursor_ms = 0
                cursor_on = not cursor_on

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return None
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        return text.strip() or None
                    elif ev.key == pygame.K_ESCAPE:
                        return None
                    elif ev.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif ev.unicode and ev.unicode.isprintable():
                        text += ev.unicode
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if ok_rect.collidepoint(ev.pos):
                        return text.strip() or None
                    elif cancel_rect.collidepoint(ev.pos):
                        return None

            # Blit static background (no full redraw each frame)
            self.screen.blit(background, (0, 0))

            # Dialog box
            box_rect = pygame.Rect(dx, dy, DW, DH)
            pygame.draw.rect(self.screen, C_PANEL_BG, box_rect, border_radius=6)
            pygame.draw.rect(self.screen, C_GRID_THICK, box_rect, 2, border_radius=6)

            # Title
            surf = self.fonts["panel_title"].render(title, True, C_GIVEN_FG)
            self.screen.blit(surf, (dx + 14, dy + 10))

            # Text field
            field_rect = pygame.Rect(dx + 14, dy + 40, DW - 28, 30)
            pygame.draw.rect(self.screen, (255, 255, 255), field_rect)
            pygame.draw.rect(self.screen, C_GRID_THIN, field_rect, 1)

            font = self.fonts["panel_body"]
            display = text
            while display and font.size(display)[0] > field_rect.width - 10:
                display = display[1:]
            surf = font.render(display, True, C_SOLVED_FG)
            self.screen.blit(surf, (field_rect.x + 5, field_rect.y + 7))
            if cursor_on:
                cx = field_rect.x + 5 + font.size(display)[0]
                pygame.draw.line(self.screen, C_SOLVED_FG,
                                 (cx, field_rect.y + 5), (cx, field_rect.y + 25), 1)

            # Buttons
            mouse = pygame.mouse.get_pos()
            for rect, label in ((ok_rect, "OK"), (cancel_rect, "Cancel")):
                bg = C_BTN_HOVER if rect.collidepoint(mouse) else C_BTN
                pygame.draw.rect(self.screen, bg, rect, border_radius=4)
                s = self.fonts["btn"].render(label, True, C_BTN_TEXT)
                self.screen.blit(s, s.get_rect(center=rect.center))

            pygame.display.flip()

    @staticmethod
    def _ensure_txt(path: str) -> str:
        """Append .txt if the path has no file extension."""
        import os
        return path if os.path.splitext(path)[1] else path + ".txt"

    def _prompt_load_file(self):
        path = self._text_dialog("Load puzzle — enter file path:")
        if not path:
            return
        path = self._ensure_txt(path)
        vals = read_puzzle(path)
        if vals:
            if self.mode == "input":
                self.input_values = vals
                self._update_input_conflicts()
            else:
                self.load_puzzle(vals)
        else:
            self._text_dialog(f"Cannot read: {path}  (ESC to dismiss)")

    def _prompt_save_file(self):
        path = self._text_dialog("Save board — enter file path:", default="puzzle.txt")
        if not path:
            return
        path = self._ensure_txt(path)
        values = (self.input_values if self.mode == "input" and self.input_values
                  else self.grid_states[self.step_idx].values)
        try:
            with open(path, "w") as f:
                for row in values:
                    f.write("".join(str(d) for d in row) + "\n")
        except OSError as e:
            self._text_dialog(f"Save failed: {e}  (ESC to dismiss)")

    # ──────────────────────────────────────────────────────────────────────────
    # Main loop
    # ──────────────────────────────────────────────────────────────────────────

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            running = self.handle_events()

            if self.auto_play and self.mode == "solve":
                self.auto_timer += dt
                if self.auto_timer >= self.auto_interval:
                    self.auto_timer = 0
                    if self.step_idx < len(self.steps):
                        self.go_to_step(self.step_idx + 1)
                    else:
                        self.auto_play = False

            total = len(self.steps)
            if self.brute_force_grid is not None:
                state = "BRUTE FORCED"
            elif self.conflict_cells and self.mode == "solve":
                state = "CONFLICT"
            elif self.stuck and self.step_idx == total:
                state = "STUCK"
            elif self.step_idx == total and not self.stuck:
                state = "SOLVED"
            else:
                state = f"Step {self.step_idx}/{total}"
            pygame.display.set_caption(f"Sudoku Tutor  —  {state}")

            self.draw()

        pygame.quit()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    puzzle_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = SudokuApp(puzzle_file)
    app.run()


if __name__ == "__main__":
    main()
