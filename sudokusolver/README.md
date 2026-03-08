# Sudoku Tutor & GUI

A human-strategy Sudoku solver with a full pygame GUI and terminal tutor mode.
The solver uses only logic techniques a human would actually apply — no backtracking guessing.

## Files

| File | Purpose |
|------|---------|
| `sudoku_gui.py` | Pygame GUI — step-by-step visual tutor |
| `sudoku_tutor.py` | Terminal solver with plain-English explanations |
| `puzzles.py` | 30 built-in graded puzzles (Tier 0–4) |
| `sudoku_generator.py` | Random puzzle generator with difficulty rating |
| `sudosolv.py` | Simple backtracking solver (brute force) |
| `sd0.txt` – `sd3.txt` | Sample puzzle files |

## Install (one line)

**Mac / Linux** — no repo needed, installs to `~/sudoku-tutor`:

```bash
curl -fsSL https://raw.githubusercontent.com/refap3/claudeCode/main/sudokusolver/install.sh | bash
```

**Windows PowerShell** — installs to `%USERPROFILE%\sudoku-tutor`:

```powershell
powershell -ExecutionPolicy Bypass -Command "iex (irm 'https://raw.githubusercontent.com/refap3/claudeCode/main/sudokusolver/install.ps1')"
```

## Launch / Update

```bash
sudoku               # launch (detached — terminal stays free)
sudoku-update        # pull latest code and dependencies
```

Launchers are written to `~/.local/bin/` by the installer. If that directory is not on your `PATH`, add this to `~/.zshrc` or `~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Or run directly from the install folder:

```bash
bash ~/sudoku-tutor/launch.sh        # Mac / Linux
bash ~/sudoku-tutor/update.sh

%USERPROFILE%\sudoku-tutor\launch.bat  # Windows
%USERPROFILE%\sudoku-tutor\update.bat
```

## Wipe and reinstall

```bash
# Mac / Linux
rm -rf ~/sudoku-tutor
curl -fsSL https://raw.githubusercontent.com/refap3/claudeCode/main/sudokusolver/install.sh | bash

# Windows PowerShell
Remove-Item -Recurse -Force ~/sudoku-tutor
powershell -ExecutionPolicy Bypass -Command "iex (irm 'https://raw.githubusercontent.com/refap3/claudeCode/main/sudokusolver/install.ps1')"
```

## If you already have the repo

```bash
# Mac / Linux — from repo root
bash sudokusolver/install.sh
bash sudokusolver/launch.sh
bash sudokusolver/update.sh

# Windows — from repo root
sudokusolver\install.bat
sudokusolver\launch.bat
sudokusolver\update.bat
```

## Manual (no venv)

```bash
pip install pygame
python sudoku_gui.py           # GUI, loads sd0.txt by default
python sudoku_gui.py sd0.txt   # GUI with explicit file
python sudoku_tutor.py sd0.txt # terminal mode, interactive
python sudoku_tutor.py sd0.txt --auto  # terminal mode, non-interactive
```

## Puzzle File Format

Plain text, one row per line, digits 0 or `.` for unknowns:

```
530070000
600195000
098000060
800060003
400803001
700020006
060000280
000419005
000080079
```

## GUI (`sudoku_gui.py`)

Window: 944 × 680 px. Layout: 9×9 grid (left) + info panel (right) + button bar (bottom).

### Colour Coding

| Colour | Meaning |
|--------|---------|
| Green cell | Digit just placed by this step |
| Orange cell | Candidate just eliminated |
| Yellow cell | House (row/col/box) involved in the strategy |
| Purple cell | Pattern/strategy-defining cell (e.g. X-Wing rows) |
| Blue tint | Cell that shares row, col, or box with the selected cell |
| Red candidate | Candidate being eliminated (shown in pencilmarks) |

### Keyboard Controls

**Solve mode:**

| Key | Action |
|-----|--------|
| `Space` / `→` | Next step |
| `←` / `Backspace` | Previous step |
| `A` | Toggle auto-play (1 step/sec) |
| `C` | Toggle candidate (pencilmark) display |
| `D` | Toggle dark mode |
| `H` | Progressive hint (4 levels: area → digit → strategy → full) |
| `P` | Enter play mode — solve manually |
| `R` | Reset to step 0 |
| `I` | Enter input mode — type a new puzzle |
| `1`–`9` | Digit filter — dim cells not containing that candidate |
| `0` | Clear digit filter |
| `Ctrl+E` | Export current view as PNG |
| `ESC` | Quit |

**Input mode:**

| Key | Action |
|-----|--------|
| `1`–`9` | Set digit in selected cell |
| `0` / `Del` | Clear cell |
| Arrow keys | Move selection |
| `X` | Clear all cells |
| `Ctrl+Z` / `Ctrl+Y` | Undo / redo |
| `Enter` | Solve the entered puzzle |
| `ESC` | Cancel |

**Create mode** (build a puzzle from scratch via the CREATE button):

| Key | Action |
|-----|--------|
| `1`–`9` | Place digit (cursor advances automatically) |
| `0` / `Del` | Clear cell |
| Arrow keys | Move selection |
| `X` | Clear all cells |
| `Ctrl+Z` / `Ctrl+Y` | Undo / redo |
| `Enter` | Open "Play or Solve?" dialog |
| `ESC` | Cancel (return to solve mode without loading) |

After pressing Enter a dialog appears:
- **PLAY (P)** — load the puzzle and enter play mode to solve it yourself
- **SOLVE (S)** — load the puzzle and let the computer walk through the solution step by step
- **CANCEL** — stay in create mode

**Play mode** (solve manually):

| Key | Action |
|-----|--------|
| `1`–`9` | Fill digit in **fill mode** (green=correct, red=wrong) |
| `1`–`9` | Toggle pencilmark candidate in **mark mode** (amber) |
| `0` / `Del` | Erase digit (fill mode) / clear cell's user marks (mark mode) |
| `M` | Toggle between fill mode and mark mode |
| `K` | Clear all user-entered pencilmarks (revert to auto-computed) |
| Arrow keys | Move selection |
| `C` | Toggle candidate (pencilmark) display |
| `H` | Get a hint |
| `ESC` | Exit play mode |

Auto-computed candidates are shown in gray; cells where you've entered your own marks show amber so you always know which is which.

**Drop an image** of a sudoku puzzle onto the window to extract it automatically via Claude API (`pip install anthropic Pillow` + `ANTHROPIC_API_KEY` required).

**Right-click** any cell in solve mode: toggle a pencilmark for the current filter digit.

### Buttons

| Button | Action |
|--------|--------|
| PREV / NEXT | Navigate steps |
| AUTO | Toggle auto-play |
| RESET | Go to step 0 |
| CANDS | Toggle pencilmarks |
| INPUT | Enter input mode |
| PLAY | Enter play mode |
| LOAD | Load a puzzle file (enter path in terminal) |
| PUZZLE | Open built-in puzzle library / generator |

### Timeline Scrubber

The thin bar above the buttons shows progress. Click anywhere on it to jump to that step.

### Config Persistence

Settings are saved to `~/.sudokurc` (JSON) on quit and restored on next launch:
- Dark mode state
- Path of last loaded puzzle

## Terminal Tutor (`sudoku_tutor.py`)

```
python sudoku_tutor.py sd0.txt
```

Each step prints:
- Strategy name and tier
- Plain-English explanation
- Board state with candidates

Press Enter to advance, `q` to quit, or pass `--auto` to print everything without prompts.

## Strategies (Tier 0–5)

| Tier | Strategy |
|------|----------|
| 0 | Full House, Naked Single only (no elimination needed) |
| 1 | Full House, Naked Single, Hidden Single |
| 2 | Naked/Hidden Pairs, Triples, Quads; Locked Candidates (Pointing, Claiming) |
| 3 | X-Wing, Swordfish, Jellyfish, Squirmbag, Y-Wing, XYZ-Wing, Simple Coloring |
| 4 | Unique Rectangle, W-Wing, Skyscraper, 2-String Kite, BUG+1 |
| 5 | Finned X-Wing, XY-Chain |

If no strategy applies, the GUI falls back to a brute-force solver and marks remaining steps as "Brute Force".

## Puzzle Library & Generator

Click **PUZZLE** in the GUI to open the library dialog:
- Browse 30 built-in puzzles organised by tier (0–4); Tier 0 ★ is the "Really Easy" tab
- Click **Load** to load any puzzle instantly
- Click **Generate** to create a new random puzzle at the selected tier (0–4)

The generator uses randomised backtracking to fill a valid grid, then removes cells while maintaining a unique solution, targeting the requested difficulty tier.

## Requirements

- Python 3.8+
- `pygame` — installed automatically by `install.sh` / `install.bat`

**Optional** (for future screenshot-import feature):
- `anthropic` — `pip install anthropic` + set `ANTHROPIC_API_KEY`
- `Pillow` — `pip install Pillow`
