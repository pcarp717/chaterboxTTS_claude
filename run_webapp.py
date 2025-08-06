"""
Launch script for ChatterboxTTS Desktop Web UI
"""

import os
import sys
import webbrowser
import time
from threading import Timer

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

from app.api import app
import uvicorn


def open_browser():
    """Open browser after a short delay."""
    time.sleep(2)
    webbrowser.open('http://localhost:8000')


if __name__ == "__main__":
    print("=" * 60)
    print("🗣️  ChatterboxTTS Desktop - Web UI")
    print("   Professional text-to-speech with voice cloning")
    print("=" * 60)
    print()
    print("🚀 Starting web server...")
    print("📱 Interface will open at: http://localhost:8000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser in background
    Timer(1.5, open_browser).start()
    
    # Start server
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=False  # Reduce console noise
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)