"""
ChatterboxTTS Desktop Application

A local text-to-speech application using Resemble AI's Chatterbox TTS model.
Designed for Windows 11 with NVIDIA RTX 3080 optimization.
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import ChatterboxUI


def main():
    """Main entry point for the application."""
    print("=" * 60)
    print("🗣️  ChatterboxTTS Desktop")
    print("   High-quality local text-to-speech generation")
    print("=" * 60)
    
    # Create and launch UI
    app = ChatterboxUI()
    app.launch()


if __name__ == "__main__":
    main()