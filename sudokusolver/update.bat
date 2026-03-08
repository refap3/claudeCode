@echo off
:: Sudoku Tutor — update script (Windows)
:: Pulls the latest code and refreshes dependencies.
setlocal

cd /d "%~dp0"
echo === Sudoku Tutor — update ===

echo Pulling latest code ...
git -C ".." pull

echo Updating dependencies ...
.venv\Scripts\pip install --upgrade pip -q
.venv\Scripts\pip install -r requirements.txt -q

echo Update complete.
