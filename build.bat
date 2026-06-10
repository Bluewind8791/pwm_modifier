@echo off
REM build pwm_modifier tool to exe (deps managed by uv)
cd /d "%~dp0"

REM sync ensures pyperclip + pyinstaller are installed in the project venv
uv sync
uv run pyinstaller pwm_modifier.spec --noconfirm --clean

REM move the built exe to the project root
if exist "dist\pwm_modifier.exe" (
    move /y "dist\pwm_modifier.exe" "pwm_modifier.exe" >nul
) else (
    echo Build failed: dist\pwm_modifier.exe not found.
    exit /b 1
)

REM clean up build artifacts
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo Build finished. pwm_modifier.exe is in the project root.
