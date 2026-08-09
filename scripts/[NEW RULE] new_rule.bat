@echo off
REM Double-click with no arguments: scans every draft under drafts\rules\ and
REM builds/updates all of them, wiring the matching Mission Brief card.
REM
REM Drag a single draft .md file onto this .bat instead if you only
REM want to rebuild that one rule page.

cd /d "%~dp0\.."

if "%~1"=="" (
    python scripts\new_rule.py --all
) else (
    python scripts\new_rule.py "%~1"
)

echo.
pause
