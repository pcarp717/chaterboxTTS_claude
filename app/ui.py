import sys
import os
import time
import threading
import tempfile
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QLabel, QPushButton, 
                            QSlider, QComboBox, QGroupBox, QProgressBar, 
                            QFileDialog, QMessageBox, QSplitter, QTabWidget,
                            QLineEdit, QSpacerItem, QSizePolicy, QFrame,
                            QDoubleSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
import torch
import pygame
import numpy as np
from model_manager import ModelManager
from tts_service import TTSService
from voice_manager import VoiceManager


class AudioPlayer:
    """Audio player using pygame for playback with speed control."""
    
    def __init__(self):
        pygame.mixer.init(frequency=48000, size=-16, channels=1, buffer=2048)
        self.is_playing = False
        self.is_paused = False
        self.playback_speed = 1.0
        self.current_file = None
        self.original_audio = None
        self.original_sample_rate = None
        
    def load_audio(self, audio_tensor, sample_rate):
        """Load audio tensor for playback."""
        self.original_audio = audio_tensor.squeeze().cpu().numpy()
        self.original_sample_rate = sample_rate
        
    def set_playback_speed(self, speed):
        """Set playback speed (0.5 to 2.0)."""
        self.playback_speed = max(0.5, min(2.0, speed))
        
    def play(self, auto_play=True):
        """Play audio with current speed settings."""
        if self.original_audio is None:
            return False
            
        try:
            # Apply speed change by resampling
            if self.playback_speed != 1.0:
                # Simple speed change by sample rate adjustment
                new_sample_rate = int(self.original_sample_rate * self.playback_speed)
                audio_to_play = self.original_audio
            else:
                new_sample_rate = self.original_sample_rate
                audio_to_play = self.original_audio
                
            # Convert to int16 for pygame
            audio_int16 = (audio_to_play * 32767).astype(np.int16)
            
            # Create a temporary file for pygame
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()
            
            # Save to temporary WAV file
            import scipy.io.wavfile as wavfile
            wavfile.write(temp_path, new_sample_rate, audio_int16)
            
            # Load and play with pygame
            pygame.mixer.music.load(temp_path)
            if auto_play:
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
            
            self.current_file = temp_path
            return True
            
        except Exception as e:
            print(f"Audio playback error: {e}")
            return False
    
    def pause(self):
        """Pause playback."""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            
    def resume(self):
        """Resume playback."""
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            
    def stop(self):
        """Stop playback."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        
    def is_busy(self):
        """Check if audio is currently playing."""
        return pygame.mixer.music.get_busy()
        
    def cleanup(self):
        """Clean up temporary files."""
        if self.current_file and os.path.exists(self.current_file):
            try:
                os.unlink(self.current_file)
            except:
                pass


class TTSWorker(QThread):
    """Worker thread for TTS generation to prevent UI freezing."""
    finished = pyqtSignal(object, int, str)  # audio_tensor, sample_rate, status
    error = pyqtSignal(str)
    
    def __init__(self, tts_service, text, voice_profile, exaggeration, cfg_weight):
        super().__init__()
        self.tts_service = tts_service
        self.text = text
        self.voice_profile = voice_profile
        self.exaggeration = exaggeration
        self.cfg_weight = cfg_weight
        
    def run(self):
        try:
            start_time = time.time()
            audio_tensor, sample_rate = self.tts_service.generate_speech(
                self.text, self.voice_profile, self.exaggeration, self.cfg_weight
            )
            generation_time = time.time() - start_time
            
            # Calculate stats
            duration = len(audio_tensor.squeeze()) / sample_rate
            speed_ratio = duration / generation_time if generation_time > 0 else 0
            
            status = (f"✅ Generated {duration:.1f}s audio in {generation_time:.1f}s "
                     f"({speed_ratio:.1f}x real-time)")
            
            self.finished.emit(audio_tensor, sample_rate, status)
        except Exception as e:
            self.error.emit(f"❌ Error: {str(e)}")


class ChatterboxUI(QMainWindow):
    """Native PyQt6 Desktop UI for ChatterboxTTS."""
    
    def __init__(self, app):
        super().__init__()
        self.app = app  # Store reference to QApplication
        self.model_manager = ModelManager()
        self.voice_manager = VoiceManager()
        self.tts_service = TTSService(self.model_manager, self.voice_manager)
        self.current_audio = None
        self.current_sr = None
        self.tts_worker = None
        self.audio_player = AudioPlayer()
        
        self.init_ui()
        self.setup_timers()
        
    def init_ui(self):
        """Initialize the user interface."""
        try:
            self.setWindowTitle("🗣️ ChatterboxTTS Desktop")
        except UnicodeEncodeError:
            self.setWindowTitle("ChatterboxTTS Desktop")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Main controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - System info and voice management
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([800, 400])
        
    def create_left_panel(self):
        """Create the main control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        try:
            title_label = QLabel("🗣️ ChatterboxTTS Desktop")
        except UnicodeEncodeError:
            title_label = QLabel("ChatterboxTTS Desktop")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("High-quality local text-to-speech generation")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: gray;")
        layout.addWidget(subtitle_label)
        
        # Text input section
        text_group = QGroupBox("Text Input")
        text_layout = QVBoxLayout(text_group)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter the text you want to convert to speech...")
        self.text_input.textChanged.connect(self.update_char_count)
        text_layout.addWidget(self.text_input)
        
        self.char_count_label = QLabel("Characters: 0 / 10,000")
        text_layout.addWidget(self.char_count_label)
        
        layout.addWidget(text_group)
        
        # Voice selection
        voice_group = QGroupBox("Voice Selection")
        voice_layout = QVBoxLayout(voice_group)
        
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(self.voice_manager.get_voice_list())
        self.voice_combo.currentTextChanged.connect(self.update_voice_info)
        voice_layout.addWidget(self.voice_combo)
        
        self.voice_info_label = QLabel("High-quality default voice")
        self.voice_info_label.setWordWrap(True)
        self.voice_info_label.setStyleSheet("""
            padding: 10px; 
            background-color: palette(alternate-base); 
            border: 1px solid palette(mid);
            border-radius: 5px;
            color: palette(text);
        """)
        voice_layout.addWidget(self.voice_info_label)
        
        layout.addWidget(voice_group)
        
        # Voice settings
        settings_group = QGroupBox("Voice Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Exaggeration slider
        exag_layout = QHBoxLayout()
        exag_layout.addWidget(QLabel("Exaggeration:"))
        self.exaggeration_slider = QSlider(Qt.Orientation.Horizontal)
        self.exaggeration_slider.setRange(0, 10)
        self.exaggeration_slider.setValue(5)
        self.exaggeration_slider.valueChanged.connect(self.update_exaggeration_label)
        exag_layout.addWidget(self.exaggeration_slider)
        self.exaggeration_label = QLabel("0.5")
        exag_layout.addWidget(self.exaggeration_label)
        settings_layout.addLayout(exag_layout)
        
        # CFG Weight slider  
        cfg_layout = QHBoxLayout()
        cfg_layout.addWidget(QLabel("CFG Weight:"))
        self.cfg_weight_slider = QSlider(Qt.Orientation.Horizontal)
        self.cfg_weight_slider.setRange(0, 10)
        self.cfg_weight_slider.setValue(5)
        self.cfg_weight_slider.valueChanged.connect(self.update_cfg_weight_label)
        cfg_layout.addWidget(self.cfg_weight_slider)
        self.cfg_weight_label = QLabel("0.5")
        cfg_layout.addWidget(self.cfg_weight_label)
        settings_layout.addLayout(cfg_layout)
        
        layout.addWidget(settings_group)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Speech")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_speech)
        layout.addWidget(self.generate_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to generate speech.")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            padding: 10px; 
            background-color: palette(alternate-base); 
            border: 1px solid palette(mid);
            border-radius: 5px;
            color: palette(text);
        """)
        layout.addWidget(self.status_label)
        
        # Export section
        export_group = QGroupBox("Export Audio")
        export_layout = QHBoxLayout(export_group)
        
        self.export_btn = QPushButton("Export as WAV")
        self.export_btn.clicked.connect(self.export_audio)
        self.export_btn.setEnabled(False)
        export_layout.addWidget(self.export_btn)
        
        layout.addWidget(export_group)
        
        # Audio playback section
        playback_group = QGroupBox("Audio Playback")
        playback_layout = QVBoxLayout(playback_group)
        
        # Playback controls
        controls_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_audio)
        self.play_btn.setEnabled(False)
        controls_layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_audio)
        self.pause_btn.setEnabled(False)
        controls_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_audio)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        playback_layout.addLayout(controls_layout)
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Playback Speed:"))
        
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.5, 2.0)
        self.speed_spinbox.setValue(1.0)
        self.speed_spinbox.setSingleStep(0.1)
        self.speed_spinbox.setDecimals(1)
        self.speed_spinbox.setSuffix("x")
        self.speed_spinbox.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_spinbox)
        
        speed_layout.addStretch()
        playback_layout.addLayout(speed_layout)
        
        # Audio info
        self.audio_info_label = QLabel("No audio loaded")
        self.audio_info_label.setStyleSheet("""
            padding: 8px; 
            background-color: palette(alternate-base); 
            border: 1px solid palette(mid);
            border-radius: 3px;
            color: palette(text);
            font-size: 11px;
        """)
        playback_layout.addWidget(self.audio_info_label)
        
        layout.addWidget(playback_group)
        
        return panel
        
    def create_right_panel(self):
        """Create the right panel with tabs for system info and voice management."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # System Status tab
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        
        system_group = QGroupBox("System Status")
        system_group_layout = QVBoxLayout(system_group)
        
        self.memory_info_label = QLabel(self.get_memory_info())
        self.memory_info_label.setWordWrap(True)
        self.memory_info_label.setStyleSheet("""
            padding: 10px; 
            font-family: monospace; 
            background-color: palette(alternate-base); 
            border: 1px solid palette(mid);
            border-radius: 5px;
            color: palette(text);
        """)
        system_group_layout.addWidget(self.memory_info_label)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_memory_info)
        system_group_layout.addWidget(refresh_btn)
        
        system_layout.addWidget(system_group)
        system_layout.addStretch()
        
        tab_widget.addTab(system_tab, "System")
        
        # Voice Management tab
        voice_tab = QWidget()
        voice_layout = QVBoxLayout(voice_tab)
        
        voice_mgmt_group = QGroupBox("Voice Management")
        voice_mgmt_layout = QVBoxLayout(voice_mgmt_group)
        
        # Add voice section
        add_voice_group = QGroupBox("Add New Voice")
        add_voice_layout = QVBoxLayout(add_voice_group)
        
        add_voice_layout.addWidget(QLabel("Upload a 7-20 second clear audio sample (WAV or MP3)"))
        
        self.voice_name_input = QLineEdit()
        self.voice_name_input.setPlaceholderText("e.g., My Voice, John's Voice")
        add_voice_layout.addWidget(QLabel("Voice Name:"))
        add_voice_layout.addWidget(self.voice_name_input)
        
        self.select_file_btn = QPushButton("Select Audio File")
        self.select_file_btn.clicked.connect(self.select_voice_file)
        add_voice_layout.addWidget(self.select_file_btn)
        
        self.selected_file_label = QLabel("No file selected")
        self.selected_file_label.setStyleSheet("color: palette(disabled-text); font-style: italic;")
        add_voice_layout.addWidget(self.selected_file_label)
        
        self.add_voice_btn = QPushButton("Add Voice")
        self.add_voice_btn.clicked.connect(self.add_voice)
        add_voice_layout.addWidget(self.add_voice_btn)
        
        voice_mgmt_layout.addWidget(add_voice_group)
        
        # Delete voice section
        delete_voice_group = QGroupBox("Delete Voice")
        delete_voice_layout = QVBoxLayout(delete_voice_group)
        
        self.delete_voice_combo = QComboBox()
        self.update_delete_voice_combo()
        delete_voice_layout.addWidget(QLabel("Select Voice to Delete:"))
        delete_voice_layout.addWidget(self.delete_voice_combo)
        
        self.delete_voice_btn = QPushButton("Delete Voice")
        self.delete_voice_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_voice_btn.clicked.connect(self.delete_voice)
        delete_voice_layout.addWidget(self.delete_voice_btn)
        
        voice_mgmt_layout.addWidget(delete_voice_group)
        
        # Voice management status
        self.voice_status_label = QLabel("")
        self.voice_status_label.setWordWrap(True)
        self.voice_status_label.setStyleSheet("""
            padding: 10px; 
            background-color: palette(alternate-base); 
            border: 1px solid palette(mid);
            border-radius: 5px;
            color: palette(text);
        """)
        voice_mgmt_layout.addWidget(self.voice_status_label)
        
        voice_layout.addWidget(voice_mgmt_group)
        voice_layout.addStretch()
        
        tab_widget.addTab(voice_tab, "Voice Management")
        
        layout.addWidget(tab_widget)
        
        return panel
        
    def setup_timers(self):
        """Setup timers for periodic updates."""
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.refresh_memory_info)
        self.memory_timer.start(5000)  # Update every 5 seconds
        
        # Timer to check audio playback status
        self.audio_timer = QTimer()
        self.audio_timer.timeout.connect(self.check_audio_status)
        self.audio_timer.start(500)  # Check every 500ms
        
    def update_char_count(self):
        """Update character count display."""
        text = self.text_input.toPlainText()
        count = len(text)
        self.char_count_label.setText(f"Characters: {count} / 10,000")
        
        if count > 10000:
            self.char_count_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.char_count_label.setStyleSheet("")
    
    def update_voice_info(self):
        """Update voice information display."""
        voice_name = self.voice_combo.currentText()
        info = self.get_voice_info(voice_name)
        self.voice_info_label.setText(info)
        
    def update_exaggeration_label(self, value):
        """Update exaggeration slider label."""
        self.exaggeration_label.setText(f"{value/10:.1f}")
        
    def update_cfg_weight_label(self, value):
        """Update CFG weight slider label.""" 
        self.cfg_weight_label.setText(f"{value/10:.1f}")
        
    def generate_speech(self):
        """Generate speech using TTS worker thread."""
        text = self.text_input.toPlainText()
        if not text.strip():
            self.update_status("Please enter some text to generate speech.", "error")
            return
            
        if len(text) > 10000:
            self.update_status("Text exceeds 10,000 character limit.", "error") 
            return
            
        # Disable generate button and show progress
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Generating...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Get settings
        voice_profile = self.voice_combo.currentText()
        exaggeration = self.exaggeration_slider.value() / 10.0
        cfg_weight = self.cfg_weight_slider.value() / 10.0
        
        # Start TTS generation in worker thread
        self.tts_worker = TTSWorker(self.tts_service, text, voice_profile, exaggeration, cfg_weight)
        self.tts_worker.finished.connect(self.on_tts_finished)
        self.tts_worker.error.connect(self.on_tts_error)
        self.tts_worker.start()
        
        self.update_status("Generating speech...", "info")
        
    def on_tts_finished(self, audio_tensor, sample_rate, status):
        """Handle TTS generation completion."""
        self.current_audio = audio_tensor
        self.current_sr = sample_rate
        
        # Re-enable UI
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Speech")
        self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)
        
        # Load audio into player and auto-play
        self.audio_player.load_audio(audio_tensor, sample_rate)
        duration = len(audio_tensor.squeeze()) / sample_rate
        self.audio_info_label.setText(f"Duration: {duration:.1f}s | Sample Rate: {sample_rate} Hz")
        
        # Enable playback controls
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        
        # Auto-play the generated audio
        if self.audio_player.play(auto_play=True):
            self.play_btn.setText("Playing...")
            self.play_btn.setEnabled(False)
        
        self.update_status(status, "success")
        self.refresh_memory_info()
        
    def on_tts_error(self, error_message):
        """Handle TTS generation error."""
        # Re-enable UI
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Speech")
        self.progress_bar.setVisible(False)
        
        self.update_status(error_message, "error")
        
    def export_audio(self):
        """Export current audio to file."""
        if self.current_audio is None:
            self.update_status("No audio to export. Generate speech first.", "error")
            return
            
        # Get save location
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Audio",
            f"chatterbox_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
            "WAV files (*.wav)"
        )
        
        if filename:
            try:
                saved_path = self.tts_service.save_audio(
                    self.current_audio, self.current_sr, filename, "wav"
                )
                self.update_status(f"✅ Audio exported to: {os.path.basename(filename)}", "success")
            except Exception as e:
                self.update_status(f"❌ Export failed: {str(e)}", "error")
                
    def select_voice_file(self):
        """Select audio file for voice cloning."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio Sample",
            "",
            "Audio files (*.wav *.mp3)"
        )
        
        if filename:
            self.selected_file_path = filename
            self.selected_file_label.setText(f"Selected: {os.path.basename(filename)}")
            self.selected_file_label.setStyleSheet("color: green;")
        else:
            self.selected_file_path = None
            self.selected_file_label.setText("No file selected")
            self.selected_file_label.setStyleSheet("color: gray; font-style: italic;")
    
    def add_voice(self):
        """Add a new custom voice."""
        voice_name = self.voice_name_input.text().strip()
        
        if not voice_name:
            self.update_voice_status("❌ Please enter a voice name.", "error")
            return
            
        if not hasattr(self, 'selected_file_path') or self.selected_file_path is None:
            self.update_voice_status("❌ Please select an audio file.", "error")
            return
        
        try:
            # Create a mock file object with the path
            class MockFile:
                def __init__(self, path):
                    self.name = path
                    
            mock_file = MockFile(self.selected_file_path)
            success, message = self.voice_manager.add_voice(voice_name, mock_file.name)
            
            if success:
                # Update voice dropdowns
                voice_choices = self.voice_manager.get_voice_list()
                self.voice_combo.clear()
                self.voice_combo.addItems(voice_choices)
                self.update_delete_voice_combo()
                
                # Clear inputs
                self.voice_name_input.clear()
                self.selected_file_path = None
                self.selected_file_label.setText("No file selected")
                self.selected_file_label.setStyleSheet("color: gray; font-style: italic;")
                
                self.update_voice_status(message, "success")
            else:
                self.update_voice_status(message, "error")
                
        except Exception as e:
            self.update_voice_status(f"❌ Error adding voice: {str(e)}", "error")
    
    def delete_voice(self):
        """Delete a custom voice."""
        voice_to_delete = self.delete_voice_combo.currentText()
        
        if not voice_to_delete:
            self.update_voice_status("❌ Please select a voice to delete.", "error")
            return
            
        if voice_to_delete == "Default":
            self.update_voice_status("❌ Cannot delete the default voice.", "error")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            'Delete Voice', 
            f'Are you sure you want to delete "{voice_to_delete}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success, message = self.voice_manager.delete_voice(voice_to_delete)
                
                if success:
                    # Update voice dropdowns
                    voice_choices = self.voice_manager.get_voice_list()
                    self.voice_combo.clear()
                    self.voice_combo.addItems(voice_choices)
                    self.voice_combo.setCurrentText("Default")
                    self.update_delete_voice_combo()
                    
                    self.update_voice_status(message, "success")
                else:
                    self.update_voice_status(message, "error")
                    
            except Exception as e:
                self.update_voice_status(f"❌ Error deleting voice: {str(e)}", "error")
    
    def update_delete_voice_combo(self):
        """Update the delete voice combo box."""
        voices = [v for v in self.voice_manager.get_voice_list() if v != "Default"]
        self.delete_voice_combo.clear()
        if voices:
            self.delete_voice_combo.addItems(voices)
            self.delete_voice_combo.setCurrentIndex(0)
        
    def get_memory_info(self):
        """Get current memory usage information."""
        stats = self.model_manager.get_memory_stats()
        
        info_lines = [
            "System Status",
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
        
    def refresh_memory_info(self):
        """Refresh memory info display."""
        self.memory_info_label.setText(self.get_memory_info())
        
    def get_voice_info(self, voice_name):
        """Get information about a selected voice."""
        if not voice_name:
            return "No voice selected."
        
        info = self.voice_manager.get_voice_info(voice_name)
        if info is None:
            return f"Voice '{voice_name}' not found."
        
        if info["type"] == "built-in":
            return f"{info['name']}\n{info['description']}"
        else:
            duration = info.get("duration", 0)
            sample_rate = info.get("sample_rate", 0)
            created_date = info.get("created_date", "Unknown")
            
            return (f"{info['name']} (Custom Voice)\n"
                   f"Duration: {duration:.1f}s\n"
                   f"Sample Rate: {sample_rate} Hz\n"
                   f"Created: {created_date[:10]}")
                   
    def update_status(self, message, status_type="info"):
        """Update status label with styling based on type."""
        self.status_label.setText(message)
        
        if status_type == "error":
            self.status_label.setStyleSheet("padding: 10px; background-color: #ffebee; color: #c62828; border-radius: 5px;")
        elif status_type == "success":
            self.status_label.setStyleSheet("padding: 10px; background-color: #e8f5e8; color: #2e7d32; border-radius: 5px;")
        else:  # info
            self.status_label.setStyleSheet("padding: 10px; background-color: #e3f2fd; color: #1565c0; border-radius: 5px;")
            
    def update_voice_status(self, message, status_type="info"):
        """Update voice management status label."""
        self.voice_status_label.setText(message)
        
        if status_type == "error":
            self.voice_status_label.setStyleSheet("padding: 10px; background-color: #ffebee; color: #c62828; border-radius: 5px;")
        elif status_type == "success":
            self.voice_status_label.setStyleSheet("padding: 10px; background-color: #e8f5e8; color: #2e7d32; border-radius: 5px;")
        else:  # info
            self.voice_status_label.setStyleSheet("padding: 10px; background-color: #e3f2fd; color: #1565c0; border-radius: 5px;")
    
    def play_audio(self):
        """Play or resume audio playback."""
        if self.audio_player.original_audio is None:
            return
            
        if self.audio_player.is_paused:
            self.audio_player.resume()
            self.play_btn.setText("Playing...")
            self.play_btn.setEnabled(False)
        else:
            if self.audio_player.play(auto_play=True):
                self.play_btn.setText("Playing...")
                self.play_btn.setEnabled(False)
                
    def pause_audio(self):
        """Pause audio playback."""
        if self.audio_player.is_playing and not self.audio_player.is_paused:
            self.audio_player.pause()
            self.play_btn.setText("Resume")
            self.play_btn.setEnabled(True)
            
    def stop_audio(self):
        """Stop audio playback."""
        self.audio_player.stop()
        self.play_btn.setText("Play")
        self.play_btn.setEnabled(True)
        
    def on_speed_changed(self, speed):
        """Handle playback speed change."""
        self.audio_player.set_playback_speed(speed)
        # If currently playing, restart with new speed
        if self.audio_player.is_playing:
            was_playing = not self.audio_player.is_paused
            self.audio_player.stop()
            if was_playing and self.audio_player.play(auto_play=True):
                self.play_btn.setText("Playing...")
                self.play_btn.setEnabled(False)
                
    def check_audio_status(self):
        """Check audio playback status and update UI accordingly."""
        if self.audio_player.is_playing and not self.audio_player.is_paused:
            if not self.audio_player.is_busy():
                # Audio finished playing
                self.audio_player.is_playing = False
                self.play_btn.setText("Play")
                self.play_btn.setEnabled(True)
        
    def launch(self, **kwargs):
        """Launch the PyQt6 application."""
        # Show the main window
        self.show()
        
        try:
            print("🚀 ChatterboxTTS Desktop started!")
            print("💻 Native desktop application running")
        except UnicodeEncodeError:
            print("ChatterboxTTS Desktop started!")
            print("Native desktop application running")
        
        try:
            return self.app.exec()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.model_manager.shutdown()
        except Exception as e:
            print(f"Application error: {e}")
            self.model_manager.shutdown()
    
    @staticmethod
    def create_and_launch():
        """Static method to create QApplication and launch the UI."""
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("ChatterboxTTS Desktop")
        app.setApplicationDisplayName("ChatterboxTTS Desktop")
        app.setApplicationVersion("1.0")
        
        # Create and launch the UI
        ui = ChatterboxUI(app)
        return ui.launch()
            
    def closeEvent(self, event):
        """Handle application close event."""
        try:
            if hasattr(self, 'memory_timer'):
                self.memory_timer.stop()
            if hasattr(self, 'tts_worker') and self.tts_worker and self.tts_worker.isRunning():
                self.tts_worker.terminate()
                self.tts_worker.wait()
            if hasattr(self, 'audio_player'):
                self.audio_player.stop()
                self.audio_player.cleanup()
            self.model_manager.shutdown()
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        event.accept()