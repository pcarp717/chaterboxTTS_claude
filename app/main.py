"""
ChatterboxTTS Desktop Application

A local text-to-speech application using Resemble AI's Chatterbox TTS model.
Designed for Windows 11 with NVIDIA RTX 3080 optimization.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import ChatterboxUI


def main():
    """Main entry point for the application."""
    try:
        print("=" * 60)
        print("ChatterboxTTS Desktop")
        print("   High-quality local text-to-speech generation")
        print("=" * 60)
    except UnicodeEncodeError:
        print("=" * 60)
        print("ChatterboxTTS Desktop")
        print("   High-quality local text-to-speech generation")
        print("=" * 60)
    
    # Create and launch UI
    return ChatterboxUI.create_and_launch()


if __name__ == "__main__":
    main()