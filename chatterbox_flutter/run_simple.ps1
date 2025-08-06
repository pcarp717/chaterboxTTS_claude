Write-Host "Starting simplified ChatterboxTTS Flutter Desktop..." -ForegroundColor Green

# Clean and get packages
Write-Host "Cleaning and getting packages..." -ForegroundColor Blue
flutter clean
flutter pub get

# Start Python backend in background
Write-Host "Starting Python backend..." -ForegroundColor Blue
$job = Start-Process python -ArgumentList "python_backend\main.py" -PassThru -WindowStyle Hidden
Start-Sleep 3

# Run Flutter app
Write-Host "Launching simplified Flutter app..." -ForegroundColor Green
flutter run -d windows

# Cleanup
if ($job -and !$job.HasExited) {
    Stop-Process -Id $job.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Backend stopped" -ForegroundColor Yellow
}