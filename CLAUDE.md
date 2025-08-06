# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

## Reminders
* You are developing on a windows 11 machine via WSL (NOT LINUX or iOS)

* when creating a virtual python environment, please ensure you use one of the following interpreters. Note that 3.13 is the default so be sure to specify 3.11 if that is the version you are using for the project.
    * C:\Users\carp7>py --list-paths
        -V:3.13 \*        C:\\Program Files\\Python\\python.exe
        -V:3.12          C:\\Program Files\\Python12\\python.exe
        -V:3.11          C:\\Program Files\\Python11\\python.exe


ChatterboxTTS Desktop is a Windows 11 application that provides local text-to-speech generation using Resemble AI's Chatterbox TTS model. The application is designed for NVIDIA RTX 3080 GPU optimization and features voice cloning capabilities.

**Current Status**: Planning phase - no code implementation yet. Complete documentation exists.

## Planned Architecture

The application will use a **locally served web UI** approach (Gradio recommended) with a Python backend for rapid development and easy TTS engine integration.

### Core Components (Planned)
- `app/main.py` - Application entry point
- `app/ui.py` - Gradio interface and UI logic
- `app/tts_service.py` - Text processing and TTS generation
- `app/model_manager.py` - Model loading, caching, and memory management
- `app/resource_monitor.py` - GPU/VRAM monitoring
- `app/voice_manager.py` - Custom voice profile management

### Key Dependencies (Planned)
- `chatterbox-tts>=0.1.2` - Core TTS engine
- `gradio` - Web UI framework
- `torch` (with CUDA) - GPU acceleration
- `librosa>=0.10.0`, `soundfile>=0.12.0`, `torchaudio>=2.0.0` - Audio processing
- `psutil>=5.9.0`, `nvidia-ml-py>=12.0.0` - Resource monitoring

## Development Commands

**Note**: No implementation exists yet. When code is added, typical commands will likely be:

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app/main.py

# Run tests (when implemented)
pytest tests/
```

## Critical Architecture Considerations

### Resource Management
- **Model Loading**: Load Chatterbox model (~6.5GB VRAM) only on first generation request
- **Caching Strategy**: Keep model in VRAM for 5 minutes (configurable 1-15 min) after last use
- **Memory Monitoring**: Unload model if VRAM usage exceeds 85% threshold
- **GPU Optimization**: Use `torch.compile()` and potentially FP16 for RTX 3080

### Performance Targets
- Model load time: <15 seconds on RTX 3080
- Generation speed: 1.5x to 5x real-time
- VRAM usage: <7GB during generation
- First generation: <20 seconds from app launch
- Subsequent generations: <5 seconds response time

### Text Processing
- **Auto-chunking**: Split text over 300 characters to prevent quality degradation
- **Input limit**: 10,000 character maximum
- **Output format**: 48kHz WAV primary, MP3 optional

### Voice Management
- Support for 10 custom voice slots plus default voice
- Voice cloning from 7-20 second audio samples (WAV/MP3)
- Voice profiles persist between sessions in `voices/` directory

## Project Structure (Planned)

```
chatterbox-desktop/
├── app/                    # Main application code
├── voices/                 # User voice samples storage
├── outputs/               # Generated audio output directory
├── requirements.txt       # Python dependencies
└── README.md
```

## Development Phases

1. **Phase 1**: Core MVP - Basic TTS, text input, audio playback, resource management
2. **Phase 2**: Voice Management - Custom voice creation, validation, playback controls  
3. **Phase 3**: Optimization - RTX 3080 tuning, UI polish, error handling
4. **Phase 4**: Future Features - Streaming playback, voice mixing, system integration