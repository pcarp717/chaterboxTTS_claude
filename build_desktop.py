#!/usr/bin/env python3
"""
ChatterboxTTS Desktop Builder
Builds and launches the production desktop application.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None, description=""):
    """Run a command with proper error handling."""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Build the desktop application."""
    print("=" * 60)
    print("🏗️  ChatterboxTTS Desktop Builder")
    print("   Building Windows Desktop Application")
    print("=" * 60)
    
    app_dir = Path(__file__).parent
    frontend_dir = app_dir / "frontend"
    
    # Step 1: Build React frontend
    if not run_command("npm run build", cwd=frontend_dir, description="Building React frontend..."):
        print("❌ Frontend build failed")
        return False
    
    print("✅ Frontend built successfully!")
    
    # Step 2: Build Electron app  
    if not run_command("npm run dist", cwd=frontend_dir, description="Building Electron desktop app..."):
        print("❌ Desktop app build failed")
        return False
    
    print("✅ Desktop application built successfully!")
    
    # Step 3: Find the built executable
    dist_dir = frontend_dir / "dist"
    exe_files = list(dist_dir.glob("*.exe"))
    
    if exe_files:
        exe_path = exe_files[0]
        print(f"🎉 Desktop app ready: {exe_path}")
        print("\n📝 To run the application:")
        print(f"   1. Double-click: {exe_path}")
        print("   2. Or run from command line: python launch_desktop.py")
    else:
        print("⚠️  Desktop executable not found, but build completed")
    
    return True

if __name__ == "__main__":
    if main():
        print("\n✅ Build complete!")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)