# Sudoku Tutor & GUI

A human-strategy Sudoku solver with a full pygame GUI, terminal tutor mode, and a **browser-based web app** deployable via Docker.
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
| `web/` | FastAPI web application (see below) |
| `Dockerfile` | Container build for the web app |
| `docker-compose.yml` | Compose config — host port **8011** → container 8080 |
| `web-requirements.txt` | Python deps for the web app |

---

## Web App (Browser / Docker)

A full-featured browser port of the pygame GUI — same solver, same strategies, same colour coding.
Works on desktop and **mobile phones** (responsive layout, touch number pad).

### Quick start (local)

```bash
pip install -r web-requirements.txt
uvicorn web.main:app --reload --port 8080
# Open http://localhost:8080
```

With image/screenshot import:

```bash
ANTHROPIC_API_KEY=sk-ant-... uvicorn web.main:app --reload --port 8080
```

### Docker (local)

```bash
docker compose up --build          # available at http://localhost:8011
ANTHROPIC_API_KEY=sk-ant-... docker compose up --build  # with image import
```

### Deploy to a remote Docker host

**Option 1 — clone from GitHub (recommended):**

```bash
# on the remote host:
git clone https://github.com/refap3/claudeCode.git
cd claudeCode/sudokusolver
ANTHROPIC_API_KEY=sk-ant-... docker compose up --build -d
```

**Option 2 — push files via scp** (no GitHub access needed):

```bash
NEWHOST=192.168.1.XX   # change to target IP

ssh pi@$NEWHOST "mkdir -p ~/sudokusolver/web/static"

scp sudoku_tutor.py sudoku_generator.py puzzles.py sudosolv.py \
    Dockerfile docker-compose.yml web-requirements.txt pi@$NEWHOST:~/sudokusolver/

scp -r web/ pi@$NEWHOST:~/sudokusolver/

ssh pi@$NEWHOST "cd ~/sudokusolver && \
  ANTHROPIC_API_KEY=sk-ant-... docker compose up --build -d"
```

**Update an existing deployment:**

```bash
# Option 1 — on the host:
git pull && docker compose up --build -d

# Option 2 — from your machine (re-run scp commands above, then):
ssh pi@$NEWHOST "cd ~/sudokusolver && docker compose up --build -d"
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/solve` | Full human-strategy solve — returns all steps + grid states |
| POST | `/api/validate` | Conflict detection only |
| POST | `/api/brute-force` | Backtracking solve → solution + iteration count |
| GET | `/api/puzzles` | List all 30 built-in puzzles |
| GET | `/api/puzzles/{id}` | Single puzzle by index |
| POST | `/api/generate` | Generate puzzle `{"tier": 0-4}` |
| POST | `/api/extract-image` | Multipart image → Claude vision → 9×9 grid |
| GET | `/api/config` | `{has_anthropic_key, has_generator, has_puzzles}` |

### Playing a puzzle (web)

**To solve step-by-step:** load a puzzle from the **PUZZLE** library → use **NEXT / PREV** to step through. The right panel explains the strategy at each step.

**To play yourself:**
1. Click **PUZZLE** → pick a puzzle, or click **INPUT** → enter a puzzle → click **PLAY**
2. Tap/click a cell to select it
3. Enter a digit (keyboard `1`–`9`, or the on-screen number pad on touch devices)
4. Use **MARK** to switch to pencil-mark mode — digits become small candidates instead of filling the cell
5. **CANDS** auto-computes all valid candidates for every empty cell and overlays them; your manual marks are always shown regardless
6. **HINT** fills the correct digit into the selected cell
7. Wrong digits are highlighted in red

### Web keyboard shortcuts

**Solve mode:**

| Key | Action |
|-----|--------|
| `Space` / `→` | Next step |
| `←` / `Backspace` | Previous step |
| `A` | Toggle auto-play |
| `C` | Toggle candidates |
| `D` | Toggle dark mode |
| `H` | Progressive hint |
| `P` | Enter play mode |
| `I` | Enter input mode |
| `R` | Reset to step 0 |
| `1`–`9` | Digit filter |
| `0` | Clear filter |

**Input / Create mode:** `1`–`9` set digit and advance · `0` clear and advance · `Del`/`Backspace` clear in place · Arrows move · cursor wraps to next row after column 9 · `Enter` solve · `Esc` cancel · `Ctrl+Z/Y` undo/redo · `X` clear all

**Play mode:** `1`–`9` fill · `M` mark/pencil mode · `K` clear all marks · `H` hint · `C` auto-candidates · `Esc` exit

### Touch / mobile (web)

On phones and tablets the layout switches automatically:
- The grid scales to screen width
- The toolbar scrolls horizontally
- A **number pad** (1–9 + ⌫) appears below the grid in Input, Create, and Play modes
- In Play mode the pad also shows **✎ MARK**, **HINT**, and **CANDS** buttons — no keyboard needed

### API Key (web)

No environment variable needed. Click **API KEY** in the toolbar to paste your Anthropic key — it is stored in browser `localStorage` and sent only during image extraction. The button turns green when a key is set. If you try to import an image without a key the dialog opens automatically.

If `ANTHROPIC_API_KEY` is set as an environment variable on the server it is used as a fallback; the browser-stored key always takes priority.

### Image / text import (web)

- **Paste image**: Cmd+V / Ctrl+V with a screenshot in clipboard → Claude vision extracts the puzzle
- **Paste text**: Cmd+V / Ctrl+V with a text puzzle (9 lines × 9 digits) → loads directly, no API key needed
- **Drag & drop**: drop an image file onto the browser window
- **Upload button**: click 📷 IMAGE in the toolbar

### Tutor sidebar

The right-hand panel shows:
- Current step strategy, tier, explanation, placements and eliminations
- **All Steps** list — builds line by line as you advance: `1. R1C2=3  Naked Single`. Click any row to jump to that step.

If no human strategy can make progress the solver stops and reports **STUCK**. A confirmation dialog offers to continue with **brute-force backtracking** — if accepted, the solution is appended as a final step showing how many backtracking iterations were needed.

---

## Desktop GUI (`sudoku_gui.py`)

### Install (one line)

**Mac / Linux** — installs to `~/sudoku-tutor`:

```bash
curl -fsSL https://raw.githubusercontent.com/refap3/claudeCode/main/sudokusolver/install.sh | bash
```

**Windows PowerShell** — installs to `%USERPROFILE%\sudoku-tutor`:

```powershell
powershell -ExecutionPolicy Bypass -Command "iex (irm 'https://raw.githubusercontent.com/refap3/claudeCode/main/sudokusolver/install.ps1')"
```

### Launch / Update

```bash
sudoku               # launch (detached — terminal stays free)
sudoku-update        # pull latest code and dependencies
```

Or run directly:

```bash
pip install pygame
python sudoku_gui.py           # loads sd0.txt by default
python sudoku_gui.py sd0.txt   # explicit file
```

### Colour Coding

| Colour | Meaning |
|--------|---------|
| Green cell | Digit just placed by this step |
| Orange cell | Candidate just eliminated |
| Yellow cell | House (row/col/box) involved in the strategy |
| Purple cell | Pattern/strategy-defining cell (e.g. X-Wing rows) |
| Blue tint | Peer cell (same row, col, or box as selection) |
| Red candidate | Candidate being eliminated (pencilmarks) |

### Keyboard Controls

**Solve mode:**

| Key | Action |
|-----|--------|
| `Space` / `→` | Next step |
| `←` / `Backspace` | Previous step |
| `A` | Toggle auto-play (1 step/sec) |
| `C` | Toggle candidate display |
| `D` | Toggle dark mode |
| `H` | Progressive hint |
| `P` | Enter play mode |
| `R` | Reset to step 0 |
| `I` | Enter input mode |
| `1`–`9` | Digit filter |
| `0` | Clear digit filter |
| `Ctrl+E` | Export PNG |
| `Ctrl+V` / `Cmd+V` | Paste puzzle (text or image via Claude) |
| `ESC` | Quit |

**Input / Create mode:** `1`–`9` set and advance · `0` clear and advance · `Del`/`Backspace` clear in place · Arrows move · cursor wraps to next row after column 9 · `X` clear all · `Ctrl+Z/Y` undo/redo · `Enter` solve · `ESC` cancel

**Play mode:** `1`–`9` fill/mark · `M` toggle fill/mark · `K` clear marks · `H` hint · `C` cands · `ESC` exit

### Paste / Image import (desktop)

`Ctrl+V` / `Cmd+V` tries in order:
1. **Text**: clipboard contains 9 lines × 9 digits → loaded into input mode instantly
2. **Image**: clipboard contains a screenshot → sent to Claude vision API → puzzle extracted

Drop an image file onto the window for the same image extraction flow.

### Tutor panel

The right-hand panel shows the current step's strategy, tier, explanation, placements, and eliminations.
Below that, an **All Steps** list accumulates line by line as you advance: `1. R1C2=3  Naked Single`.

### Timeline Scrubber

The thin bar below the grid shows progress. Click anywhere to jump to that step.

---

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

---

## Strategies (Tier 0–5)

| Tier | Strategy |
|------|----------|
| 0 | Full House, Naked Single only |
| 1 | Full House, Naked Single, Hidden Single |
| 2 | Naked/Hidden Pairs, Triples, Quads; Pointing Pairs, Box-Line Reduction |
| 3 | X-Wing, Swordfish, Jellyfish, Squirmbag, Y-Wing, XYZ-Wing, Simple Coloring |
| 4 | Unique Rectangle, W-Wing, Skyscraper, 2-String Kite, BUG+1 |
| 5 | Finned X-Wing, XY-Chain |

If no strategy applies, the solver falls back to backtracking and marks remaining steps as "Brute Force".

---

## Requirements

**Desktop GUI:** Python 3.8+ · `pygame`

**Web app:** Python 3.11+ · `fastapi` · `uvicorn[standard]` · `python-multipart` · `anthropic` · `Pillow`

**Image import (both):** `anthropic` + `Pillow` + Anthropic API key
