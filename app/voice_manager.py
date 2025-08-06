import os
import json
import librosa
import soundfile as sf
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path


class VoiceProfile:
    """Represents a custom voice profile."""
    
    def __init__(self, name: str, file_path: str, created_date: str = None):
        self.name = name
        self.file_path = file_path
        self.created_date = created_date or datetime.now().isoformat()
        self.duration = None
        self.sample_rate = None
        self._load_audio_info()
    
    def _load_audio_info(self):
        """Load audio file information."""
        try:
            if os.path.exists(self.file_path):
                audio, sr = librosa.load(self.file_path, sr=None)
                self.duration = len(audio) / sr
                self.sample_rate = sr
        except Exception:
            self.duration = None
            self.sample_rate = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "created_date": self.created_date,
            "duration": self.duration,
            "sample_rate": self.sample_rate
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VoiceProfile':
        """Create VoiceProfile from dictionary."""
        profile = cls(data["name"], data["file_path"], data.get("created_date"))
        profile.duration = data.get("duration")
        profile.sample_rate = data.get("sample_rate")
        return profile


class VoiceManager:
    """Manages custom voice profiles and cloning functionality."""
    
    def __init__(self, voices_dir: str = "voices", max_voices: int = 10):
        self.voices_dir = Path(voices_dir)
        self.max_voices = max_voices
        self.profiles_file = self.voices_dir / "profiles.json"
        self.voices: Dict[str, VoiceProfile] = {}
        
        # Create directories
        self.voices_dir.mkdir(exist_ok=True)
        
        # Load existing profiles
        self._load_profiles()
    
    def _load_profiles(self):
        """Load voice profiles from JSON file."""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    for voice_data in data.get("voices", []):
                        profile = VoiceProfile.from_dict(voice_data)
                        self.voices[profile.name] = profile
            except Exception as e:
                print(f"Warning: Could not load voice profiles: {e}")
    
    def _save_profiles(self):
        """Save voice profiles to JSON file."""
        try:
            data = {
                "voices": [profile.to_dict() for profile in self.voices.values()]
            }
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save voice profiles: {e}")
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate uploaded audio file for voice cloning.
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        try:
            # Load audio file
            audio, sr = librosa.load(file_path, sr=None)
            duration = len(audio) / sr
            
            # Check duration (7-20 seconds as per requirements)
            if duration < 7:
                return False, f"Audio too short ({duration:.1f}s). Minimum 7 seconds required."
            if duration > 20:
                return False, f"Audio too long ({duration:.1f}s). Maximum 20 seconds allowed."
            
            # Check if audio has content (not just silence)
            rms_energy = np.sqrt(np.mean(audio**2))
            if rms_energy < 0.01:  # Very quiet threshold
                return False, "Audio appears to be mostly silence. Please provide clear speech."
            
            # Check sample rate (should be reasonable)
            if sr < 8000:
                return False, f"Sample rate too low ({sr} Hz). Minimum 8kHz required."
            
            return True, f"✅ Valid audio: {duration:.1f}s at {sr} Hz"
            
        except Exception as e:
            return False, f"Could not process audio file: {str(e)}"
    
    def add_voice(self, name: str, source_file: str) -> Tuple[bool, str]:
        """
        Add a new voice profile.
        
        Args:
            name: Display name for the voice
            source_file: Path to the source audio file
            
        Returns:
            Tuple of (success, message)
        """
        # Check if we have room for more voices
        if len(self.voices) >= self.max_voices:
            return False, f"Maximum {self.max_voices} voices allowed. Delete a voice first."
        
        # Check if name already exists
        if name in self.voices:
            return False, f"Voice '{name}' already exists. Choose a different name."
        
        # Validate the audio file
        is_valid, message = self.validate_audio_file(source_file)
        if not is_valid:
            return False, message
        
        try:
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name}_{timestamp}.wav"
            target_path = self.voices_dir / filename
            
            # Convert and save as WAV (standardize format)
            audio, sr = librosa.load(source_file, sr=48000)  # Standardize to 48kHz
            sf.write(target_path, audio, sr)
            
            # Create profile
            profile = VoiceProfile(name, str(target_path))
            self.voices[name] = profile
            
            # Save profiles
            self._save_profiles()
            
            return True, f"✅ Voice '{name}' added successfully ({profile.duration:.1f}s)"
            
        except Exception as e:
            return False, f"Failed to add voice: {str(e)}"
    
    def delete_voice(self, name: str) -> Tuple[bool, str]:
        """Delete a voice profile and its audio file."""
        if name not in self.voices:
            return False, f"Voice '{name}' not found."
        
        try:
            profile = self.voices[name]
            
            # Delete audio file if it exists
            if os.path.exists(profile.file_path):
                os.remove(profile.file_path)
            
            # Remove from profiles
            del self.voices[name]
            self._save_profiles()
            
            return True, f"✅ Voice '{name}' deleted successfully."
            
        except Exception as e:
            return False, f"Failed to delete voice: {str(e)}"
    
    def get_voice_list(self) -> List[str]:
        """Get list of available voice names."""
        return ["Default"] + list(self.voices.keys())
    
    def get_voice_info(self, name: str) -> Optional[Dict]:
        """Get detailed information about a voice."""
        if name == "Default":
            return {
                "name": "Default",
                "type": "built-in",
                "description": "High-quality default voice"
            }
        
        if name in self.voices:
            profile = self.voices[name]
            return {
                "name": profile.name,
                "type": "custom",
                "duration": profile.duration,
                "sample_rate": profile.sample_rate,
                "created_date": profile.created_date,
                "file_path": profile.file_path
            }
        
        return None
    
    def get_voice_sample_path(self, name: str) -> Optional[str]:
        """Get the audio file path for a voice (for cloning)."""
        if name == "Default" or name not in self.voices:
            return None
        return self.voices[name].file_path