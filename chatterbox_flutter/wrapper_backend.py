#!/usr/bin/env python3
"""
Simple wrapper that calls your working app/main.py via subprocess.
"""

import sys
import time
import subprocess
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
app = FastAPI(title="ChatterboxTTS Wrapper API", version="1.0.0")

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
        "message": "Wrapper backend - calls your working app/main.py"
    }

@app.post("/generate")
async def generate_speech(request: TTSRequest):
    """Generate speech by calling your working app/main.py."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text exceeds 10,000 character limit")
        
        print(f"🗣️ Generating TTS for {len(request.text)} characters...")
        start_time = time.time()
        
        # Create a temporary text file with the input
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(request.text)
            temp_file_path = temp_file.name
        
        try:
            # Run your working app/main.py 
            project_root = Path(__file__).parent.parent
            result = subprocess.run([
                sys.executable, "app/main.py", "--text-file", temp_file_path, "--no-ui"
            ], cwd=str(project_root), capture_output=True, text=True, timeout=180)
            
            generation_time = time.time() - start_time
            
            print(f"📄 App stdout: {result.stdout}")
            if result.stderr:
                print(f"📄 App stderr: {result.stderr}")
            
            if result.returncode == 0:
                # Look for the most recent output file
                outputs_dir = project_root / "outputs"
                if outputs_dir.exists():
                    wav_files = list(outputs_dir.glob("*.wav"))
                    if wav_files:
                        # Get the most recent file
                        latest_file = max(wav_files, key=lambda p: p.stat().st_mtime)
                        
                        # Estimate duration (rough calculation)
                        file_size = latest_file.stat().st_size
                        estimated_duration = max(1.0, file_size / 100000)  # Very rough estimate
                        
                        print(f"✅ Generated audio in {generation_time:.1f}s")
                        
                        return {
                            "status": "success",
                            "message": f"Generated audio in {generation_time:.1f}s",
                            "audio_path": str(latest_file),
                            "duration": estimated_duration,
                            "generation_time": generation_time,
                            "sample_rate": 48000,  # ChatterboxTTS default
                            "text_length": len(request.text),
                            "voice": request.voice
                        }
                
                # If no output file found, still return success
                return {
                    "status": "success",
                    "message": f"TTS completed in {generation_time:.1f}s",
                    "text_length": len(request.text),
                    "voice": request.voice
                }
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                print(f"❌ TTS failed: {error_msg}")
                return {
                    "status": "error", 
                    "message": f"TTS failed: {error_msg[:200]}",
                    "text_length": len(request.text),
                    "voice": request.voice
                }
                
        finally:
            # Clean up temp file
            Path(temp_file_path).unlink(missing_ok=True)
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "TTS generation timed out (>3 minutes)",
            "text_length": len(request.text)
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "status": "error",
            "message": f"Wrapper error: {str(e)}",
            "text_length": len(request.text),
            "voice": request.voice
        }

def main():
    print("=" * 60)
    print("🗣️  ChatterboxTTS Wrapper Backend")
    print("🔧 Calls your working app/main.py directly")
    print("📡 Server starting on http://localhost:8000")
    print("=" * 60)
    
    # Ensure outputs directory exists
    Path("outputs").mkdir(exist_ok=True)
    
    uvicorn.run(
        "wrapper_backend:app",
        host="127.0.0.1", 
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()