import gradio as gr
import torch
import os
import time
from datetime import datetime
from model_manager import ModelManager
from tts_service import TTSService


class ChatterboxUI:
    """Gradio UI for ChatterboxTTS Desktop."""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.tts_service = TTSService(self.model_manager)
        self.current_audio = None
        self.current_sr = None
        
    def generate_speech(self, text: str, exaggeration: float, cfg_weight: float, 
                       progress=gr.Progress()) -> tuple:
        """Generate speech and return audio for Gradio player."""
        try:
            if not text.strip():
                return None, "Please enter some text to generate speech."
            
            progress(0, desc="Starting generation...")
            
            # Generate audio
            start_time = time.time()
            audio_tensor, sample_rate = self.tts_service.generate_speech(
                text, exaggeration=exaggeration, cfg_weight=cfg_weight
            )
            
            generation_time = time.time() - start_time
            
            # Convert to numpy for Gradio
            audio_np = audio_tensor.squeeze().cpu().numpy()
            
            # Store current audio
            self.current_audio = audio_tensor
            self.current_sr = sample_rate
            
            progress(1.0, desc="Complete!")
            
            # Calculate stats
            duration = len(audio_np) / sample_rate
            speed_ratio = duration / generation_time if generation_time > 0 else 0
            
            status = (f"✅ Generated {duration:.1f}s audio in {generation_time:.1f}s "
                     f"({speed_ratio:.1f}x real-time)")
            
            return (sample_rate, audio_np), status
            
        except Exception as e:
            return None, f"❌ Error: {str(e)}"
    
    def export_audio(self, format_choice: str) -> tuple:
        """Export current audio to file."""
        try:
            if self.current_audio is None:
                return None, "No audio to export. Generate speech first."
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chatterbox_output_{timestamp}.{format_choice.lower()}"
            filepath = os.path.join("outputs", filename)
            
            # Ensure outputs directory exists
            os.makedirs("outputs", exist_ok=True)
            
            # Save audio
            saved_path = self.tts_service.save_audio(
                self.current_audio, self.current_sr, filepath, format_choice
            )
            
            return saved_path, f"✅ Audio exported to: {filename}"
            
        except Exception as e:
            return None, f"❌ Export failed: {str(e)}"
    
    def get_memory_info(self) -> str:
        """Get current memory usage information."""
        # Force refresh of model status
        stats = self.model_manager.get_memory_stats()
        
        info_lines = [
            f"🖥️ **System Status**",
            f"• Model: {'Loaded' if stats['model_loaded'] else 'Not loaded'}",
            f"• Device: {stats['device'].upper()}",
            f"• RAM Usage: {stats.get('ram_usage_percent', 0):.1f}%",
        ]
        
        if stats['device'] == 'cuda':
            if 'vram_used' in stats:
                info_lines.extend([
                    f"• VRAM: {stats['vram_used']:.1f}GB / {stats['vram_total']:.1f}GB ({stats['vram_usage_percent']:.1f}%)",
                ])
            else:
                info_lines.extend([
                    f"• CUDA Memory: {stats.get('cuda_memory_allocated', 0):.1f}GB allocated",
                ])
        
        if stats['last_used']:
            time_since = time.time() - stats['last_used']
            info_lines.append(f"• Last used: {time_since:.0f}s ago")
        
        return "\n".join(info_lines)
    
    def create_interface(self) -> gr.Blocks:
        """Create and return the Gradio interface."""
        
        with gr.Blocks(
            title="ChatterboxTTS Desktop",
            theme=gr.themes.Soft(),
            css=".gradio-container {max-width: 1200px !important}"
        ) as interface:
            
            gr.Markdown(
                "# 🗣️ ChatterboxTTS Desktop\n"
                "High-quality local text-to-speech generation with voice cloning capabilities."
            )
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Input Section
                    gr.Markdown("## 📝 Text Input")
                    text_input = gr.Textbox(
                        label="Text to Generate (max 10,000 characters)",
                        placeholder="Enter the text you want to convert to speech...",
                        lines=8,
                        max_lines=12,
                        show_label=True
                    )
                    
                    char_count = gr.Markdown("**Characters: 0 / 10,000**")
                    
                    # Update character count
                    text_input.change(
                        fn=lambda text: f"**Characters: {len(text)} / 10,000**",
                        inputs=[text_input],
                        outputs=[char_count]
                    )
                    
                    # Voice Settings
                    gr.Markdown("## 🎛️ Voice Settings")
                    with gr.Row():
                        exaggeration = gr.Slider(
                            minimum=0.0, maximum=1.0, value=0.5, step=0.1,
                            label="Exaggeration (Emotion Level)",
                            info="Higher values make speech more expressive"
                        )
                        cfg_weight = gr.Slider(
                            minimum=0.0, maximum=1.0, value=0.5, step=0.1,
                            label="CFG Weight (Generation Control)",
                            info="Higher values follow text more closely"
                        )
                    
                    # Generate Button
                    generate_btn = gr.Button(
                        "🎤 Generate Speech", 
                        variant="primary", 
                        size="lg"
                    )
                
                with gr.Column(scale=1):
                    # System Info
                    gr.Markdown("## 📊 System Status")
                    memory_info = gr.Markdown(self.get_memory_info())
                    
                    # Refresh button
                    refresh_btn = gr.Button("🔄 Refresh", size="sm")
                    refresh_btn.click(
                        fn=self.get_memory_info,
                        outputs=[memory_info]
                    )
            
            # Status and Results
            status_text = gr.Markdown("**Ready to generate speech.**")
            
            # Audio Player
            gr.Markdown("## 🔊 Generated Audio")
            audio_player = gr.Audio(
                label="Generated Speech",
                type="numpy",
                show_download_button=True,
                interactive=False
            )
            
            # Export Section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## 💾 Export Audio")
                    format_choice = gr.Radio(
                        choices=["WAV"], 
                        value="WAV",
                        label="Export Format",
                        info="High-quality 48kHz WAV format"
                    )
                    export_btn = gr.Button("📁 Export Audio", variant="secondary")
                    download_file = gr.File(label="Download", visible=False)
            
            # Wire up the interface
            generate_btn.click(
                fn=self.generate_speech,
                inputs=[text_input, exaggeration, cfg_weight],
                outputs=[audio_player, status_text],
                show_progress=True
            ).then(
                fn=self.get_memory_info,
                outputs=[memory_info]
            )
            
            export_btn.click(
                fn=self.export_audio,
                inputs=[format_choice],
                outputs=[download_file, status_text]
            )
            
            # Manual refresh only - auto-refresh removed due to Gradio compatibility
            # Users can click the refresh button to update memory info
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        
        # Default launch settings
        launch_kwargs = {
            "server_name": "127.0.0.1",
            "server_port": 7860,
            "share": False,
            "inbrowser": True,
            **kwargs
        }
        
        print("🚀 Starting ChatterboxTTS Desktop...")
        print(f"📱 Web interface will open at: http://{launch_kwargs['server_name']}:{launch_kwargs['server_port']}")
        
        try:
            interface.launch(**launch_kwargs)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.model_manager.shutdown()
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            self.model_manager.shutdown()