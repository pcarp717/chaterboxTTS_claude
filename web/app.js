// ChatterboxTTS Desktop - Frontend JavaScript

class ChatterboxApp {
    constructor() {
        this.currentAudio = null;
        this.audioData = null;
        this.isPlaying = false;
        this.websocket = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadVoices();
        this.startWebSocket();
        this.updateSystemStatus();
        this.initializeDarkMode();
    }
    
    initializeElements() {
        // Text input
        this.textInput = document.getElementById('textInput');
        this.charCount = document.getElementById('charCount');
        
        // Voice selection
        this.voiceSelect = document.getElementById('voiceSelect');
        this.voiceInfo = document.getElementById('voiceInfo');
        
        // Voice controls
        this.exaggeration = document.getElementById('exaggeration');
        this.exaggerationValue = document.getElementById('exaggerationValue');
        this.cfgWeight = document.getElementById('cfgWeight');
        this.cfgWeightValue = document.getElementById('cfgWeightValue');
        
        // Generation
        this.generateBtn = document.getElementById('generateBtn');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.statusMessage = document.getElementById('statusMessage');
        
        // Audio player
        this.audioPlayer = document.getElementById('audioPlayer');
        this.waveformPlaceholder = document.getElementById('waveformPlaceholder');
        this.audioControls = document.getElementById('audioControls');
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.timeline = document.getElementById('timeline');
        this.currentTime = document.getElementById('currentTime');
        this.totalTime = document.getElementById('totalTime');
        this.volumeSlider = document.getElementById('volumeSlider');
        this.playbackSpeedSlider = document.getElementById('playbackSpeedSlider');
        this.speedValue = document.getElementById('speedValue');
        
        // Export
        this.exportBtn = document.getElementById('exportBtn');
        this.exportFormat = document.getElementById('exportFormat');
        
        // System status
        this.deviceStatus = document.getElementById('deviceStatus');
        this.memoryStatus = document.getElementById('memoryStatus');
        this.modelStatus = document.getElementById('modelStatus');
        
        // Voice management modal
        this.voiceModal = document.getElementById('voiceModal');
        this.manageVoicesBtn = document.getElementById('manageVoicesBtn');
        this.closeModal = document.getElementById('closeModal');
        this.voiceName = document.getElementById('voiceName');
        this.voiceFile = document.getElementById('voiceFile');
        this.fileName = document.getElementById('fileName');
        this.addVoiceBtn = document.getElementById('addVoiceBtn');
        this.voiceListContainer = document.getElementById('voiceListContainer');
        this.modalStatus = document.getElementById('modalStatus');
        
        // Dark mode toggle
        this.darkModeToggle = document.getElementById('darkModeToggle');
    }
    
    bindEvents() {
        // Text input
        this.textInput.addEventListener('input', () => this.updateCharCount());
        
        // Voice selection
        this.voiceSelect.addEventListener('change', () => this.updateVoiceInfo());
        
        // Range sliders
        this.exaggeration.addEventListener('input', (e) => {
            this.exaggerationValue.textContent = e.target.value;
        });
        
        this.cfgWeight.addEventListener('input', (e) => {
            this.cfgWeightValue.textContent = e.target.value;
        });
        
        // Generate button
        this.generateBtn.addEventListener('click', () => this.generateSpeech());
        
        // Audio controls
        this.playPauseBtn.addEventListener('click', () => this.togglePlayPause());
        this.timeline.addEventListener('input', () => this.seekAudio());
        this.volumeSlider.addEventListener('input', () => this.updateVolume());
        this.playbackSpeedSlider.addEventListener('input', () => this.updatePlaybackSpeed());
        
        // Audio player events
        this.audioPlayer.addEventListener('loadedmetadata', () => this.onAudioLoaded());
        this.audioPlayer.addEventListener('timeupdate', () => this.updateTimeDisplay());
        this.audioPlayer.addEventListener('ended', () => this.onAudioEnded());
        
        // Export
        this.exportBtn.addEventListener('click', () => this.exportAudio());
        
        // Voice management modal
        this.manageVoicesBtn.addEventListener('click', () => this.openVoiceModal());
        this.closeModal.addEventListener('click', () => this.closeVoiceModal());
        this.voiceFile.addEventListener('change', () => this.updateFileName());
        this.addVoiceBtn.addEventListener('click', () => this.addVoice());
        
        // Dark mode toggle
        this.darkModeToggle.addEventListener('click', () => this.toggleDarkMode());
        
        // Model status click to preload
        this.modelStatus.addEventListener('click', () => this.preloadModel());
        
        // Close modal on outside click
        this.voiceModal.addEventListener('click', (e) => {
            if (e.target === this.voiceModal) {
                this.closeVoiceModal();
            }
        });
    }
    
    updateCharCount() {
        const count = this.textInput.value.length;
        this.charCount.textContent = count;
        
        if (count > 9000) {
            this.charCount.style.color = 'var(--danger-color)';
        } else if (count > 7000) {
            this.charCount.style.color = 'var(--warning-color)';
        } else {
            this.charCount.style.color = 'var(--text-secondary)';
        }
    }
    
    async loadVoices() {
        try {
            const response = await fetch('/api/voices');
            const voices = await response.json();
            
            this.voiceSelect.innerHTML = '';
            voices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = voice.name;
                this.voiceSelect.appendChild(option);
            });
            
            this.updateVoiceInfo();
        } catch (error) {
            console.error('Failed to load voices:', error);
        }
    }
    
    async updateVoiceInfo() {
        const selectedVoice = this.voiceSelect.value;
        
        try {
            const response = await fetch('/api/voices');
            const voices = await response.json();
            const voice = voices.find(v => v.name === selectedVoice);
            
            if (voice) {
                if (voice.type === 'built-in') {
                    this.voiceInfo.innerHTML = `<strong>${voice.name}</strong><br>${voice.description}`;
                } else {
                    const createdDate = new Date(voice.created_date).toLocaleDateString();
                    this.voiceInfo.innerHTML = `
                        <strong>${voice.name}</strong> (Custom Voice)<br>
                        Duration: ${voice.duration?.toFixed(1)}s<br>
                        Sample Rate: ${voice.sample_rate} Hz<br>
                        Created: ${createdDate}
                    `;
                }
            }
        } catch (error) {
            console.error('Failed to update voice info:', error);
        }
    }
    
    async generateSpeech() {
        const text = this.textInput.value.trim();
        
        if (!text) {
            this.showStatus('Please enter some text to generate speech.', 'error');
            return;
        }
        
        this.generateBtn.disabled = true;
        this.progressContainer.style.display = 'block';
        this.progressFill.style.width = '0%';
        this.progressText.textContent = 'Starting generation...';
        
        try {
            // Simulate progress
            this.animateProgress();
            
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice: this.voiceSelect.value,
                    exaggeration: parseFloat(this.exaggeration.value),
                    cfg_weight: parseFloat(this.cfgWeight.value)
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.loadGeneratedAudio(result);
                this.showStatus(result.message, 'success');
            } else {
                throw new Error(result.message || 'Generation failed');
            }
            
        } catch (error) {
            this.showStatus(`Error: ${error.message}`, 'error');
        } finally {
            this.generateBtn.disabled = false;
            this.progressContainer.style.display = 'none';
        }
    }
    
    animateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) {
                clearInterval(interval);
                progress = 90;
            }
            this.progressFill.style.width = `${progress}%`;
        }, 200);
        
        // Clear interval after 10 seconds max
        setTimeout(() => clearInterval(interval), 10000);
    }
    
    loadGeneratedAudio(result) {
        // Convert base64 to blob
        const audioData = atob(result.audio_data);
        const arrayBuffer = new ArrayBuffer(audioData.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        
        for (let i = 0; i < audioData.length; i++) {
            uint8Array[i] = audioData.charCodeAt(i);
        }
        
        const audioBlob = new Blob([arrayBuffer], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Store audio data for export
        this.audioData = result;
        
        // Load into audio player
        this.audioPlayer.src = audioUrl;
        this.audioPlayer.load();
        
        // Show audio controls
        this.waveformPlaceholder.style.display = 'none';
        this.audioControls.style.display = 'flex';
        this.exportBtn.disabled = false;
        
        // Auto-play
        this.audioPlayer.play().catch(console.error);
    }
    
    togglePlayPause() {
        if (this.audioPlayer.paused) {
            this.audioPlayer.play();
            this.playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
            this.isPlaying = true;
        } else {
            this.audioPlayer.pause();
            this.playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            this.isPlaying = false;
        }
    }
    
    seekAudio() {
        const seekTime = (this.timeline.value / 100) * this.audioPlayer.duration;
        this.audioPlayer.currentTime = seekTime;
    }
    
    updateVolume() {
        this.audioPlayer.volume = this.volumeSlider.value / 100;
    }
    
    updatePlaybackSpeed() {
        const speed = parseFloat(this.playbackSpeedSlider.value);
        this.audioPlayer.playbackRate = speed;
        this.speedValue.textContent = `${speed.toFixed(1)}x`;
    }
    
    onAudioLoaded() {
        this.totalTime.textContent = this.formatTime(this.audioPlayer.duration);
        this.timeline.max = 100;
    }
    
    updateTimeDisplay() {
        if (this.audioPlayer.duration) {
            const progress = (this.audioPlayer.currentTime / this.audioPlayer.duration) * 100;
            this.timeline.value = progress;
            this.currentTime.textContent = this.formatTime(this.audioPlayer.currentTime);
        }
    }
    
    onAudioEnded() {
        this.playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
        this.isPlaying = false;
        this.timeline.value = 0;
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    async exportAudio() {
        if (!this.audioData) {
            this.showStatus('No audio to export', 'error');
            return;
        }
        
        try {
            // Convert base64 to blob
            const audioData = atob(this.audioData.audio_data);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const uint8Array = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                uint8Array[i] = audioData.charCodeAt(i);
            }
            
            const audioBlob = new Blob([arrayBuffer], { type: 'audio/wav' });
            
            // Create download link
            const url = URL.createObjectURL(audioBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chatterbox_output_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.wav`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showStatus('Audio exported successfully', 'success');
        } catch (error) {
            this.showStatus(`Export failed: ${error.message}`, 'error');
        }
    }
    
    showStatus(message, type = 'info') {
        this.statusMessage.textContent = message;
        this.statusMessage.className = `status-message status-${type}`;
    }
    
    // Dark Mode Functions
    initializeDarkMode() {
        // Check for saved theme preference or default to light mode
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
            this.setDarkMode(true);
        } else {
            this.setDarkMode(false);
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.setDarkMode(e.matches);
            }
        });
    }
    
    toggleDarkMode() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        this.setDarkMode(!isDark);
        localStorage.setItem('theme', !isDark ? 'dark' : 'light');
    }
    
    setDarkMode(isDark) {
        if (isDark) {
            document.documentElement.setAttribute('data-theme', 'dark');
            this.darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            this.darkModeToggle.title = 'Switch to Light Mode';
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            this.darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            this.darkModeToggle.title = 'Switch to Dark Mode';
        }
    }
    
    // Voice Management Modal
    openVoiceModal() {
        this.voiceModal.style.display = 'flex';
        this.loadVoiceList();
    }
    
    closeVoiceModal() {
        this.voiceModal.style.display = 'none';
        this.modalStatus.textContent = '';
        this.voiceName.value = '';
        this.voiceFile.value = '';
        this.fileName.textContent = 'No file selected';
    }
    
    updateFileName() {
        const file = this.voiceFile.files[0];
        this.fileName.textContent = file ? file.name : 'No file selected';
    }
    
    async addVoice() {
        const name = this.voiceName.value.trim();
        const file = this.voiceFile.files[0];
        
        if (!name) {
            this.modalStatus.textContent = '❌ Please enter a voice name.';
            this.modalStatus.className = 'modal-status status-error';
            return;
        }
        
        if (!file) {
            this.modalStatus.textContent = '❌ Please select an audio file.';
            this.modalStatus.className = 'modal-status status-error';
            return;
        }
        
        this.addVoiceBtn.disabled = true;
        this.modalStatus.textContent = 'Uploading voice...';
        this.modalStatus.className = 'modal-status';
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('name', name);
            
            const response = await fetch('/api/voices/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.modalStatus.textContent = `✅ ${result.message}`;
                this.modalStatus.className = 'modal-status status-success';
                
                // Refresh voice list
                await this.loadVoices();
                await this.loadVoiceList();
                
                // Clear form
                this.voiceName.value = '';
                this.voiceFile.value = '';
                this.fileName.textContent = 'No file selected';
            } else {
                throw new Error(result.detail || 'Upload failed');
            }
        } catch (error) {
            this.modalStatus.textContent = `❌ ${error.message}`;
            this.modalStatus.className = 'modal-status status-error';
        } finally {
            this.addVoiceBtn.disabled = false;
        }
    }
    
    async loadVoiceList() {
        try {
            const response = await fetch('/api/voices');
            const voices = await response.json();
            const customVoices = voices.filter(v => v.type === 'custom');
            
            if (customVoices.length === 0) {
                this.voiceListContainer.innerHTML = '<p class="no-voices">No custom voices added yet.</p>';
                return;
            }
            
            this.voiceListContainer.innerHTML = customVoices.map(voice => `
                <div class="voice-item">
                    <div class="voice-item-info">
                        <h4>${voice.name}</h4>
                        <div class="voice-item-details">
                            Duration: ${voice.duration?.toFixed(1)}s | 
                            Sample Rate: ${voice.sample_rate} Hz | 
                            Created: ${new Date(voice.created_date).toLocaleDateString()}
                        </div>
                    </div>
                    <button class="btn btn-danger" onclick="app.deleteVoice('${voice.name}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load voice list:', error);
        }
    }
    
    async deleteVoice(voiceName) {
        if (!confirm(`Are you sure you want to delete the voice "${voiceName}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/voices/${encodeURIComponent(voiceName)}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.modalStatus.textContent = `✅ ${result.message}`;
                this.modalStatus.className = 'modal-status status-success';
                
                // Refresh voice lists
                await this.loadVoices();
                await this.loadVoiceList();
            } else {
                throw new Error(result.detail || 'Delete failed');
            }
        } catch (error) {
            this.modalStatus.textContent = `❌ ${error.message}`;
            this.modalStatus.className = 'modal-status status-error';
        }
    }
    
    // WebSocket for real-time updates
    startWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'status_update') {
                this.updateSystemStatusFromData(data.data);
            }
        };
        
        this.websocket.onclose = () => {
            // Reconnect after 5 seconds
            setTimeout(() => this.startWebSocket(), 5000);
        };
    }
    
    async updateSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            this.updateSystemStatusFromData(status);
        } catch (error) {
            console.error('Failed to fetch system status:', error);
        }
    }
    
    updateSystemStatusFromData(status) {
        // Device status
        this.deviceStatus.textContent = status.device.toUpperCase();
        
        // Memory status
        if (status.vram_used !== undefined) {
            this.memoryStatus.textContent = `VRAM: ${status.vram_used.toFixed(1)}GB / ${status.vram_total.toFixed(1)}GB (${status.vram_usage_percent.toFixed(1)}%)`;
        } else {
            this.memoryStatus.textContent = `RAM: ${status.ram_usage_percent.toFixed(1)}%`;
        }
        
        // Model status
        this.modelStatus.textContent = status.model_loaded ? 'Loaded' : 'Not loaded';
        this.modelStatus.className = status.model_loaded ? 'status-success' : '';
        
        // Update tooltip
        this.modelStatus.title = status.model_loaded ? 
            'Model is loaded and ready' : 
            'Click to preload model (speeds up first generation)';
    }
    
    async preloadModel() {
        // Don't reload if already loaded
        const currentStatus = this.modelStatus.textContent;
        if (currentStatus === 'Loaded') {
            return;
        }
        
        // Show loading state
        this.modelStatus.textContent = 'Loading...';
        this.modelStatus.className = 'loading';
        this.modelStatus.title = 'Loading model, please wait...';
        
        try {
            const response = await fetch('/api/preload-model', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Update status immediately
                this.modelStatus.textContent = 'Loaded';
                this.modelStatus.className = 'status-success';
                this.modelStatus.title = 'Model is loaded and ready';
                
                // Show success message briefly
                this.showStatus(`✅ Model loaded successfully on ${result.device.toUpperCase()}`, 'success');
                
                // Refresh system status
                this.updateSystemStatus();
            } else {
                throw new Error(result.detail || 'Failed to load model');
            }
        } catch (error) {
            // Reset status on error
            this.modelStatus.textContent = 'Not loaded';
            this.modelStatus.className = '';
            this.modelStatus.title = 'Click to preload model (speeds up first generation)';
            
            this.showStatus(`❌ Failed to load model: ${error.message}`, 'error');
        }
    }
}

// Initialize app when page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ChatterboxApp();
});