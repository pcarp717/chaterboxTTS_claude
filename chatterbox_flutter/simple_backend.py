#!/usr/bin/env python3
"""
Enhanced backend for ChatterboxTTS Flutter with real TTS.
"""

import sys
import time
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path for app imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# Try to import TTS components by running from project root
tts_available = False
try:
    # Change to project root directory 
    project_root = Path(__file__).parent.parent
    original_cwd = os.getcwd()
    os.chdir(str(project_root))
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    print(f"🔍 Changed to project root: {os.getcwd()}")
    
    # Debug: List what's actually in the app directory
    app_dir = Path("app")
    if app_dir.exists():
        print(f"📁 Files in app directory: {list(app_dir.glob('*.py'))}")
    
    # Try a different import approach - maybe the issue is with module caching
    import importlib
    import app
    importlib.reload(app)
    
    from app.model_manager import ModelManager
    from app.tts_service import TTSService
    from app.voice_manager import VoiceManager
    
    # Initialize TTS components
    print("🔄 Loading TTS components...")
    model_manager = ModelManager()
    voice_manager = VoiceManager()  
    tts_service = TTSService(model_manager, voice_manager)
    tts_available = True
    print("✅ TTS components loaded successfully")
    
    # Change back to original directory
    os.chdir(original_cwd)
except ImportError as e:
    print(f"⚠️ TTS components not available: {e}")
    print("💡 Running in demo mode - no actual audio generation")
    tts_available = False
except Exception as e:
    print(f"⚠️ TTS initialization failed: {e}")
    print("💡 Running in demo mode - no actual audio generation")
    tts_available = False

# FastAPI app
app = FastAPI(title="ChatterboxTTS Simple API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice: str = "default"

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tts_available": tts_available,
        "message": "Enhanced TTS backend running" if tts_available else "Demo mode - TTS not available"
    }

@app.post("/generate")
async def generate_speech(request: TTSRequest):
    """Generate speech using real TTS or demo mode."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text exceeds 10,000 character limit")
        
        if tts_available:
            # Real TTS generation
            print(f"🗣️ Generating TTS for {len(request.text)} characters...")
            start_time = time.time()
            
            try:
                # Generate speech
                audio_tensor, sample_rate = tts_service.generate_speech(
                    text=request.text,
                    voice_profile="Default",
                    exaggeration=0.5,
                    cfg_weight=0.5,
                )
                
                # Save audio file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"flutter_tts_{timestamp}.wav"
                output_dir = Path("outputs")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / filename
                
                saved_path = tts_service.save_audio(
                    audio_tensor, sample_rate, str(output_path), "wav"
                )
                
                generation_time = time.time() - start_time
                duration = len(audio_tensor.squeeze()) / sample_rate
                
                print(f"✅ Generated {duration:.1f}s audio in {generation_time:.1f}s ({duration/generation_time:.1f}x real-time)")
                
                return {
                    "status": "success", 
                    "message": f"Generated {duration:.1f}s audio in {generation_time:.1f}s",
                    "audio_path": str(saved_path),
                    "duration": duration,
                    "generation_time": generation_time,
                    "sample_rate": sample_rate,
                    "text_length": len(request.text),
                    "voice": request.voice
                }
                
            except Exception as e:
                print(f"❌ TTS generation failed: {e}")
                return {
                    "status": "error",
                    "message": f"TTS generation failed: {str(e)}",
                    "text_length": len(request.text),
                    "voice": request.voice
                }
        else:
            # Demo mode
            time.sleep(1)  # Simulate processing
            return {
                "status": "demo",
                "message": f"Demo mode: Would generate speech for '{request.text[:50]}{'...' if len(request.text) > 50 else ''}'",
                "text_length": len(request.text),
                "voice": request.voice,
                "note": "Install TTS components for real audio generation"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    print("=" * 60)
    print("🗣️  ChatterboxTTS Enhanced Backend")
    if tts_available:
        print("✅ Real TTS generation enabled")
    else:
        print("⚠️  Demo mode - TTS components not available")
    print("📡 Server starting on http://localhost:8000")
    print("=" * 60)
    
    # Ensure outputs directory exists
    Path("outputs").mkdir(exist_ok=True)
    
    uvicorn.run(
        "simple_backend:app",
        host="127.0.0.1", 
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()