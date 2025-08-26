@echo off
REM Build standalone executable using PyInstaller
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --onefile --windowed toolbox\main.py --name Toolbox
