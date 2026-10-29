@echo off
title Two-Level Agent - Web Dashboard Server
echo =======================================================
echo    Launching Two-Level Agent Web Dashboard Server
echo =======================================================
echo.
echo Starting FastAPI and React Web Server on http://localhost:8000 ...
start "" http://localhost:8000
py backend/server.py
if errorlevel 1 (
    python backend/server.py
)
pause
