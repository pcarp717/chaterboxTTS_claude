# How to Run ChatterboxTTS Flutter Desktop

## 🚀 Quick Start Options

### Option 1: PowerShell (Recommended)
```powershell
# From PowerShell in the chatterbox_flutter directory:
./run_flutter_app.ps1
```

### Option 2: Command Prompt / Batch
```cmd
# From CMD in the chatterbox_flutter directory:
.\run_flutter_app.bat
```

### Option 3: Manual Start
```bash
# Terminal 1: Start Python backend
python python_backend/main.py

# Terminal 2: Start Flutter app (in new terminal)
flutter run -d windows
```

## ⚠️ Common Issues & Solutions

### Issue: "run_flutter_app.bat is not recognized"
**Solution**: You're in PowerShell. Use one of these:
- `./run_flutter_app.ps1` (PowerShell script)  
- `./run_flutter_app.bat` (with dot-slash prefix)
- Switch to CMD: `cmd` then `run_flutter_app.bat`

### Issue: "Flutter is not installed"
**Solution**: 
1. Install Flutter: https://docs.flutter.dev/get-started/install
2. Enable desktop: `flutter config --enable-windows-desktop`
3. Verify: `flutter doctor`

### Issue: "Backend not responding"
**Solution**:
1. Check if Python dependencies are installed: `pip install fastapi uvicorn pydantic`
2. Make sure you're in the correct directory with the existing Python TTS setup
3. Try running backend manually: `python python_backend/main.py`

### Issue: Flutter build errors
**Solution**:
1. Check Flutter doctor: `flutter doctor`
2. Install Visual Studio with C++ tools
3. Try debug mode: `flutter run -d windows` (without --release)
4. Clean and rebuild: `flutter clean && flutter pub get`

## 🛠️ Development Mode

For development with hot reload:
```bash
flutter run -d windows
```

For release build:
```bash
flutter run -d windows --release
```

To build executable:
```bash
flutter build windows --release
```

## 📱 Checking Prerequisites

Run these commands to verify your setup:

```bash
# Check Flutter
flutter doctor
flutter config --enable-windows-desktop

# Check Python dependencies  
pip install fastapi uvicorn pydantic

# Check if backend works
python python_backend/main.py
# Should show: "API server ready on http://localhost:8000"
```

## 🎯 What Should Happen

When successful, you should see:
1. **Backend starts**: Python API server on port 8000
2. **Flutter builds**: Compilation of the desktop app  
3. **App launches**: Beautiful Material Design 3 window opens
4. **Ready to use**: Enter text and generate speech!

The app will have:
- 🎨 Modern UI with dynamic theming
- 🎵 Audio player with waveform visualization
- ⚡ Speed controls (0.5x to 2.0x)
- 🎤 Voice selection and management
- 📊 Real-time system monitoring

Enjoy your modern Flutter desktop TTS experience! 🚀