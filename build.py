#!/usr/bin/env python3
"""
Build script for ChatterboxTTS Desktop Application
Creates a distributable Windows executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and handle errors."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            shell=True if isinstance(cmd, str) else False,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_requirements():
    """Check if all build requirements are met."""
    print("🔍 Checking build requirements...")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js.")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        print(f"✅ npm: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js with npm.")
        return False
    
    # Check Python
    print(f"✅ Python: {sys.version.split()[0]}")
    
    # Check required Python packages
    try:
        import chatterbox
        import fastapi
        import uvicorn
        print("✅ Python packages: Available")
    except ImportError as e:
        print(f"❌ Missing Python packages: {e}")
        return False
    
    return True

def build_frontend():
    """Build the React frontend for production."""
    print("🏗️  Building React frontend...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Install dependencies
    run_command(["npm", "install"], cwd=frontend_dir)
    
    # Build for production
    run_command(["npm", "run", "build"], cwd=frontend_dir)
    
    print("✅ Frontend build completed")

def create_executable():
    """Create Windows executable using electron-builder."""
    print("📦 Creating Windows executable...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Run electron-builder
    run_command(["npm", "run", "dist"], cwd=frontend_dir)
    
    print("✅ Executable created")

def create_portable_version():
    """Create a portable version with Python backend included."""
    print("📁 Creating portable version...")
    
    build_dir = Path(__file__).parent / "build"
    portable_dir = build_dir / "ChatterboxTTS-Portable"
    
    # Create directories
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy Python app
    app_dir = Path(__file__).parent / "app"
    shutil.copytree(app_dir, portable_dir / "app", dirs_exist_ok=True)
    
    # Copy requirements
    shutil.copy2(Path(__file__).parent / "requirements.txt", portable_dir)
    
    # Copy launcher script
    shutil.copy2(Path(__file__).parent / "start_app.py", portable_dir)
    
    # Copy Electron build
    frontend_build = Path(__file__).parent / "frontend" / "build"
    if frontend_build.exists():
        shutil.copytree(frontend_build, portable_dir / "frontend" / "build", dirs_exist_ok=True)
    
    # Copy Electron files
    electron_files = [
        "frontend/public/electron.js",
        "frontend/public/preload.js",
        "frontend/package.json"
    ]
    
    for file_path in electron_files:
        src = Path(__file__).parent / file_path
        dst = portable_dir / file_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    
    # Create batch file launcher for Windows
    batch_content = '''@echo off
echo Starting ChatterboxTTS Desktop...
python start_app.py
pause
'''
    
    with open(portable_dir / "ChatterboxTTS.bat", "w") as f:
        f.write(batch_content)
    
    # Create README
    readme_content = '''# ChatterboxTTS Desktop - Portable Version

## Requirements

1. Python 3.11 or 3.12 with pip
2. Node.js 18+ with npm
3. NVIDIA GPU with CUDA support (recommended)

## Installation

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install Node.js dependencies:
   ```
   cd frontend
   npm install
   ```

## Running the Application

### Windows
Double-click `ChatterboxTTS.bat`

### Command Line
```
python start_app.py
```

## Features

- High-quality text-to-speech generation
- Custom voice cloning
- Modern desktop interface
- Local processing (no internet required)
- GPU acceleration support

## Troubleshooting

If you encounter issues:

1. Make sure you have the correct Python version (3.11 or 3.12)
2. Ensure CUDA is installed if using NVIDIA GPU
3. Check that all dependencies installed correctly
4. Try running `python -m pip install --upgrade pip` first

For support, check the project documentation.
'''
    
    with open(portable_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print(f"✅ Portable version created in: {portable_dir}")

def main():
    """Main build process."""
    print("=" * 60)
    print("🏗️  ChatterboxTTS Desktop Build Process")
    print("=" * 60)
    
    if not check_requirements():
        print("❌ Build requirements not met. Please install missing dependencies.")
        sys.exit(1)
    
    # Build steps
    try:
        build_frontend()
        create_executable()
        create_portable_version()
        
        print("\n" + "=" * 60)
        print("✅ Build completed successfully!")
        print("\nGenerated files:")
        print("📦 Windows Installer: frontend/dist/")
        print("📁 Portable Version: build/ChatterboxTTS-Portable/")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()