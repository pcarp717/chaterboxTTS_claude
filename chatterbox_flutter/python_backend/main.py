#!/usr/bin/env python3
"""
Python backend server for ChatterboxTTS Flutter Desktop App.
Provides REST API endpoints for TTS generation and system monitoring.
"""

import sys
import os
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Add the parent app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    
    # Import the existing TTS components
    from app.model_manager import ModelManager
    from app.tts_service import TTSService  
    from app.voice_manager import VoiceManager
    
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# Initialize TTS components
model_manager = ModelManager()
voice_manager = VoiceManager()
tts_service = TTSService(model_manager, voice_manager)

# FastAPI app
app = FastAPI(
    title="ChatterboxTTS API",
    description="Backend API for ChatterboxTTS Flutter Desktop App",
    version="1.0.0",
)

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class TTSRequest(BaseModel):
    text: str
    voice_profile: str = "Default"
    exaggeration: float = 0.5
    cfg_weight: float = 0.5

class TTSResponse(BaseModel):
    audio_path: str
    duration: float
    sample_rate: int
    generation_time: float
    status: str

class VoiceAddRequest(BaseModel):
    name: str
    file_path: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    model_loaded: bool

# API Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=model_manager.model is not None,
    )

@app.post("/generate", response_model=TTSResponse)
async def generate_speech(request: TTSRequest):
    """Generate speech from text."""
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text exceeds 10,000 character limit")
        
        print(f"Generating TTS for {len(request.text)} characters with voice '{request.voice_profile}'")
        
        # Generate speech
        start_time = time.time()
        audio_tensor, sample_rate = tts_service.generate_speech(
            text=request.text,
            voice_profile=request.voice_profile,
            exaggeration=request.exaggeration,
            cfg_weight=request.cfg_weight,
        )
        generation_time = time.time() - start_time
        
        # Save audio to temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flutter_output_{timestamp}.wav"
        output_path = Path("outputs") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        saved_path = tts_service.save_audio(
            audio_tensor, sample_rate, str(output_path), "wav"
        )
        
        # Calculate duration
        duration = len(audio_tensor.squeeze()) / sample_rate
        
        print(f"Generated {duration:.1f}s audio in {generation_time:.1f}s ({duration/generation_time:.1f}x real-time)")
        
        return TTSResponse(
            audio_path=str(saved_path),
            duration=duration,
            sample_rate=sample_rate,
            generation_time=generation_time,
            status=f"Generated {duration:.1f}s audio in {generation_time:.1f}s",
        )
        
    except Exception as e:
        print(f"TTS generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/stats")
async def get_system_stats():
    """Get current system statistics."""
    try:
        stats = model_manager.get_memory_stats()
        return stats
    except Exception as e:
        print(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def get_voices():
    """Get available voice profiles."""
    try:
        voices = voice_manager.get_voice_list()
        voice_info = []
        
        for voice_name in voices:
            info = voice_manager.get_voice_info(voice_name)
            if info:
                voice_info.append({
                    "name": voice_name,
                    "type": info.get("type", "unknown"),
                    "description": info.get("description", ""),
                    "duration": info.get("duration"),
                    "sample_rate": info.get("sample_rate"),
                    "created_date": info.get("created_date"),
                })
        
        return {"voices": voice_info}
    except Exception as e:
        print(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voices/add")
async def add_voice(request: VoiceAddRequest):
    """Add a new custom voice."""
    try:
        success, message = voice_manager.add_voice(request.name, request.file_path)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        print(f"Error adding voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/voices/{voice_name}")
async def delete_voice(voice_name: str):
    """Delete a custom voice."""
    try:
        if voice_name == "Default":
            raise HTTPException(status_code=400, detail="Cannot delete default voice")
        
        success, message = voice_manager.delete_voice(voice_name)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        print(f"Error deleting voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    print("🚀 ChatterboxTTS Flutter Backend starting...")
    print("📡 API server ready on http://localhost:8000")
    print("📊 Swagger docs available at http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Shutting down ChatterboxTTS Backend...")
    try:
        model_manager.shutdown()
    except Exception as e:
        print(f"Cleanup error: {e}")

def main():
    """Main entry point."""
    print("=" * 60)
    print("🗣️  ChatterboxTTS Flutter Backend")
    print("   REST API Server for Desktop App")
    print("=" * 60)
    
    # Ensure outputs directory exists
    Path("outputs").mkdir(exist_ok=True)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,  # Disable reload to prevent issues with model loading
        log_level="info",
        access_log=True,
    )

if __name__ == "__main__":
    main()