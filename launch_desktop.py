#!/usr/bin/env python3
"""
ChatterboxTTS Desktop Launcher
Production desktop application launcher.
"""

import os
import sys
import time
import signal
import threading
import subprocess
import webbrowser
from pathlib import Path

def start_api_server():
    """Start the FastAPI server."""
    try:
        import uvicorn
        from app.api_server import app
        
        print("🚀 Starting ChatterboxTTS API server...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="warning",
            access_log=False
        )
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        sys.exit(1)

def wait_for_server():
    """Wait for API server to be ready."""
    import requests
    for i in range(30):
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    """Launch the desktop application."""
    print("=" * 60)
    print("🗣️  ChatterboxTTS Desktop Application")
    print("   Production Desktop Version")
    print("=" * 60)
    
    # Change to app directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)
    
    # Check if frontend build exists
    build_dir = app_dir / "frontend" / "build"
    if not build_dir.exists():
        print("❌ Frontend not built. Run: cd frontend && npm run build")
        sys.exit(1)
    
    # Start API server in background
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Wait for server
    print("⏳ Starting API server...")
    if not wait_for_server():
        print("❌ API server failed to start")
        sys.exit(1)
    
    print("✅ API server ready!")
    
    # Start Electron desktop app
    frontend_dir = app_dir / "frontend"
    try:
        print("🚀 Launching desktop application...")
        
        # Try direct Electron execution first
        electron_process = None
        try:
            electron_process = subprocess.Popen(
                ["npx", "electron", "."],
                cwd=frontend_dir,
                env=os.environ.copy(),
                shell=True,  # Add shell=True for Windows
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
        except FileNotFoundError:
            # Fallback to npm command
            electron_process = subprocess.Popen(
                ["npm", "run", "electron"],
                cwd=frontend_dir,
                env=os.environ.copy(),
                shell=True,  # Add shell=True for Windows
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
        
        print("✅ ChatterboxTTS Desktop is running!")
        print("📱 Desktop app should open in a new window")
        print("🌐 Or visit: http://127.0.0.1:8000/app")
        print("🛑 Close the desktop window or press Ctrl+C to exit")
        
        # Wait for Electron to close
        electron_process.wait()
        
    except Exception as e:
        print(f"⚠️  Desktop app launch failed: {e}")
        print("🌐 Opening in browser instead...")
        webbrowser.open("http://127.0.0.1:8000/app")
        print("🛑 Press Ctrl+C to exit")
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()