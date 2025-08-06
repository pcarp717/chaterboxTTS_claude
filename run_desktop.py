#!/usr/bin/env python3
"""
ChatterboxTTS Desktop Application Launcher

This script launches the PyQt6 desktop version of ChatterboxTTS.
For WSL users: This should be run from Windows terminal or with X11 forwarding enabled.
"""

import sys
import os
import subprocess

def main():
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in WSL and provide guidance
    if "microsoft" in os.uname().release.lower() if hasattr(os, 'uname') else False:
        print("=" * 70)
        print("IMPORTANT: WSL detected!")
        print("For the desktop app to work, you need to:")
        print("1. Install an X server like VcXsrv or X410")
        print("2. Set DISPLAY environment variable")
        print("3. Or run this from Windows PowerShell/CMD instead:")
        print(f"   cd {script_dir}")
        print("   .\\venv\\Scripts\\python.exe app\\main.py")
        print("=" * 70)
        print()
    
    try:
        # Set up environment
        os.environ["PYTHONPATH"] = os.path.join(script_dir, "app")
        
        # For WSL, try to detect display
        if "DISPLAY" not in os.environ and hasattr(os, 'uname'):
            if "microsoft" in os.uname().release.lower():
                os.environ["DISPLAY"] = ":0"
                print("Set DISPLAY=:0 for WSL")
        
        # Change to the app directory and run the main script
        app_dir = os.path.join(script_dir, "app")
        python_exe = os.path.join(script_dir, "venv", "Scripts", "python.exe")
        main_script = os.path.join(app_dir, "main.py")
        
        if not os.path.exists(python_exe):
            # Try alternative paths
            python_exe = sys.executable
            
        print("Starting ChatterboxTTS Desktop Application...")
        print(f"Python: {python_exe}")
        print(f"Script: {main_script}")
        print()
        
        # Run the application
        result = subprocess.run([python_exe, main_script], 
                              cwd=script_dir,
                              env=os.environ.copy())
        
        return result.returncode
        
    except Exception as e:
        print(f"Error launching application: {e}")
        print("\nIf you're on Windows, try running from PowerShell/CMD:")
        print("  .\\venv\\Scripts\\python.exe app\\main.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())