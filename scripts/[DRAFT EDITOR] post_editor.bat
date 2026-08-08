@echo off
REM Opens the Dev Journal post editor in your browser.
REM Keep this window open while you're writing — closing it stops the local server.
REM Your browser tab will still show your text if you close it by accident,
REM but the Save button needs this window running to actually write the files.

cd /d "%~dp0\.."
python scripts\post_editor.py
pause
