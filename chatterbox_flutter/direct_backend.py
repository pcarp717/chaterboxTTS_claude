#!/usr/bin/env python3
"""
Direct backend that imports TTS modules in the same process.
"""

import sys
import time
import os
import threading
from datetime import datetime
from pathlib import Path

# Change to project root immediately
project_root = Path(__file__).parent.parent
os.chdir(str(project_root))
sys.path.insert(0, str(project_root))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# Try to import TTS components directly
tts_components = None
tts_error = None

def load_tts_components():
    global tts_components, tts_error
    try:
        print("🔄 Loading TTS components directly...")
        from app.model_manager import ModelManager
        from app.tts_service import TTSService
        from app.voice_manager import VoiceManager
        
        model_manager = ModelManager()
        voice_manager = VoiceManager()
        tts_service = TTSService(model_manager, voice_manager)
        
        tts_components = {
            'model_manager': model_manager,
            'voice_manager': voice_manager, 
            'tts_service': tts_service
        }
        print("✅ TTS components loaded successfully!")
        
    except Exception as e:
        tts_error = str(e)
        print(f"❌ TTS loading failed: {e}")

# Load TTS components in a separate thread to avoid blocking startup
print(f"📁 Working directory: {os.getcwd()}")
load_thread = threading.Thread(target=load_tts_components)
load_thread.start()

# FastAPI app
app = FastAPI(title="ChatterboxTTS Direct API", version="1.0.0")

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
    # Wait for TTS loading to complete
    if load_thread.is_alive():
        load_thread.join(timeout=1)
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tts_available": tts_components is not None,
        "tts_error": tts_error,
        "message": "Direct TTS integration" if tts_components else f"TTS not available: {tts_error}"
    }

@app.post("/generate")
async def generate_speech(request: TTSRequest):
    """Generate speech using direct TTS integration."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text exceeds 10,000 character limit")
        
        # Wait for TTS loading if still in progress
        if load_thread.is_alive():
            print("⏳ Waiting for TTS components to finish loading...")
            load_thread.join(timeout=30)
        
        if not tts_components:
            return {
                "status": "error",
                "message": f"TTS not available: {tts_error or 'Failed to load'}",
                "text_length": len(request.text),
                "voice": request.voice
            }
        
        print(f"🗣️ Generating TTS for {len(request.text)} characters...")
        start_time = time.time()
        
        # Generate speech using loaded components
        tts_service = tts_components['tts_service']
        
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
        print(f"❌ TTS generation error: {e}")
        return {
            "status": "error",
            "message": f"TTS generation failed: {str(e)}",
            "text_length": len(request.text),
            "voice": request.voice
        }

def main():
    print("=" * 60)
    print("🗣️  ChatterboxTTS Direct Backend")
    print("🔗 Direct integration with TTS components")
    print("📡 Server starting on http://localhost:8000")
    print("=" * 60)
    
    # Ensure outputs directory exists
    Path("outputs").mkdir(exist_ok=True)
    
    uvicorn.run(
        "direct_backend:app",
        host="127.0.0.1", 
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()