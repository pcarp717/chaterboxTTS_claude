# ChatterboxTTS Desktop - Setup Guide

## Overview

ChatterboxTTS Desktop is a modern desktop application that provides high-quality local text-to-speech generation using the ChatterboxTTS model. It features a beautiful Electron + React interface with a Python FastAPI backend.

## Architecture

- **Frontend**: Electron + React with Material-UI
- **Backend**: Python FastAPI serving ChatterboxTTS model
- **Communication**: REST API between frontend and backend
- **Audio**: Native HTML5 audio with download/export capabilities

## Prerequisites

### Required Software

1. **Python 3.11 or 3.12** (3.13 may have compatibility issues)
   - Download from: https://python.org/downloads/
   - Make sure to add Python to PATH during installation

2. **Node.js 18+** with npm
   - Download from: https://nodejs.org/
   - LTS version recommended

3. **Git** (for cloning and development)
   - Download from: https://git-scm.com/

### Hardware Requirements

- **GPU**: NVIDIA RTX 3080 or similar (6GB+ VRAM) for optimal performance
- **RAM**: 16GB+ recommended
- **Storage**: 10GB+ free space for models and dependencies
- **OS**: Windows 11 (primary target), Windows 10, or Linux

## Installation

### 1. Clone and Setup Python Environment

```bash
# Clone the repository
git clone <repository-url>
cd Chatterbox_TTS_App

# Create Python virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\\Scripts\\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Setup Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Test the Installation

```bash
# Test Python backend
python app/api_server.py

# In another terminal, test frontend (development mode)
cd frontend
npm start
```

## Running the Application

### Development Mode

For development with hot reloading:

```bash
# Terminal 1: Start Python backend
python app/api_server.py

# Terminal 2: Start React frontend
cd frontend
npm start
```

### Integrated Mode (Recommended)

Use the integrated launcher that starts both backend and frontend:

```bash
python start_app.py
```

This will:
1. Start the Python FastAPI server on `http://127.0.0.1:8000`
2. Launch the Electron desktop app
3. Handle graceful shutdown when closed

## Building for Distribution

### Create Development Build

```bash
python build.py
```

This creates:
- Windows installer in `frontend/dist/`
- Portable version in `build/ChatterboxTTS-Portable/`

### Manual Build Steps

```bash
# Build React frontend
cd frontend
npm run build

# Create Windows executable
npm run dist
```

## Configuration

### Python Backend Settings

The backend can be configured by modifying `app/api_server.py`:

- **Model Settings**: GPU/CPU usage, model caching duration
- **API Settings**: Port, CORS settings
- **Voice Settings**: Maximum voices, file size limits

### Electron Settings

Frontend configuration in `frontend/public/electron.js`:

- **Window Settings**: Size, minimum dimensions
- **Development Settings**: Auto-open DevTools
- **Security Settings**: Context isolation, node integration

## Usage Guide

### Basic Text-to-Speech

1. **Enter Text**: Type or paste text in the text input area (max 10,000 characters)
2. **Select Voice**: Choose "Default" or a custom voice
3. **Generate**: Click "Generate Speech" or press Ctrl+Enter
4. **Play**: Use audio controls to play, pause, or download

### Voice Cloning

1. **Prepare Sample**: Record 10-15 seconds of clear speech (WAV/MP3)
2. **Create Voice**: Click "Create Custom Voice" in Voice Selection
3. **Upload**: Select your audio file and enter a name
4. **Use**: Select your custom voice for generation

### Advanced Settings

- **Emotion Intensity**: Controls expressiveness (0-100%)
- **Voice Guidance**: Controls consistency vs naturalness (0-100%)

## Troubleshooting

### Common Issues

**"Cannot connect to TTS server"**
- Ensure Python backend is running
- Check that port 8000 is available
- Verify Python dependencies are installed

**"Model loading failed"**
- Check GPU memory (need 6GB+ VRAM)
- Verify CUDA installation for GPU acceleration
- Try CPU mode if GPU unavailable

**"Audio playback issues"**
- Check browser audio permissions
- Verify audio file was generated successfully
- Try different audio format settings

**"Voice cloning failed"**
- Ensure audio sample is 7-20 seconds
- Use clear speech with minimal background noise
- Try WAV format instead of MP3

### Performance Optimization

**GPU Acceleration**
- Install CUDA toolkit matching PyTorch version
- Monitor VRAM usage in status bar
- Adjust model caching duration if needed

**Memory Management**
- Model auto-unloads after 5 minutes of inactivity
- Reduce batch size for long texts
- Close other GPU-intensive applications

### Development Tips

**Hot Reloading**
```bash
# Python backend with auto-reload
uvicorn app.api_server:app --reload --host 127.0.0.1 --port 8000

# React frontend with hot reload
cd frontend && npm start
```

**Debugging**
- Use browser DevTools (F12) for frontend debugging
- Check terminal output for Python backend logs
- Enable verbose logging in development mode

## File Structure

```
Chatterbox_TTS_App/
├── app/                    # Python backend
│   ├── api_server.py      # FastAPI server
│   ├── tts_service.py     # TTS logic
│   ├── model_manager.py   # Model loading/caching
│   └── voice_manager.py   # Voice profile management
├── frontend/              # Electron + React app
│   ├── public/            # Electron main process
│   ├── src/               # React components
│   └── build/             # Production build
├── voices/                # Custom voice samples
├── outputs/               # Generated audio files
├── requirements.txt       # Python dependencies
├── start_app.py          # Integrated launcher
└── build.py              # Build script
```

## API Reference

The Python backend provides a REST API at `http://127.0.0.1:8000`:

- `GET /` - Health check
- `GET /status` - System status
- `POST /generate` - Generate speech
- `GET /audio/{filename}` - Serve audio files
- `GET /voices` - List custom voices
- `POST /voices/create` - Create voice profile
- `DELETE /voices/{name}` - Delete voice profile

## Support

For issues and questions:

1. Check this documentation first
2. Review error messages in terminal/console
3. Check system requirements and dependencies
4. Search existing issues or create new ones

## License

This project uses the ChatterboxTTS model from Resemble AI. Please review their licensing terms for commercial usage.