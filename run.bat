@echo off
echo ===================================================
echo   Energy Resilience Command - AI Agents Backend
echo ===================================================
echo Starting FastAPI server...

:: Start the FastAPI backend in a new command prompt window
start cmd /k "python backend\main.py"

:: Wait for a few seconds to let the server start
timeout /t 3 /nobreak >nul

:: Open the browser to the Mirror Agent Dashboard
echo Opening browser for testing...
start http://localhost:8000/

echo.
echo The backend is now running in a separate window.
echo You can test the end-to-end pipeline by clicking "Initialize Simulation" in the browser.
echo.
pause
