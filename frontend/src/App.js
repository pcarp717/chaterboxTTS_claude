import React, { useState, useCallback, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  Grid,
  AppBar,
  Toolbar,
  Typography,
  Alert,
  Snackbar,
  IconButton,
  Tooltip
} from '@mui/material';
import { VolumeUp, DarkMode, LightMode } from '@mui/icons-material';

import TextInput from './components/TextInput';
import VoiceSelector from './components/VoiceSelector';
import AudioControls from './components/AudioControls';
import AdvancedSettings from './components/AdvancedSettings';
import StatusBar from './components/StatusBar';

import { ttsApi } from './services/api';
import { useApi } from './hooks/useApi';

// Create dynamic Material-UI theme
const createAppTheme = (darkMode) => createTheme({
  palette: {
    mode: darkMode ? 'dark' : 'light',
    primary: {
      main: darkMode ? '#90caf9' : '#1976d2',
    },
    secondary: {
      main: darkMode ? '#f48fb1' : '#dc004e',
    },
    background: {
      default: darkMode ? '#121212' : '#f5f5f5',
      paper: darkMode ? '#1e1e1e' : '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

function App() {
  // State
  const [selectedVoice, setSelectedVoice] = useState('Default');
  const [darkMode, setDarkMode] = useState(true); // Default to dark mode
  const [settings, setSettings] = useState({
    exaggeration: 0.5,
    cfgWeight: 0.5,
    format: 'wav'
  });
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioFilename, setAudioFilename] = useState(null);
  const [generationTime, setGenerationTime] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

  const { loading, error, execute, clearError } = useApi();

  // Check server connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await execute(() => ttsApi.checkHealth());
        showNotification('Connected to TTS server', 'success');
      } catch (err) {
        console.error('Failed to connect to server:', err);
      }
    };

    checkConnection();
  }, [execute]);

  const showNotification = useCallback((message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  }, []);

  const hideNotification = useCallback(() => {
    setNotification(prev => ({ ...prev, open: false }));
  }, []);

  const handleGenerate = useCallback(async (text) => {
    try {
      clearError();
      
      const startTime = Date.now();
      const result = await execute(() => 
        ttsApi.generateSpeech(
          text,
          selectedVoice,
          settings.exaggeration,
          settings.cfgWeight,
          settings.format
        )
      );
      
      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      
      if (result.success) {
        const url = ttsApi.getAudioUrl(result.audio_file);
        setAudioUrl(url);
        setAudioFilename(result.audio_file);
        setGenerationTime(duration);
        showNotification(result.message, 'success');
      }
    } catch (err) {
      showNotification(`Generation failed: ${err.message}`, 'error');
    }
  }, [selectedVoice, settings, execute, clearError, showNotification]);

  const handleVoiceChange = useCallback((voice) => {
    setSelectedVoice(voice);
    showNotification(`Selected voice: ${voice}`, 'info');
  }, [showNotification]);

  const handleSettingsChange = useCallback((newSettings) => {
    setSettings(newSettings);
  }, []);

  const theme = createAppTheme(darkMode);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* App Bar */}
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <VolumeUp sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              ChatterboxTTS Desktop
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8, mr: 2 }}>
              High-Quality Local Text-to-Speech
            </Typography>
            <Tooltip title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
              <IconButton
                color="inherit"
                onClick={() => setDarkMode(!darkMode)}
                size="large"
              >
                {darkMode ? <LightMode /> : <DarkMode />}
              </IconButton>
            </Tooltip>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Box sx={{ flex: 1, p: 3, backgroundColor: 'background.default' }}>
          <Grid container spacing={3}>
            {/* Left Column */}
            <Grid item xs={12} md={8}>
              <Grid container spacing={3}>
                {/* Text Input */}
                <Grid item xs={12}>
                  <TextInput
                    onGenerate={handleGenerate}
                    loading={loading}
                    error={error}
                  />
                </Grid>

                {/* Audio Controls */}
                <Grid item xs={12}>
                  <AudioControls
                    audioUrl={audioUrl}
                    filename={audioFilename}
                    generationTime={generationTime}
                    autoPlay={true}
                  />
                </Grid>
              </Grid>
            </Grid>

            {/* Right Column */}
            <Grid item xs={12} md={4}>
              <Grid container spacing={3}>
                {/* Voice Selector */}
                <Grid item xs={12}>
                  <VoiceSelector
                    selectedVoice={selectedVoice}
                    onVoiceChange={handleVoiceChange}
                  />
                </Grid>

                {/* Advanced Settings */}
                <Grid item xs={12}>
                  <AdvancedSettings
                    settings={settings}
                    onSettingsChange={handleSettingsChange}
                  />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Box>

        {/* Status Bar */}
        <StatusBar />

        {/* Notifications */}
        <Snackbar
          open={notification.open}
          autoHideDuration={4000}
          onClose={hideNotification}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert 
            onClose={hideNotification} 
            severity={notification.severity}
            variant="filled"
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;