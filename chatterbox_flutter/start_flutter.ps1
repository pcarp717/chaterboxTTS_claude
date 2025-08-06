# Simple ChatterboxTTS Flutter Launcher

Write-Host "Starting ChatterboxTTS Flutter Desktop..." -ForegroundColor Green

# Check Flutter
if (Get-Command flutter -ErrorAction SilentlyContinue) {
    Write-Host "Flutter found" -ForegroundColor Green
} else {
    Write-Host "ERROR: Flutter not found!" -ForegroundColor Red
    Write-Host "Install Flutter and run: flutter config --enable-windows-desktop" -ForegroundColor Yellow
    exit 1
}

# Check Python dependencies
Write-Host "Checking Python dependencies..." -ForegroundColor Blue
& python -c "import fastapi, uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install fastapi uvicorn pydantic
}

# Get Flutter dependencies
Write-Host "Installing Flutter packages..." -ForegroundColor Blue
flutter pub get

# Start Python backend in background
Write-Host "Starting Python backend..." -ForegroundColor Blue
$job = Start-Process python -ArgumentList "python_backend\main.py" -PassThru -WindowStyle Hidden
Start-Sleep 3

# Try to start Flutter app
Write-Host "Launching Flutter Desktop App..." -ForegroundColor Green
Write-Host ""
flutter run -d windows

# Cleanup
if ($job -and !$job.HasExited) {
    Stop-Process -Id $job.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Backend stopped" -ForegroundColor Yellow
}