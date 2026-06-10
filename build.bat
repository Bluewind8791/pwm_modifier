@echo off
REM build pwm_modifier tool to exe (deps managed by uv)
cd /d "%~dp0"

REM sync ensures pyperclip + pyinstaller are installed in the project venv
uv sync
uv run pyinstaller pwm_modifier.spec --noconfirm --clean

echo.
echo Build finished. Check the dist folder.
