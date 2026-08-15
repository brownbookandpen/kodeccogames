@echo off
cd /d "%~dp0"
echo Updating Supplies artwork from PSDs...
echo.
python update_supplies.py
if errorlevel 1 (
  echo.
  echo Something went wrong ^(see above^). Make sure Python and psd-tools are installed:
  echo     pip install psd-tools pillow
)
echo.
pause
