import React, { useState, useEffect, useCallback } from 'react';
import {
  Paper,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  Person,
  Add,
  Delete,
  Upload,
  Info
} from '@mui/icons-material';
import { ttsApi } from '../services/api';
import { useApi } from '../hooks/useApi';

const VoiceSelector = ({ selectedVoice, onVoiceChange }) => {
  const [voices, setVoices] = useState(['Default']);
  const [customVoices, setCustomVoices] = useState([]);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newVoiceName, setNewVoiceName] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [validationError, setValidationError] = useState('');

  const { loading, error, execute, clearError } = useApi();

  // Load voices
  const loadVoices = useCallback(async () => {
    try {
      const voiceData = await execute(() => ttsApi.listVoices());
      const voiceNames = voiceData.map(v => v.name);
      setVoices(['Default', ...voiceNames]);
      setCustomVoices(voiceData);
    } catch (err) {
      console.error('Failed to load voices:', err);
    }
  }, [execute]);

  useEffect(() => {
    loadVoices();
  }, [loadVoices]);

  const handleCreateVoice = useCallback(async () => {
    if (!newVoiceName.trim()) {
      setValidationError('Voice name is required');
      return;
    }

    if (!selectedFile) {
      setValidationError('Audio file is required');
      return;
    }

    try {
      await execute(() => ttsApi.createVoice(newVoiceName.trim(), selectedFile));
      setCreateDialogOpen(false);
      setNewVoiceName('');
      setSelectedFile(null);
      setValidationError('');
      await loadVoices();
    } catch (err) {
      setValidationError(err.message);
    }
  }, [newVoiceName, selectedFile, execute, loadVoices]);

  const handleDeleteVoice = useCallback(async (voiceName) => {
    if (window.confirm(`Are you sure you want to delete "${voiceName}"?`)) {
      try {
        await execute(() => ttsApi.deleteVoice(voiceName));
        await loadVoices();
        
        // Reset selection if deleted voice was selected
        if (selectedVoice === voiceName) {
          onVoiceChange('Default');
        }
      } catch (err) {
        console.error('Failed to delete voice:', err);
      }
    }
  }, [execute, loadVoices, selectedVoice, onVoiceChange]);

  const handleFileSelect = useCallback(async () => {
    try {
      const result = await window.electronAPI.showOpenDialog();
      if (!result.canceled && result.filePaths.length > 0) {
        const filePath = result.filePaths[0];
        const file = new File(
          [await fetch(`file://${filePath}`).then(r => r.blob())],
          window.electronAPI.path.basename(filePath)
        );
        setSelectedFile(file);
        setValidationError('');
      }
    } catch (err) {
      setValidationError('Failed to load file');
    }
  }, []);

  const openCreateDialog = useCallback(() => {
    setCreateDialogOpen(true);
    setNewVoiceName('');
    setSelectedFile(null);
    setValidationError('');
    clearError();
  }, [clearError]);

  const closeCreateDialog = useCallback(() => {
    setCreateDialogOpen(false);
    setValidationError('');
    clearError();
  }, [clearError]);

  return (
    <>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            Voice Selection
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Choose a voice for speech generation or create custom voices.
          </Typography>
        </Box>

        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel id="voice-select-label">Voice</InputLabel>
          <Select
            labelId="voice-select-label"
            value={selectedVoice}
            label="Voice"
            onChange={(e) => onVoiceChange(e.target.value)}
            startAdornment={<Person sx={{ mr: 1, color: 'action.active' }} />}
          >
            {voices.map((voice) => (
              <MenuItem key={voice} value={voice}>
                <Box display="flex" alignItems="center" width="100%">
                  <Typography>{voice}</Typography>
                  {voice === 'Default' && (
                    <Chip label="Built-in" size="small" sx={{ ml: 1 }} />
                  )}
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button
          variant="outlined"
          startIcon={<Add />}
          onClick={openCreateDialog}
          fullWidth
          disabled={loading}
        >
          Create Custom Voice
        </Button>

        {/* Custom voices list */}
        {customVoices.length > 0 && (
          <Box mt={3}>
            <Typography variant="subtitle2" gutterBottom>
              Custom Voices ({customVoices.length}/10)
            </Typography>
            <List dense>
              {customVoices.map((voice) => (
                <ListItem key={voice.name} divider>
                  <ListItemText
                    primary={voice.name}
                    secondary={`Created: ${new Date(voice.created_date).toLocaleDateString()}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={() => handleDeleteVoice(voice.name)}
                      disabled={loading}
                      size="small"
                    >
                      <Delete />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </Paper>

      {/* Create Voice Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={closeCreateDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create Custom Voice</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Upload a clear audio sample (7-20 seconds) of the voice you want to clone.
              WAV or MP3 format recommended.
            </Typography>
          </Alert>

          <TextField
            fullWidth
            label="Voice Name"
            value={newVoiceName}
            onChange={(e) => setNewVoiceName(e.target.value)}
            sx={{ mb: 2 }}
            disabled={loading}
            placeholder="e.g., My Custom Voice"
          />

          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Upload />}
              onClick={handleFileSelect}
              disabled={loading}
              fullWidth
            >
              {selectedFile ? `Selected: ${selectedFile.name}` : 'Select Audio File'}
            </Button>
          </Box>

          {validationError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {validationError}
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Alert severity="warning" icon={<Info />}>
            <Typography variant="caption">
              Best results: Clear speech, minimal background noise, 10-15 seconds duration.
            </Typography>
          </Alert>
        </DialogContent>

        <DialogActions>
          <Button onClick={closeCreateDialog} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateVoice}
            variant="contained"
            disabled={loading || !newVoiceName.trim() || !selectedFile}
            startIcon={loading ? <CircularProgress size={16} /> : <Add />}
          >
            {loading ? 'Creating...' : 'Create Voice'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default VoiceSelector;