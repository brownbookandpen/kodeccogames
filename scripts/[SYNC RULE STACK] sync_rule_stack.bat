@echo off
REM Scans every folder under drafts\rules\ ending in " TEXT" (e.g.
REM "ALLEGIANCE TEXT") and rebuilds that rule's stacked image page,
REM wiring it into the matching Mission Brief card on index.html.
REM
REM Just drop/rename/remove PNGs in the source folder and re-run this
REM any time — it always fully regenerates from what's there.

cd /d "%~dp0\.."
python scripts\sync_rule_stack.py

echo.
pause
