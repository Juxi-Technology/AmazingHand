@echo off
cd /d "%~dp0"
title AmazingHand Serial Port Setup (Windows)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp02-Setup_Serial.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] Serial port setup failed. Make sure 2-Setup_Serial.ps1 is readable.
    pause
)
