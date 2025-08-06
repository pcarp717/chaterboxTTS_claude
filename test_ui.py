#!/usr/bin/env python3
"""
Simple test for PyQt6 UI components without running the full application.
"""

import sys
import os

# Add app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import PyQt6
        print("[OK] PyQt6 imported")
    except ImportError as e:
        print(f"[FAIL] PyQt6 import failed: {e}")
        return False
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("[OK] PyQt6.QtWidgets imported")
    except ImportError as e:
        print(f"[FAIL] PyQt6.QtWidgets import failed: {e}")
        return False
    
    try:
        from model_manager import ModelManager
        print("[OK] ModelManager imported")
    except ImportError as e:
        print(f"[FAIL] ModelManager import failed: {e}")
        return False
    
    try:
        from tts_service import TTSService
        print("[OK] TTSService imported")
    except ImportError as e:
        print(f"[FAIL] TTSService import failed: {e}")
        return False
    
    try:
        from voice_manager import VoiceManager
        print("[OK] VoiceManager imported")
    except ImportError as e:
        print(f"[FAIL] VoiceManager import failed: {e}")
        return False
    
    return True

def test_ui_creation():
    """Test creating the UI class without showing it."""
    print("\nTesting UI creation...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui import ChatterboxUI
        
        # Create application (required for Qt widgets)
        app = QApplication([])
        
        # Create the UI (but don't show it)
        ui = ChatterboxUI(app)
        print("[OK] ChatterboxUI created successfully")
        
        # Clean up
        app.quit()
        return True
        
    except Exception as e:
        print(f"[FAIL] UI creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("ChatterboxTTS Desktop UI Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\nSome imports failed. Cannot proceed with UI test.")
        return 1
    
    # Test UI creation
    if not test_ui_creation():
        print("\nUI creation failed.")
        return 1
    
    print("\n" + "=" * 50)
    print("[SUCCESS] All tests passed!")
    print("The PyQt6 desktop application should work.")
    print("To run the full app:")
    print("  Windows: run_desktop.bat")
    print("  Linux/WSL: python run_desktop.py")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())