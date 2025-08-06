@echo off
echo ============================================================
echo          ChatterboxTTS Flutter Desktop Application  
echo            Modern UI with Material Design 3
echo ============================================================
echo.

REM Change to the Flutter project directory
cd /d "%~dp0"

REM Check if Flutter is installed
flutter --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Flutter is not installed or not in PATH!
    echo Please install Flutter Desktop: https://docs.flutter.dev/get-started/install
    echo Then enable desktop: flutter config --enable-windows-desktop
    pause
    exit /b 1
)

REM Check if Python backend dependencies are available
python -c "import fastapi, uvicorn" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Python backend dependencies...
    pip install fastapi uvicorn pydantic
)

REM Install Flutter dependencies
echo Installing Flutter dependencies...
flutter pub get

REM Start Python backend server in background
echo Starting Python TTS backend...
start /B python python_backend\main.py
echo Backend starting on http://localhost:8000

REM Wait for backend to initialize
echo Waiting for backend to start...
timeout /t 5

REM Check if backend is running
python -c "import requests; requests.get('http://localhost:8000/health')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Backend may not be running. Check python_backend\main.py
    echo The app will still start but TTS features may not work.
    echo.
)

REM Start Flutter desktop application
echo Starting ChatterboxTTS Flutter Desktop...
echo.
echo ============================================================
echo  🚀 Launching Modern Desktop App
echo  💻 Native Windows application with Material Design 3
echo  🎤 High-quality local TTS with beautiful audio controls
echo  🎨 Dynamic theming with smooth animations
echo ============================================================
echo.

flutter run -d windows --release

REM Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo Application exited with error code: %ERRORLEVEL%
    echo.
    echo Common solutions:
    echo 1. Make sure Flutter desktop is enabled: flutter config --enable-windows-desktop
    echo 2. Check flutter doctor for any issues: flutter doctor
    echo 3. Verify Windows development tools are installed
    echo 4. Try debug mode: flutter run -d windows
    echo ============================================================
    pause
)