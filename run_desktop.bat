@echo off
echo ============================================================
echo            ChatterboxTTS Desktop Application
echo    High-quality local text-to-speech generation
echo ============================================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\pip.exe install -r requirements.txt
    pause
    exit /b 1
)

REM Check if PyQt6 is installed
venv\Scripts\python.exe -c "import PyQt6" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyQt6 not found! Installing now...
    venv\Scripts\pip.exe install PyQt6
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install PyQt6. Please install manually.
        pause
        exit /b 1
    )
)

REM Check if pygame is installed (for audio playback)
venv\Scripts\python.exe -c "import pygame" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing pygame for audio playback...
    venv\Scripts\pip.exe install pygame
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install pygame. Audio playback may not work.
    )
)

REM Run the desktop application
echo Starting ChatterboxTTS Desktop...
echo.
venv\Scripts\python.exe app\main.py

REM Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    echo Check the error message above for troubleshooting.
    pause
)