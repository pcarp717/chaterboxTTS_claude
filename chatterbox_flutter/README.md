# ChatterboxTTS Flutter Desktop

A modern, beautiful Flutter desktop application for high-quality local text-to-speech generation using Resemble AI's Chatterbox TTS model.

## ✨ Features

### 🎨 Modern UI/UX
- **Material Design 3** with dynamic colors
- **Dark/Light theme** support with system integration  
- **Smooth animations** and micro-interactions
- **Responsive design** that adapts to different screen sizes
- **Native Windows integration** with custom window controls

### 🎤 Advanced Audio Features
- **Built-in audio player** with waveform visualization
- **Precise playback speed control** (0.5x to 2.0x in 0.1x increments)
- **Auto-play** generated audio
- **Real-time progress tracking** with seek functionality
- **High-quality audio processing** with visual feedback

### 🗣️ Text-to-Speech Excellence  
- **Local TTS generation** with Chatterbox model
- **Voice cloning** from audio samples
- **Smart text processing** with automatic chunking
- **Configurable voice parameters** (emotion, generation control)
- **Real-time generation progress** with beautiful indicators

### 🛠️ Voice Management
- **Modern file picker** for voice samples
- **Voice library management** with metadata
- **Instant voice testing** and preview
- **Visual voice information** with creation dates

### 📊 System Monitoring
- **Real-time system stats** with beautiful charts
- **GPU/VRAM monitoring** with visual indicators  
- **Memory usage tracking** with color-coded alerts
- **Performance metrics** and model status

## 🚀 Getting Started

### Prerequisites
- **Flutter 3.10+** with desktop support enabled
- **Windows 10/11** (primary target)
- **Python 3.11+** with existing ChatterboxTTS setup
- **NVIDIA RTX 3080** (or compatible GPU) for optimal performance

### Installation

1. **Install Flutter Desktop**:
   ```bash
   flutter config --enable-windows-desktop
   flutter doctor
   ```

2. **Clone and Setup**:
   ```bash
   cd chatterbox_flutter
   flutter pub get
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

4. **Run the Application**:
   ```bash
   # Terminal 1: Start Python backend
   python python_backend/main.py
   
   # Terminal 2: Start Flutter app  
   flutter run -d windows
   ```

### Quick Start Scripts

**Windows Batch File** (`run_flutter_app.bat`):
```batch
@echo off
echo Starting ChatterboxTTS Flutter Desktop...

REM Start Python backend in background
start /B python python_backend/main.py

REM Wait for backend to start
timeout /t 3

REM Start Flutter app
flutter run -d windows --release
```

## 🏗️ Architecture

### Flutter Frontend
```
lib/
├── main.dart                 # App entry point with Material Design 3
├── screens/
│   └── home_screen.dart      # Main application screen
├── widgets/                  # Reusable UI components
│   ├── audio_player_card.dart      # Advanced audio player with waveform
│   ├── text_input_card.dart        # Smart text input with examples
│   ├── voice_selection_card.dart   # Voice picker with testing
│   ├── system_monitor_card.dart    # Real-time system monitoring
│   ├── voice_management_card.dart  # Voice CRUD operations
│   └── modern_app_bar.dart         # Custom app bar with controls
├── providers/                # State management (Riverpod)
│   └── app_providers.dart           # App-wide state providers
├── services/                 # Business logic
│   ├── tts_service.dart             # TTS API integration
│   ├── audio_service.dart           # Audio playback management
│   └── theme_service.dart           # Theme persistence
└── models/                   # Data models
    ├── audio_state.dart             # Audio playback state
    └── voice_profile.dart           # Voice profile model
```

### Python Backend
```
python_backend/
└── main.py                   # FastAPI REST API server
```

### Communication Flow
```
Flutter App ↔ REST API ↔ Python Backend ↔ TTS Engine
    ↓              ↓              ↓           ↓
Modern UI    JSON/HTTP    FastAPI/Uvicorn  Chatterbox
```

## 🎯 Key Advantages Over PyQt6 Version

| Feature | Flutter Desktop | PyQt6 Version |
|---------|----------------|---------------|
| **UI Framework** | Material Design 3 | Custom styling |
| **Animations** | Smooth, built-in | Manual implementation |
| **Theming** | Dynamic colors, automatic | Manual dark mode |
| **Audio Player** | Beautiful waveform player | Basic pygame integration |
| **File Picker** | Native, modern dialogs | Basic Qt dialogs |  
| **State Management** | Riverpod (reactive) | Manual state handling |
| **Development Speed** | Rapid with hot reload | Slower iteration |
| **Performance** | Compiled to native | Interpreted |
| **Responsiveness** | Async by design | Threading required |

## 🛡️ Error Handling & Robustness

- **Graceful backend connection handling**
- **Automatic retry mechanisms** for API calls  
- **User-friendly error messages** with recovery suggestions
- **Offline mode detection** with appropriate UI states
- **Resource cleanup** on application exit

## 🎨 UI/UX Highlights

### Dynamic Theming
- Automatically adapts to Windows 11 accent colors
- Smooth theme transitions with animations
- Consistent Material Design 3 throughout

### Audio Player
- **Waveform Visualization**: Beautiful animated waveform display
- **Precise Controls**: 0.1x speed increments with instant feedback  
- **Progress Seeking**: Click anywhere on timeline to jump
- **Visual States**: Different colors for play/pause/loading states

### Voice Management  
- **Drag & Drop**: Native file dropping support (planned)
- **Preview Cards**: Beautiful voice profile cards with metadata
- **Instant Testing**: One-click voice preview with sample text

### System Monitoring
- **Live Charts**: Real-time memory usage with smooth animations
- **Color-coded Alerts**: Visual warnings for high usage
- **Detailed Stats**: Comprehensive system information display

## 🚀 Performance Optimizations

- **Lazy Loading**: Components load only when needed
- **Efficient State Management**: Minimal rebuilds with Riverpod
- **Background Processing**: Non-blocking TTS generation
- **Memory Management**: Automatic audio buffer management
- **Native Compilation**: Full compiled performance on Windows

## 🔮 Future Enhancements

- **Voice Mixing**: Blend multiple voices for unique effects
- **Batch Processing**: Generate multiple texts simultaneously  
- **Export Formats**: MP3, FLAC, OGG support
- **Streaming Audio**: Real-time TTS streaming
- **Cloud Sync**: Voice profiles sync across devices
- **Mobile Version**: Same codebase, mobile experience

## 🤝 Development

### Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with hot reload: `flutter run -d windows`
4. Test thoroughly: `flutter test`
5. Submit pull request

### Building for Release
```bash
flutter build windows --release
```

## 📋 Requirements

### System Requirements
- **OS**: Windows 10 v1903+ (64-bit)
- **RAM**: 8GB minimum (16GB recommended)
- **GPU**: NVIDIA RTX 3080 or compatible
- **Storage**: 2GB free space
- **Display**: 1280x720 minimum (1920x1080 recommended)

### Development Requirements  
- **Flutter SDK**: 3.10 or higher
- **Dart SDK**: 3.0 or higher
- **Visual Studio**: 2019 or 2022 with C++ tools
- **Python**: 3.11 with existing TTS dependencies

## 🏆 Why Choose Flutter Desktop?

✅ **Modern**: Latest UI frameworks and design systems  
✅ **Performance**: Compiled to native machine code  
✅ **Beautiful**: Material Design 3 out of the box  
✅ **Maintainable**: Single codebase for multiple platforms  
✅ **Future-proof**: Active development by Google  
✅ **Developer Experience**: Hot reload, excellent tooling

Experience the future of desktop TTS applications with ChatterboxTTS Flutter Desktop! 🎉