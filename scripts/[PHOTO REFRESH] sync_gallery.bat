@echo off
REM Double-click after dropping new photos into any of:
REM   images\concept-core-loop\
REM   images\early-prototypes\
REM   images\balancing-playtesting\
REM   images\art-component\
REM
REM Name your photo like a caption, e.g. "New box render with foil logo.png" —
REM that filename becomes the caption and tile title on the site.

cd /d "%~dp0\.."
python scripts\sync_gallery.py

echo.
pause
