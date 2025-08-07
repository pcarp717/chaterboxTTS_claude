#!/usr/bin/env python3
"""
ChatterboxTTS Desktop Application Launcher
Starts both the Python FastAPI backend and Electron frontend
"""

import os
import sys
import subprocess
import threading
import time
import signal
import requests
from pathlib import Path

def check_python_env():
    """Check if we're in the correct Python environment with required packages."""
    try:
        import chatterbox
        import fastapi
        import uvicorn
        print("✅ Python environment check passed")
        return True
    except ImportError as e:
        print(f"❌ Missing required Python packages: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_node_env():
    """Check if Node.js and npm are available and frontend is built."""
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("❌ Frontend dependencies not installed")
        print("Please run: cd frontend && npm install")
        return False
    
    # Check if build directory exists for production
    if not (frontend_dir / "build").exists():
        print("⚠️  Frontend not built for production")
        print("For development, this is fine. For production, run: cd frontend && npm run build")
    
    print("✅ Node.js environment check passed")
    return True

def start_python_server():
    """Start the FastAPI server only."""
    def run_fastapi_server():
        try:
            import uvicorn
            from app.api_server import app
            
            print("🚀 Starting Python FastAPI server...")
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=8000,
                log_level="info",
                access_log=False
            )
        except Exception as e:
            print(f"❌ Failed to start FastAPI server: {e}")
            os._exit(1)
    
    fastapi_thread = threading.Thread(target=run_fastapi_server, daemon=True)
    fastapi_thread.start()
    return fastapi_thread

def wait_for_server():
    """Wait for the Python server to be ready."""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=1)
            if response.status_code == 200:
                print("✅ Python server is ready")
                return True
        except requests.exceptions.RequestException:
            if attempt == 0:
                print("⏳ Waiting for Python server to start...")
            time.sleep(1)
    
    print("❌ Python server failed to start within 30 seconds")
    return False

def start_electron_app():
    """Start the Electron application."""
    frontend_dir = Path(__file__).parent / "frontend"
    
    print("🚀 Starting Electron app...")
    
    # Get current environment and ensure PATH is preserved
    env = os.environ.copy()
    
    try:
        # Check if npm is available
        npm_cmd = "npm"
        if sys.platform == "win32":
            # On Windows, try npm.cmd first
            npm_cmd = "npm.cmd"
        
        # Try to start in development mode first
        if (frontend_dir / "src").exists():
            print("📱 Starting in development mode...")
            process = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=frontend_dir,
                env=env,
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
        else:
            # Production mode
            print("📱 Starting in production mode...")
            process = subprocess.Popen(
                [npm_cmd, "run", "electron"],
                cwd=frontend_dir,
                env=env,
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
        
        return process
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm.")
        return None
    except Exception as e:
        print(f"❌ Failed to start Electron app: {e}")
        return None

def main():
    """Main application launcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ChatterboxTTS Desktop Application")
    parser.add_argument("--web-only", action="store_true", help="Start only the web interface (no Electron)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🗣️  ChatterboxTTS Desktop Application")
    print("   Starting integrated TTS application...")
    print("=" * 60)
    
    # Change to the app directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)
    
    # Environment checks
    if not check_python_env():
        sys.exit(1)
    
    if not args.web_only and not check_node_env():
        sys.exit(1)
    
    # Start Python server
    server_thread = start_python_server()
    
    # Wait for server to be ready
    if not wait_for_server():
        sys.exit(1)
    
    electron_process = None
    if not args.web_only:
        # Start Electron app
        electron_process = start_electron_app()
        if not electron_process:
            print("⚠️  Electron failed to start, continuing with web-only mode")
    
    print("✅ Application started successfully!")
    print("\n📝 Usage:")
    if args.web_only or not electron_process:
        print("   - Open your browser to: http://localhost:7860")
        print("   - The Gradio web interface will be available there")
    else:
        print("   - The TTS interface will open in a desktop window")
    print("   - Type your text and select a voice")
    print("   - Click 'Generate Speech' to create audio")
    print("   - Use the audio controls to play and download")
    print("\n🛑 Press Ctrl+C to stop the application")
    
    def signal_handler(signum, frame):
        print("\n\n🛑 Shutting down application...")
        if electron_process:
            try:
                electron_process.terminate()
                electron_process.wait(timeout=3)
            except:
                electron_process.kill()
        # Kill any remaining Node.js processes
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/f", "/im", "node.exe"], capture_output=True)
        except:
            pass
        print("✅ Application stopped")
        os._exit(0)
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if electron_process:
            # Wait for Electron process to finish
            electron_process.wait()
        else:
            # Web-only mode - wait for keyboard interrupt
            print("🌐 Web interface running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n🛑 Application finished")

if __name__ == "__main__":
    main()