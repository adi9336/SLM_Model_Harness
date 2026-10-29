@echo off
title Two-Level Agent - Live CLI Demo Runner
echo =======================================================
echo    Launching Live Two-Level Agent CLI Demo Runner
echo =======================================================
echo.
py backend/demo_runner.py --live
if errorlevel 1 (
    python backend/demo_runner.py --live
)
pause
