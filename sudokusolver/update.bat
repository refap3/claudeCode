@echo off
:: Sudoku Tutor — update script (Windows)
setlocal

cd /d "%~dp0"
echo === Sudoku Tutor — update ===

:: Check if we're inside a git repo
git -C ".." rev-parse --show-toplevel >nul 2>&1
if %errorlevel% == 0 (
    echo Pulling latest code ...
    git -C ".." pull
) else (
    echo Downloading latest files from GitHub ...
    set "TMP=%TEMP%\sudoku_update_%RANDOM%"
    git clone --depth 1 --filter=blob:none --sparse https://github.com/refap3/claudeCode "%TMP%\repo" -q
    git -C "%TMP%\repo" sparse-checkout set sudokusolver
    xcopy /E /Y "%TMP%\repo\sudokusolver\*" "%~dp0" >nul
    rd /s /q "%TMP%" 2>nul
)

echo Updating dependencies ...
.venv\Scripts\python -m pip install --upgrade pip -q
.venv\Scripts\python -m pip install -r requirements.txt -q

echo Update complete.
