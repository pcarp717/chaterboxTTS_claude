"""
FastAPI backend for ChatterboxTTS Desktop
"""

import asyncio
import json
import os
import tempfile
from typing import List, Optional
from datetime import datetime
import base64

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

from model_manager import ModelManager
from tts_service import TTSService
from voice_manager import VoiceManager


# Pydantic models for API
class TTSRequest(BaseModel):
    text: str
    voice: str = "Default"
    exaggeration: float = 0.5
    cfg_weight: float = 0.5


class TTSResponse(BaseModel):
    success: bool
    message: str
    audio_data: Optional[str] = None  # Base64 encoded audio
    duration: Optional[float] = None
    generation_time: Optional[float] = None
    sample_rate: Optional[int] = None


class VoiceInfo(BaseModel):
    name: str
    type: str
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    created_date: Optional[str] = None
    description: Optional[str] = None


class SystemStatus(BaseModel):
    model_loaded: bool
    device: str
    ram_usage_percent: float
    vram_used: Optional[float] = None
    vram_total: Optional[float] = None
    vram_usage_percent: Optional[float] = None
    last_used: Optional[float] = None


# FastAPI app
app = FastAPI(title="ChatterboxTTS Desktop API", version="1.0.0")

# Initialize services
model_manager = ModelManager()
voice_manager = VoiceManager()
tts_service = TTSService(model_manager, voice_manager)

# Serve static files
app.mount("/static", StaticFiles(directory="web"), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main HTML page."""
    with open("web/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get current system status."""
    stats = model_manager.get_memory_stats()
    
    return SystemStatus(
        model_loaded=stats["model_loaded"],
        device=stats["device"],
        ram_usage_percent=stats.get("ram_usage_percent", 0),
        vram_used=stats.get("vram_used"),
        vram_total=stats.get("vram_total"),
        vram_usage_percent=stats.get("vram_usage_percent"),
        last_used=stats.get("last_used")
    )


@app.post("/api/preload-model")
async def preload_model():
    """Preload the TTS model into memory."""
    try:
        # This will load the model if not already loaded
        model = model_manager.get_model()
        
        return {
            "success": True,
            "message": "Model loaded successfully",
            "device": model_manager.device
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@app.get("/api/voices", response_model=List[VoiceInfo])
async def get_voices():
    """Get list of available voices."""
    voices = []
    voice_list = voice_manager.get_voice_list()
    
    for voice_name in voice_list:
        info = voice_manager.get_voice_info(voice_name)
        if info:
            voices.append(VoiceInfo(**info))
    
    return voices


@app.post("/api/voices/upload")
async def upload_voice(name: str, file: UploadFile = File(...)):
    """Upload a new voice sample."""
    if not name.strip():
        raise HTTPException(status_code=400, detail="Voice name is required")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Add voice using voice_manager
        success, message = voice_manager.add_voice(name.strip(), temp_path)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@app.delete("/api/voices/{voice_name}")
async def delete_voice(voice_name: str):
    """Delete a voice."""
    if voice_name == "Default":
        raise HTTPException(status_code=400, detail="Cannot delete default voice")
    
    success, message = voice_manager.delete_voice(voice_name)
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)


@app.post("/api/generate", response_model=TTSResponse)
async def generate_speech(request: TTSRequest):
    """Generate speech from text."""
    try:
        import time
        import torch
        import torchaudio as ta
        import io
        
        start_time = time.time()
        
        # Generate audio
        audio_tensor, sample_rate = tts_service.generate_speech(
            text=request.text,
            voice_profile=request.voice,
            exaggeration=request.exaggeration,
            cfg_weight=request.cfg_weight
        )
        
        generation_time = time.time() - start_time
        
        # Convert to WAV bytes
        audio_np = audio_tensor.squeeze().cpu().numpy()
        duration = len(audio_np) / sample_rate
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        
        # Ensure audio is 2D (channels, samples)
        if audio_tensor.dim() == 1:
            audio_tensor = audio_tensor.unsqueeze(0)
        
        ta.save(buffer, audio_tensor, sample_rate, format="wav")
        buffer.seek(0)
        
        # Encode as base64
        audio_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return TTSResponse(
            success=True,
            message=f"Generated {duration:.1f}s audio in {generation_time:.1f}s",
            audio_data=audio_b64,
            duration=duration,
            generation_time=generation_time,
            sample_rate=sample_rate
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await websocket.accept()
    
    try:
        while True:
            # Send periodic status updates
            stats = model_manager.get_memory_stats()
            await websocket.send_json({
                "type": "status_update",
                "data": stats
            })
            
            # Wait for next update or client message
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            except asyncio.TimeoutError:
                pass  # Continue sending updates
                
    except WebSocketDisconnect:
        pass


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    model_manager.shutdown()


if __name__ == "__main__":
    print("🚀 Starting ChatterboxTTS Desktop Web UI...")
    print("📱 Opening at: http://localhost:8000")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )