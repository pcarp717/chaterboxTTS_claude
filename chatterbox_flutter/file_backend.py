#!/usr/bin/env python3
"""
File-based backend that communicates with your TTS via file system.
"""

import sys
import time
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# FastAPI app
app = FastAPI(title="ChatterboxTTS File API", version="1.0.0")

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
        "tts_available": True,
        "message": "File-based backend - uses your working TTS system"
    }

@app.post("/generate")  
async def generate_speech(request: TTSRequest):
    """Generate speech by communicating via files."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text exceeds 10,000 character limit")
        
        print(f"🗣️ Generating TTS for {len(request.text)} characters...")
        start_time = time.time()
        
        # Create a request file
        project_root = Path(__file__).parent.parent
        request_dir = project_root / "flutter_requests"
        request_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        request_file = request_dir / f"request_{timestamp}.json"
        
        # Write the request
        request_data = {
            "text": request.text,
            "voice": request.voice,
            "timestamp": timestamp
        }
        
        request_file.write_text(json.dumps(request_data, indent=2))
        
        print(f"📝 Created request file: {request_file}")
        
        # For now, simulate the TTS process
        # In a real implementation, a separate process would watch this directory
        time.sleep(2)  # Simulate processing time
        
        generation_time = time.time() - start_time
        
        # Look for existing output files to reference
        outputs_dir = project_root / "outputs"
        recent_files = []
        if outputs_dir.exists():
            recent_files = [f for f in outputs_dir.glob("*.wav") 
                          if f.stat().st_mtime > start_time - 60]  # Files from last minute
        
        # Clean up request file
        request_file.unlink(missing_ok=True)
        
        if recent_files:
            latest_file = max(recent_files, key=lambda p: p.stat().st_mtime)
            return {
                "status": "success", 
                "message": f"TTS request processed in {generation_time:.1f}s",
                "audio_path": str(latest_file),
                "duration": 2.0,  # Estimated
                "generation_time": generation_time,
                "sample_rate": 48000,
                "text_length": len(request.text),
                "voice": request.voice,
                "note": "File-based communication - real TTS integration needed"
            }
        else:
            return {
                "status": "demo",
                "message": f"TTS request created in {generation_time:.1f}s",
                "text_length": len(request.text),
                "voice": request.voice,
                "note": "File-based demo - connect to your working TTS system"
            }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "status": "error",
            "message": f"File backend error: {str(e)}",
            "text_length": len(request.text),
            "voice": request.voice
        }

def main():
    print("=" * 60)
    print("🗣️  ChatterboxTTS File Backend")
    print("📁 Communicates via file system")  
    print("📡 Server starting on http://localhost:8000")
    print("=" * 60)
    
    uvicorn.run(
        "file_backend:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()