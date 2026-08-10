@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python not found on PATH. Install Python 3, then try again.
    pause
    exit /b 1
)

python -c "import psd_tools" >nul 2>nul
if errorlevel 1 (
    echo Installing required packages: psd-tools, pillow ...
    python -m pip install --quiet psd-tools pillow
)

python "%~dp0update_allegiance.py"

echo.
pause
