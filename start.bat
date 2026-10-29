@echo off
title Two-Level Agent Harness - Master Launcher
:menu
cls
echo ============================================================
echo      TWO-LEVEL AGENT ARCHITECTURE - MASTER LAUNCHER
echo ============================================================
echo.
echo   [1] Start Web Dashboard (FastAPI + React UI on :8000)
echo   [2] Run Live Terminal CLI Demo (Interactive Scenarios)
echo   [3] Run Clean Dates Benchmark directly (t001)
echo   [4] Run Setup Ollama & Local xLAM 1B Model
echo   [5] Exit
echo.
set /p choice="Enter option [1-5]: "

if "%choice%"=="1" (
    start "" http://localhost:8000
    py backend/server.py
    pause
    goto menu
)
if "%choice%"=="2" (
    py backend/demo_runner.py --live
    pause
    goto menu
)
if "%choice%"=="3" (
    py backend/demo_runner.py --task tasks/t001_clean_dates --live
    pause
    goto menu
)
if "%choice%"=="4" (
    call setup_ollama.bat
    goto menu
)
if "%choice%"=="5" (
    exit /b
)
goto menu
