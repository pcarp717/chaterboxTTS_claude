@echo off
REM ChatterboxTTS Desktop Launcher
REM This batch file launches the ChatterboxTTS web application

echo.
echo ==========================================
echo   ChatterboxTTS Desktop Launcher
echo ==========================================
echo.
echo Starting ChatterboxTTS Desktop...
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please make sure you're running this from the ChatterboxTTS folder.
    echo.
    pause
    exit /b 1
)

REM Launch the application
echo Opening ChatterboxTTS in your default browser...
echo.
echo ==========================================
echo  Ready! ChatterboxTTS is now running.
echo  
echo  - Web interface: http://localhost:8000
echo  - Press Ctrl+C in this window to stop
echo ==========================================
echo.

venv\Scripts\python.exe run_webapp.py

REM If we get here, the app has stopped
echo.
echo ChatterboxTTS has been stopped.
echo.
pause