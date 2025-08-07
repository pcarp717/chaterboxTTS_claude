import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout for TTS generation
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.code === 'ECONNREFUSED') {
      throw new Error('Cannot connect to TTS server. Please make sure the Python backend is running.');
    }
    
    if (error.response?.status === 500) {
      throw new Error(error.response.data?.detail || 'Server error occurred');
    }
    
    throw error;
  }
);

export const ttsApi = {
  // Health check
  async checkHealth() {
    const response = await api.get('/');
    return response.data;
  },

  // Get system status
  async getStatus() {
    const response = await api.get('/status');
    return response.data;
  },

  // Generate speech
  async generateSpeech(text, voiceProfile = 'Default', exaggeration = 0.5, cfgWeight = 0.5, format = 'wav') {
    const response = await api.post('/generate', {
      text,
      voice_profile: voiceProfile,
      exaggeration,
      cfg_weight: cfgWeight,
      format
    });
    return response.data;
  },

  // Get audio file URL
  getAudioUrl(filename) {
    return `${API_BASE_URL}/audio/${filename}`;
  },

  // List available voices
  async listVoices() {
    const response = await api.get('/voices');
    return response.data;
  },

  // Create new voice
  async createVoice(voiceName, audioFile) {
    const formData = new FormData();
    formData.append('voice_name', voiceName);
    formData.append('audio_file', audioFile);

    const response = await api.post('/voices/create', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Delete voice
  async deleteVoice(voiceName) {
    const response = await api.delete(`/voices/${voiceName}`);
    return response.data;
  }
};

export default api;