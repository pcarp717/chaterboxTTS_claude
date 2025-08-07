import React, { useState, useCallback } from 'react';
import {
  Paper,
  TextField,
  Box,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip
} from '@mui/material';
import { VolumeUp, Clear } from '@mui/icons-material';

const MAX_CHARACTERS = 10000;

const TextInput = ({ onGenerate, loading, error }) => {
  const [text, setText] = useState('');

  const handleTextChange = useCallback((event) => {
    const newText = event.target.value;
    if (newText.length <= MAX_CHARACTERS) {
      setText(newText);
    }
  }, []);

  const handleGenerate = useCallback(() => {
    if (text.trim() && onGenerate) {
      onGenerate(text.trim());
    }
  }, [text, onGenerate]);

  const handleClear = useCallback(() => {
    setText('');
  }, []);

  const handleKeyPress = useCallback((event) => {
    if (event.ctrlKey && event.key === 'Enter') {
      event.preventDefault();
      handleGenerate();
    }
  }, [handleGenerate]);

  const characterCount = text.length;
  const isNearLimit = characterCount > MAX_CHARACTERS * 0.8;
  const canGenerate = text.trim().length > 0 && !loading;

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Box mb={2}>
        <Typography variant="h6" gutterBottom>
          Text Input
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Enter the text you want to convert to speech. Press Ctrl+Enter to generate.
        </Typography>
      </Box>

      <TextField
        fullWidth
        multiline
        rows={8}
        value={text}
        onChange={handleTextChange}
        onKeyDown={handleKeyPress}
        placeholder="Type your text here... (maximum 10,000 characters)"
        variant="outlined"
        disabled={loading}
        sx={{
          mb: 2,
          '& .MuiOutlinedInput-root': {
            backgroundColor: loading ? 'action.hover' : 'background.paper'
          }
        }}
      />

      {/* Character counter and actions */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Chip
          label={`${characterCount} / ${MAX_CHARACTERS}`}
          color={isNearLimit ? 'warning' : 'default'}
          size="small"
          variant={isNearLimit ? 'filled' : 'outlined'}
        />

        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Clear />}
            onClick={handleClear}
            disabled={loading || characterCount === 0}
            size="small"
          >
            Clear
          </Button>

          <Button
            variant="contained"
            startIcon={<VolumeUp />}
            onClick={handleGenerate}
            disabled={!canGenerate}
            size="large"
            sx={{ minWidth: 140 }}
          >
            {loading ? 'Generating...' : 'Generate Speech'}
          </Button>
        </Box>
      </Box>

      {/* Loading progress */}
      {loading && (
        <Box mb={2}>
          <LinearProgress />
          <Typography variant="caption" color="text.secondary" mt={1} display="block">
            Processing text and generating speech...
          </Typography>
        </Box>
      )}

      {/* Error display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Text statistics */}
      {text && (
        <Box mt={1}>
          <Typography variant="caption" color="text.secondary">
            Words: {text.trim().split(/\s+/).length} • 
            Estimated duration: ~{Math.max(1, Math.ceil(text.trim().split(/\s+/).length / 180))} minutes
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default TextInput;