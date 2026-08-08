@echo off
REM Double-click with no arguments: scans every draft under drafts\ and
REM builds/updates all of them, refreshing the homepage Dev Journal.
REM
REM Drag a single draft .md file onto this .bat instead if you only
REM want to rebuild that one post.

cd /d "%~dp0\.."

if "%~1"=="" (
    python scripts\new_post.py --all
) else (
    python scripts\new_post.py "%~1"
)

echo.
pause
