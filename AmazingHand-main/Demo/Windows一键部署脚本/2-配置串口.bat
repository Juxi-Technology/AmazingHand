@echo off
cd /d "%~dp0"
title AmazingHand Serial Port Setup (Windows)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp02-ÅäÖÃ´®¿Ú.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] Serial port setup script failed. Make sure 2-ÅäÖÃ´®¿Ú.ps1 is readable.
    pause
)
