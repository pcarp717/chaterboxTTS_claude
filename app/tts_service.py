import re
import torch
import torchaudio as ta
import numpy as np
from typing import List, Tuple
from model_manager import ModelManager


class TTSService:
    """Handles text processing and TTS generation."""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.max_chunk_length = 300  # Characters
        
    def generate_speech(self, text: str, voice_profile: str = "default", 
                       exaggeration: float = 0.5, cfg_weight: float = 0.5) -> Tuple[torch.Tensor, int]:
        """
        Generate speech from text.
        
        Args:
            text: Input text (max 10,000 characters)
            voice_profile: Voice to use (currently only "default" supported)
            exaggeration: Emotion control (0.0 to 1.0)
            cfg_weight: Generation control (0.0 to 1.0)
            
        Returns:
            Tuple of (audio_tensor, sample_rate)
        """
        if len(text) > 10000:
            raise ValueError("Text exceeds 10,000 character limit")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Get model
        model = self.model_manager.get_model()
        
        # Split text into chunks if needed
        chunks = self._chunk_text(text) if len(text) > self.max_chunk_length else [text]
        
        # Generate audio for each chunk
        audio_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"Generating chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
            
            # Generate audio
            wav = model.generate(
                chunk, 
                exaggeration=exaggeration, 
                cfg_weight=cfg_weight
            )
            audio_chunks.append(wav)
        
        # Concatenate chunks
        if len(audio_chunks) == 1:
            final_audio = audio_chunks[0]
        else:
            final_audio = torch.cat(audio_chunks, dim=-1)
        
        return final_audio, model.sr
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks at sentence boundaries.
        
        Prioritizes keeping sentences intact while staying under max_chunk_length.
        """
        # Split on sentence endings
        sentences = re.split(r'([.!?]+)', text)
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + punctuation
            
            # If adding this sentence would exceed limit, start new chunk
            if current_chunk and len(current_chunk) + len(full_sentence) > self.max_chunk_length:
                chunks.append(current_chunk.strip())
                current_chunk = full_sentence
            else:
                current_chunk += full_sentence
        
        # Add remaining text
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Handle edge case where single sentence is too long
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.max_chunk_length:
                final_chunks.append(chunk)
            else:
                # Split long chunk at word boundaries
                words = chunk.split()
                sub_chunk = ""
                for word in words:
                    if len(sub_chunk) + len(word) + 1 > self.max_chunk_length:
                        if sub_chunk:
                            final_chunks.append(sub_chunk.strip())
                        sub_chunk = word
                    else:
                        sub_chunk += " " + word if sub_chunk else word
                if sub_chunk:
                    final_chunks.append(sub_chunk.strip())
        
        return final_chunks
    
    def save_audio(self, audio_tensor: torch.Tensor, sample_rate: int, 
                   filepath: str, format: str = "wav") -> str:
        """
        Save audio tensor to file.
        
        Args:
            audio_tensor: Audio data
            sample_rate: Sample rate
            filepath: Output file path
            format: Output format ("wav" or "mp3")
            
        Returns:
            Path to saved file
        """
        # Ensure audio is in correct format (2D tensor with channels first)
        if audio_tensor.dim() == 1:
            audio_tensor = audio_tensor.unsqueeze(0)  # Add channel dimension
        
        # Save audio
        if format.lower() == "wav":
            ta.save(filepath, audio_tensor, sample_rate)
        elif format.lower() == "mp3":
            # For MP3, we might need additional setup, but start with WAV
            # This would require additional dependencies like ffmpeg
            raise NotImplementedError("MP3 export not yet implemented")
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return filepath