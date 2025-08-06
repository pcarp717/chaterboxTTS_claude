# ChatterboxTTS Flutter Desktop PowerShell Launcher
# Modern UI with Material Design 3

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         ChatterboxTTS Flutter Desktop Application" -ForegroundColor White  
Write-Host "           Modern UI with Material Design 3" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set location to script directory
Set-Location $PSScriptRoot

# Check if Flutter is installed
$flutterInstalled = $false
try {
    $null = flutter --version 2>$null
    Write-Host "✓ Flutter found" -ForegroundColor Green
    $flutterInstalled = $true
} catch {
    Write-Host "ERROR: Flutter is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Flutter Desktop: https://docs.flutter.dev/get-started/install" -ForegroundColor Yellow
    Write-Host "Then enable desktop: flutter config --enable-windows-desktop" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python backend dependencies are available
Write-Host "Checking Python dependencies..." -ForegroundColor Blue
$pythonDepsInstalled = $false
try {
    $null = python -c "import fastapi, uvicorn" 2>$null
    Write-Host "✓ Python backend dependencies found" -ForegroundColor Green
    $pythonDepsInstalled = $true
} catch {
    Write-Host "Installing Python backend dependencies..." -ForegroundColor Yellow
    pip install fastapi uvicorn pydantic
}

# Install Flutter dependencies
Write-Host "Installing Flutter dependencies..." -ForegroundColor Blue
flutter pub get

# Start Python backend server in background
Write-Host "Starting Python TTS backend..." -ForegroundColor Blue
$backendJob = Start-Job -ScriptBlock {
    param($workingDir)
    Set-Location $workingDir
    python python_backend\main.py
} -ArgumentList $PWD

Write-Host "✓ Backend starting on http://localhost:8000" -ForegroundColor Green

# Wait for backend to initialize
Write-Host "Waiting for backend to start..." -ForegroundColor Blue
Start-Sleep -Seconds 5

# Check if backend is running
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Backend is running successfully" -ForegroundColor Green
    $backendRunning = $true
} catch {
    Write-Host "WARNING: Backend may not be running. Check python_backend\main.py" -ForegroundColor Yellow
    Write-Host "The app will still start but TTS features may not work." -ForegroundColor Yellow
    Write-Host ""
}

# Start Flutter desktop application
Write-Host "Starting ChatterboxTTS Flutter Desktop..." -ForegroundColor Blue
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " 🚀 Launching Modern Desktop App" -ForegroundColor White
Write-Host " 💻 Native Windows application with Material Design 3" -ForegroundColor Gray
Write-Host " 🎤 High-quality local TTS with beautiful audio controls" -ForegroundColor Gray
Write-Host " 🎨 Dynamic theming with smooth animations" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    flutter run -d windows --release
    $flutterExitCode = $LASTEXITCODE
} catch {
    $flutterExitCode = 1
}

if ($flutterExitCode -ne 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "Application failed to start. Exit code: $flutterExitCode" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common solutions:" -ForegroundColor Yellow
    Write-Host "1. Make sure Flutter desktop is enabled: flutter config --enable-windows-desktop" -ForegroundColor White
    Write-Host "2. Check flutter doctor for any issues: flutter doctor" -ForegroundColor White
    Write-Host "3. Verify Windows development tools are installed" -ForegroundColor White
    Write-Host "4. Try debug mode: flutter run -d windows" -ForegroundColor White
    Write-Host "============================================================" -ForegroundColor Red
    
    Read-Host "Press Enter to exit"
}

# Clean up background job when Flutter app exits
if ($backendJob) {
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Write-Host "Cleaned up backend process" -ForegroundColor Green
}