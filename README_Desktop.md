# ChatterboxTTS Desktop Application

A native PyQt6 desktop application for high-quality local text-to-speech generation using Resemble AI's Chatterbox TTS model.

## Features

### 🖥️ Native Desktop Experience
- **No Browser Required**: True desktop application that runs natively on Windows
- **Responsive UI**: Clean, professional interface with resizable panels
- **System Integration**: Native file dialogs, notifications, and window management

### 🎤 Advanced Text-to-Speech
- **High-Quality Generation**: Local TTS using Chatterbox model with RTX 3080 optimization
- **Voice Cloning**: Create custom voices from 7-20 second audio samples
- **Smart Text Processing**: Automatic text chunking for optimal quality
- **Configurable Settings**: Adjustable exaggeration and CFG weight parameters

### 🛠️ Voice Management
- **Custom Voice Creation**: Upload WAV/MP3 samples to create personalized voices
- **Voice Library**: Manage multiple custom voices alongside the default voice
- **Voice Information**: View details like duration, sample rate, and creation date
- **Easy Deletion**: Remove unwanted custom voices with confirmation dialogs

### 📊 System Monitoring
- **Real-time Stats**: Monitor model loading status, RAM usage, and VRAM usage
- **GPU Optimization**: Automatic CUDA detection and memory management
- **Performance Metrics**: Track generation speed and model usage timing

### 💾 Audio Export
- **High-Quality Export**: Export generated speech as 48kHz WAV files
- **Custom Naming**: Automatic timestamped filenames with custom save locations
- **Direct Download**: Easy file export through native file dialogs

## Installation & Setup

### Prerequisites
- Windows 10/11
- Python 3.11 or later
- NVIDIA RTX 3080 (or compatible GPU) for optimal performance

### Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Desktop App**:
   
   **Windows (Recommended)**:
   ```bash
   run_desktop.bat
   ```
   
   **Or manually**:
   ```bash
   venv\Scripts\python.exe app\main.py
   ```

3. **WSL Users**: 
   - Install X server (VcXsrv, X410)
   - Set DISPLAY environment variable
   - Or run from Windows PowerShell instead

### Testing the Installation
```bash
python test_ui.py
```

## Application Interface

### Main Panel (Left)
- **Text Input**: Large text area with character counter (10,000 character limit)
- **Voice Selection**: Dropdown to choose between default and custom voices
- **Voice Settings**: Sliders for exaggeration (emotion level) and CFG weight
- **Generate Button**: Large, prominent button to start TTS generation
- **Export Controls**: WAV export functionality with native file dialogs

### System Panel (Right)
- **System Status Tab**: Real-time monitoring of:
  - Model loading status
  - Device (CUDA/CPU) information
  - RAM and VRAM usage percentages
  - Time since last model use
  
- **Voice Management Tab**: Tools for:
  - Adding new custom voices from audio files
  - Deleting existing custom voices
  - Viewing voice information and metadata

## Technical Features

### Performance Optimizations
- **Threaded Generation**: TTS runs in background thread to prevent UI freezing
- **Smart Memory Management**: Automatic model loading/unloading based on usage
- **GPU Acceleration**: Full CUDA support for RTX 3080 optimization
- **Efficient Audio Processing**: Direct tensor handling for optimal performance

### User Experience
- **Progress Feedback**: Visual progress bars during generation
- **Status Messages**: Color-coded status updates (success, error, info)
- **Responsive Design**: Resizable interface that adapts to different screen sizes
- **Native Look**: OS-appropriate styling and behavior

### Error Handling
- **Graceful Degradation**: Handles missing models, GPU issues, and file errors
- **User Feedback**: Clear error messages with actionable solutions
- **Automatic Cleanup**: Proper resource cleanup on application exit

## Comparison with Web Version

| Feature | Desktop (PyQt6) | Web (Gradio) |
|---------|-----------------|--------------|
| **Runtime** | Native executable | Browser-based |
| **Performance** | Direct system access | HTTP overhead |
| **File Access** | Native dialogs | Web file uploads |
| **System Integration** | Full Windows integration | Limited to browser |
| **Resource Usage** | Optimized native code | Browser + server |
| **Offline Usage** | Complete offline | Requires local server |
| **Multi-window** | Native window management | Single browser tab |
| **Notifications** | System notifications | Browser-only |

## Architecture

```
ChatterboxTTS Desktop/
├── app/
│   ├── main.py              # Application entry point
│   ├── ui.py                # PyQt6 desktop interface (NEW)
│   ├── tts_service.py       # TTS generation logic
│   ├── model_manager.py     # Model loading and memory management
│   └── voice_manager.py     # Custom voice management
├── run_desktop.bat          # Windows launcher (NEW)
├── run_desktop.py           # Cross-platform launcher (NEW)
├── test_ui.py               # UI component testing (NEW)
└── requirements.txt         # Updated with PyQt6
```

## Development Notes

### Threading Model
- **Main Thread**: UI updates and user interactions
- **Worker Thread**: TTS generation to prevent blocking
- **Timer Updates**: Periodic system status refresh

### Memory Management
- **Lazy Loading**: Model loads only when needed
- **Timeout Unloading**: Model unloads after 5 minutes of inactivity
- **VRAM Monitoring**: Tracks and displays GPU memory usage

### Voice Processing
- **File Validation**: Checks audio format and duration
- **Metadata Extraction**: Stores voice information for display
- **Safe Deletion**: Confirmation dialogs prevent accidental removal

## Future Enhancements

- **Audio Playback**: Built-in audio player with playback controls
- **Streaming Generation**: Real-time audio streaming during generation
- **Batch Processing**: Process multiple texts simultaneously
- **Voice Mixing**: Blend multiple voices for unique effects
- **System Tray**: Minimize to system tray for background operation
- **Hotkeys**: Global keyboard shortcuts for quick access

## Troubleshooting

### Common Issues

1. **Application won't start in WSL**
   - Solution: Run from Windows terminal or install X server

2. **PyQt6 import errors**
   - Solution: `pip install PyQt6` in the virtual environment

3. **CUDA not detected**
   - Solution: Install NVIDIA drivers and CUDA toolkit

4. **Memory errors during generation**
   - Solution: Close other applications to free VRAM

### Support
- Check `test_ui.py` output for import/setup issues
- Monitor system status tab for memory and GPU information
- Review error messages in status display for specific issues

## License & Credits

Built on the foundation of the Gradio web version, this desktop application provides a native Windows experience for ChatterboxTTS while maintaining all core functionality with enhanced performance and system integration.