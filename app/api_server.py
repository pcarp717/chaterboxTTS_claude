"""
FastAPI server for ChatterboxTTS Desktop
Provides REST API endpoints for the Electron frontend
"""

import os
import sys
import asyncio
import base64
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_manager import ModelManager
from voice_manager import VoiceManager
from tts_service import TTSService
from resource_monitor import ResourceMonitor

app = FastAPI(title="ChatterboxTTS API", version="1.0.0")

# Add CORS middleware for Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React app static files
frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
if frontend_build_path.exists():
    app.mount("/app", StaticFiles(directory=frontend_build_path, html=True), name="frontend")

# Global service instances
model_manager: ModelManager = None
voice_manager: VoiceManager = None
tts_service: TTSService = None
resource_monitor: ResourceMonitor = None

# Request/Response Models
class TTSRequest(BaseModel):
    text: str
    voice_profile: str = "Default"
    exaggeration: float = 0.5
    cfg_weight: float = 0.5
    format: str = "wav"

class TTSResponse(BaseModel):
    success: bool
    message: str
    audio_file: Optional[str] = None
    duration: Optional[float] = None

class VoiceProfile(BaseModel):
    name: str
    created_date: str
    file_path: str

class SystemStatus(BaseModel):
    gpu_available: bool
    model_loaded: bool
    vram_usage_mb: int
    vram_usage_percent: float
    available_voices: List[str]

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global model_manager, voice_manager, tts_service, resource_monitor
    
    print("🚀 Initializing ChatterboxTTS API server...")
    
    # Initialize services
    model_manager = ModelManager()
    voice_manager = VoiceManager()
    tts_service = TTSService(model_manager, voice_manager)
    resource_monitor = ResourceMonitor()
    
    print("✅ API server ready!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ChatterboxTTS API Server", "status": "running"}

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get current system status"""
    try:
        gpu_info = resource_monitor.get_gpu_status()
        model_loaded = model_manager.is_model_loaded() if model_manager else False
        voices = voice_manager.get_voice_list() if voice_manager else []
        
        return SystemStatus(
            gpu_available=gpu_info["gpu_available"],
            model_loaded=model_loaded,
            vram_usage_mb=gpu_info["vram_used_mb"],
            vram_usage_percent=gpu_info["vram_usage_percent"],
            available_voices=voices
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.post("/generate", response_model=TTSResponse)
async def generate_speech(request: TTSRequest):
    """Generate speech from text"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text exceeds 10,000 character limit")
        
        print(f"🎙️ Generating speech: {len(request.text)} characters")
        start_time = datetime.now()
        
        # Generate audio
        audio_tensor, sample_rate = tts_service.generate_speech(
            text=request.text,
            voice_profile=request.voice_profile,
            exaggeration=request.exaggeration,
            cfg_weight=request.cfg_weight
        )
        
        # Save audio file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chatterbox_output_{timestamp}.{request.format}"
        outputs_dir = Path(__file__).parent.parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        filepath = outputs_dir / filename
        
        tts_service.save_audio(audio_tensor, sample_rate, str(filepath), request.format)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return TTSResponse(
            success=True,
            message=f"Speech generated successfully in {duration:.2f}s",
            audio_file=filename,
            duration=duration
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve generated audio files"""
    outputs_dir = Path(__file__).parent.parent / "outputs"
    file_path = outputs_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=str(file_path),
        media_type="audio/wav" if filename.endswith('.wav') else "audio/mpeg",
        filename=filename
    )

@app.get("/voices", response_model=List[VoiceProfile])
async def list_voices():
    """List available custom voices"""
    try:
        voices = voice_manager.get_voice_list()
        profiles = []
        
        for voice_name in voices:
            if voice_name != "Default":
                voice_data = voice_manager.get_voice_info(voice_name)
                if voice_data:
                    profiles.append(VoiceProfile(
                        name=voice_name,
                        created_date=voice_data.get("created_date", "Unknown"),
                        file_path=voice_data.get("file_path", "")
                    ))
        
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {str(e)}")

@app.post("/voices/create")
async def create_voice(
    voice_name: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """Create a new custom voice from audio sample"""
    try:
        if not voice_name.strip():
            raise HTTPException(status_code=400, detail="Voice name cannot be empty")
        
        # Check file format
        if not audio_file.filename.lower().endswith(('.wav', '.mp3')):
            raise HTTPException(status_code=400, detail="Only WAV and MP3 files are supported")
        
        # Save uploaded file
        voices_dir = Path(__file__).parent.parent / "voices"
        voices_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(audio_file.filename).suffix
        filename = f"{voice_name}_{timestamp}{file_extension}"
        file_path = voices_dir / filename
        
        # Write file
        content = await audio_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create voice profile
        success, message = voice_manager.add_voice(voice_name, str(file_path))
        
        if not success:
            # Clean up file if profile creation failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=400, detail=message)
        
        return {
            "success": True,
            "message": f"Voice '{voice_name}' created successfully",
            "voice_name": voice_name,
            "file_path": str(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create voice: {str(e)}")

@app.delete("/voices/{voice_name}")
async def delete_voice(voice_name: str):
    """Delete a custom voice"""
    try:
        if voice_name == "Default":
            raise HTTPException(status_code=400, detail="Cannot delete default voice")
        
        success, message = voice_manager.delete_voice(voice_name)
        
        if not success:
            raise HTTPException(status_code=404, detail=message)
        
        return {
            "success": True,
            "message": f"Voice '{voice_name}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete voice: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )