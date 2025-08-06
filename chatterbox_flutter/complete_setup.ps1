Write-Host "Completing Flutter setup..." -ForegroundColor Green

# Get Flutter packages
Write-Host "Getting Flutter packages..." -ForegroundColor Blue
flutter pub get

# Enable Windows desktop
Write-Host "Enabling Windows desktop support..." -ForegroundColor Blue  
flutter config --enable-windows-desktop

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "VS Code problems should now be resolved." -ForegroundColor Yellow
Write-Host "To run the app: flutter run -d windows" -ForegroundColor Cyan