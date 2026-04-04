# Mobile-Friendly Test Plan — Sudoku Tutor Web

## Devices / Environments

| Environment | Tool |
|---|---|
| iPhone (small, ~375px) | Chrome DevTools device emulation or real device |
| Android phone (~390px) | Chrome DevTools or real device |
| iPad / tablet (~768px) | DevTools or real device |
| Desktop baseline | Any desktop browser, 1280px+ |

---

## 1. Layout & Responsive Sizing

### 1.1 Grid scales to screen width
- [ ] On a 375px-wide screen the grid fills the available width (no horizontal scroll on the main area)
- [ ] Grid stays square (viewBox aspect ratio is preserved — not squashed or stretched)
- [ ] On desktop (>760px) the grid remains 540×540px

### 1.2 Toolbar
- [ ] On mobile the toolbar scrolls horizontally — all buttons reachable by swiping
- [ ] No vertical overflow from the toolbar (does not push grid off screen)
- [ ] Toolbar is single-row on mobile (flex-wrap: nowrap applies)

### 1.3 Vertical stacking
- [ ] On mobile, panel appears below the grid (column layout)
- [ ] Panel is full-width below the grid
- [ ] No element overflows the viewport horizontally

### 1.4 Status bar
- [ ] Hidden on screens ≤760px (keyboard shortcuts not relevant on touch)
- [ ] Visible on desktop

### 1.5 Timeline
- [ ] Taller hit area (28px) on mobile — easy to tap
- [ ] Tapping the timeline scrubs to correct step

---

## 2. Number Pad (Touch Input)

### 2.1 Visibility rules
- [ ] Numpad **hidden** in Solve mode
- [ ] Numpad **visible** in Input mode (after tapping INPUT button)
- [ ] Numpad **visible** in Create mode (after tapping CREATE button)
- [ ] Numpad **visible** in Play mode (after tapping PLAY button)
- [ ] Numpad returns to hidden when leaving input/play/create back to Solve

### 2.2 Layout
- [ ] 10 buttons arranged 5×2 (digits 1–9 + ⌫ delete)
- [ ] Buttons fill grid width
- [ ] Each button at least 52px tall (large enough tap target)
- [ ] Delete button styled distinctly (red)

### 2.3 Input mode — digit entry
- [ ] Select a cell → tap a digit → digit appears in cell
- [ ] Cursor advances to next cell automatically after digit entry
- [ ] Tap ⌫ → clears selected cell
- [ ] Conflict cells highlighted red if duplicate entered

### 2.4 Play mode — digit entry
- [ ] Select an empty non-given cell → tap a digit → digit fills the cell
- [ ] Cursor advances after fill
- [ ] Tap ⌫ → clears cell and any marks
- [ ] Cannot overwrite a given (pre-filled) cell

### 2.5 Play mode — mark mode
- [ ] Enable MARK via numpad button (turns green when active)
- [ ] Tap digit → candidate pencil mark toggled in cell (not filled)
- [ ] Tap same digit again → mark removed
- [ ] Tap ⌫ → all marks and value cleared
- [ ] CANDS off: manual marks still visible
- [ ] CANDS on: auto-computed candidates shown alongside manual marks

### 2.8 Play mode — HINT
- [ ] HINT fills correct digit into the selected cell
- [ ] HINT with no cell selected auto-fills the first available empty cell
- [ ] Status bar (or panel) shows `Hint: R#C# = #` after each hint

### 2.6 Play mode — stopwatch & completion
- [ ] Stopwatch appears below timeline immediately on entering play mode
- [ ] Stopwatch counts up in M:SS format
- [ ] Filling the last correct cell triggers 🎉 Solved! modal
- [ ] Modal shows correct elapsed time
- [ ] Stopwatch freezes at completion time
- [ ] Tapping OK dismisses the modal
- [ ] Exiting play mode (EXIT PLAY) hides the stopwatch

### 2.7 Create mode — digit entry
- [ ] Same behavior as Input mode

---

## 3. Touch Interactions on the Grid

### 3.1 Cell selection
- [ ] Single tap selects a cell (highlighted blue)
- [ ] Tapping same cell again deselects it (in Solve mode)
- [ ] Row, column, and box peers highlighted after selection
- [ ] No accidental double-tap zoom (touch-action: manipulation applied)

### 3.2 After selection, numpad works
- [ ] Tap numpad digit → value appears in selected cell (Input/Play)
- [ ] Tap ⌫ → clears selected cell

---

## 4. Button Touch Targets

- [ ] All `.btn` elements are at least 40px tall on mobile
- [ ] Tapping buttons does not require precise pointer — comfortable with a finger
- [ ] Mode badge (INPUT / PLAY / CREATE) visible and readable

---

## 5. Dialogs

### 5.1 Puzzle library
- [ ] Opens on tap of PUZZLE button
- [ ] Scrollable puzzle list (can scroll within dialog)
- [ ] Tap puzzle card loads the puzzle
- [ ] Dialog close button (✕) reachable and tappable

### 5.2 API key dialog
- [ ] Opens correctly
- [ ] Input field accepts text (mobile keyboard appears on focus)
- [ ] Save / Clear / Close buttons all reachable

---

## 6. Dark Mode

- [ ] DARK button toggles dark theme on mobile
- [ ] All numpad buttons render correctly in dark theme
- [ ] SVG grid colors apply correctly in dark theme

---

## 7. Digit Filter Bar (mobile)

- [ ] Digit filter row is **not visible** in the toolbar on mobile (≤760px)
- [ ] A full-width digit filter strip (1–9) appears below the numpad in grid-area
- [ ] Tapping a filter button highlights all matching cells; tapping again clears the filter
- [ ] Numpad digit button matching the active filter shows a bottom-border underline indicator
- [ ] Tapping a numpad digit with **no cell selected** toggles the filter for that digit
- [ ] Tapping a numpad digit with a cell selected enters the digit as normal (filter not affected)

---

## 8. Desktop Regression (no mobile changes should break desktop)

- [ ] SVG remains 540×540 on desktop
- [ ] Digit filter row visible in toolbar on desktop (unchanged)
- [ ] Mobile digit filter strip hidden on desktop
- [ ] Keyboard shortcuts still work (Space, arrows, A, C, D, H, P, I, 1–9, R)
- [ ] Numpad is hidden on desktop (non-touch) in all modes
- [ ] Status bar visible on desktop
- [ ] Toolbar wraps normally on desktop

---

## 9. Orientation & Resize

- [ ] Rotating phone portrait→landscape: grid resizes without reload
- [ ] Grid layout adapts (landscape may show panel beside grid if width >760px)
- [ ] Resizing browser window between mobile and desktop sizes updates layout

---

## 10. Image Import (if API key available)

- [ ] IMAGE button is tappable on mobile
- [ ] File picker opens (camera or photo library on iOS/Android)
- [ ] Flash overlay (spinner) displays correctly over full screen

---

## Known Limitations / Out of Scope

- Keyboard shortcuts are not tested on mobile (by design — numpad replaces them)
- Paste-from-clipboard image import may not work on all mobile browsers
- The puzzle generator (CREATE → generate tier) requires server-side support
