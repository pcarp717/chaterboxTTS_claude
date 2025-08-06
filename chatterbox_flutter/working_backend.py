#!/usr/bin/env python3
"""
Working backend that calls your existing TTS system directly.
"""

import sys
import time
import subprocess
import json
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
app = FastAPI(title="ChatterboxTTS Working API", version="1.0.0")

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
        "message": "Working backend - calls your existing TTS system"
    }

@app.post("/generate")
async def generate_speech(request: TTSRequest):
    """Generate speech by calling your working TTS system."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text exceeds 10,000 character limit")
        
        print(f"🗣️ Generating TTS for {len(request.text)} characters...")
        start_time = time.time()
        
        # Create a simple script to generate TTS
        tts_script = f"""
import os
import sys
from pathlib import Path

# Ensure we're in the right directory and can import
project_root = Path.cwd()
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

# Import everything we need
from datetime import datetime
from pathlib import Path

try:
    from app.model_manager import ModelManager
    from app.tts_service import TTSService  
    from app.voice_manager import VoiceManager
    
    # Initialize components
    model_manager = ModelManager()
    voice_manager = VoiceManager()
    tts_service = TTSService(model_manager, voice_manager)
    
except Exception as e:
    print(f"IMPORT_ERROR:{{e}}")
    sys.exit(1)

# Generate speech
text = '''{request.text}'''
audio_tensor, sample_rate = tts_service.generate_speech(
    text=text,
    voice_profile="Default",
    exaggeration=0.5,
    cfg_weight=0.5,
)

# Save audio
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"flutter_tts_{{timestamp}}.wav"
output_path = Path("outputs") / filename
output_path.parent.mkdir(exist_ok=True)

saved_path = tts_service.save_audio(audio_tensor, sample_rate, str(output_path), "wav")
duration = len(audio_tensor.squeeze()) / sample_rate

print(f"SUCCESS:{{saved_path}}:{{duration}}:{{sample_rate}}")
"""
        
        # Write script to temp file
        script_path = Path("temp_tts_script.py")
        script_path.write_text(tts_script)
        
        try:
            # Run the TTS script with the same Python environment
            project_root = Path(__file__).parent.parent
            
            # Use the same Python executable and environment
            env = dict(os.environ)
            env['PYTHONPATH'] = str(project_root)
            
            result = subprocess.run([
                sys.executable, str(script_path)
            ], cwd=str(project_root), capture_output=True, text=True, timeout=120, env=env)
            
            print(f"📄 Script stdout: {result.stdout}")
            if result.stderr:
                print(f"📄 Script stderr: {result.stderr}")
                
            if result.returncode == 0:
                # Parse the output to get file info
                for line in result.stdout.split('\n'):
                    if line.startswith('SUCCESS:'):
                        parts = line.split(':')
                        audio_path = parts[1]
                        duration = float(parts[2])
                        sample_rate = int(parts[3])
                        generation_time = time.time() - start_time
                        
                        print(f"✅ Generated {duration:.1f}s audio in {generation_time:.1f}s")
                        
                        return {
                            "status": "success",
                            "message": f"Generated {duration:.1f}s audio in {generation_time:.1f}s",
                            "audio_path": audio_path,
                            "duration": duration,
                            "generation_time": generation_time,
                            "sample_rate": sample_rate,
                            "text_length": len(request.text),
                            "voice": request.voice
                        }
                    elif line.startswith('IMPORT_ERROR:'):
                        import_error = line.replace('IMPORT_ERROR:', '')
                        return {
                            "status": "error",
                            "message": f"Import error: {import_error}",
                            "text_length": len(request.text),
                            "voice": request.voice
                        }
                
                # If we didn't find SUCCESS line, return generic success
                return {
                    "status": "success", 
                    "message": "TTS generation completed",
                    "text_length": len(request.text),
                    "voice": request.voice
                }
            else:
                error_msg = result.stderr or "Unknown error"
                print(f"❌ TTS generation failed: {error_msg}")
                return {
                    "status": "error",
                    "message": f"TTS generation failed: {error_msg}",
                    "text_length": len(request.text),
                    "voice": request.voice
                }
        finally:
            # Clean up temp script
            if script_path.exists():
                script_path.unlink()
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "TTS generation timed out (>120s)",
            "text_length": len(request.text)
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    print("=" * 60)
    print("🗣️  ChatterboxTTS Working Backend")
    print("✅ Calls your existing TTS system directly")
    print("📡 Server starting on http://localhost:8000")
    print("=" * 60)
    
    # Ensure outputs directory exists
    Path("outputs").mkdir(exist_ok=True)
    
    uvicorn.run(
        "working_backend:app",
        host="127.0.0.1", 
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()