# ChatterboxTTS Desktop Shortcut Creator
# Run this script to create desktop and Start Menu shortcuts

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "  ChatterboxTTS Shortcut Creator" -ForegroundColor Cyan  
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Get the current directory (where ChatterboxTTS is located)
$ChatterboxPath = $PSScriptRoot
$BatchFile = Join-Path $ChatterboxPath "Launch ChatterboxTTS.bat"

# Check if batch file exists
if (-not (Test-Path $BatchFile)) {
    Write-Host "ERROR: Launch ChatterboxTTS.bat not found!" -ForegroundColor Red
    Write-Host "Please make sure you're running this from the ChatterboxTTS folder." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Creating shortcuts..." -ForegroundColor Green
Write-Host ""

# Create Desktop Shortcut
try {
    $WshShell = New-Object -comObject WScript.Shell
    $DesktopPath = [System.Environment]::GetFolderPath('Desktop')
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\ChatterboxTTS Desktop.lnk")
    $Shortcut.TargetPath = $BatchFile
    $Shortcut.WorkingDirectory = $ChatterboxPath
    $Shortcut.Description = "ChatterboxTTS Desktop - AI Text-to-Speech with Voice Cloning"
    $Shortcut.IconLocation = "shell32.dll,23"  # Microphone icon
    $Shortcut.Save()
    
    Write-Host "✅ Desktop shortcut created successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create desktop shortcut: $_" -ForegroundColor Red
}

# Create Start Menu Shortcut  
try {
    $StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
    $StartShortcut = $WshShell.CreateShortcut("$StartMenuPath\ChatterboxTTS Desktop.lnk")
    $StartShortcut.TargetPath = $BatchFile
    $StartShortcut.WorkingDirectory = $ChatterboxPath
    $StartShortcut.Description = "ChatterboxTTS Desktop - AI Text-to-Speech with Voice Cloning"
    $StartShortcut.IconLocation = "shell32.dll,23"  # Microphone icon
    $StartShortcut.Save()
    
    Write-Host "✅ Start Menu shortcut created successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create Start Menu shortcut: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now launch ChatterboxTTS by:" -ForegroundColor White
Write-Host "• Double-clicking the desktop icon" -ForegroundColor Yellow
Write-Host "• Searching 'ChatterboxTTS' in Start Menu" -ForegroundColor Yellow
Write-Host "• Double-clicking 'Launch ChatterboxTTS.bat'" -ForegroundColor Yellow
Write-Host ""
Write-Host "The web interface will open automatically at:" -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"