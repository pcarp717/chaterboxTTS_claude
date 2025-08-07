import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Paper,
  Typography,
  Box,
  IconButton,
  Slider,
  LinearProgress,
  Button,
  Alert,
  Tooltip,
  Chip
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  VolumeUp,
  Download,
  Replay,
  Speed
} from '@mui/icons-material';

const AudioControls = ({ audioUrl, filename, generationTime, autoPlay = false }) => {
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const audioRef = useRef(null);

  // Initialize audio element when URL changes
  useEffect(() => {
    if (audioUrl && !audioRef.current) {
      audioRef.current = new Audio(audioUrl);
      
      const audio = audioRef.current;
      
      const handleLoadedMetadata = () => {
        setDuration(audio.duration);
        setError(null);
      };
      
      const handleTimeUpdate = () => {
        setCurrentTime(audio.currentTime);
      };
      
      const handleEnded = () => {
        setPlaying(false);
        setCurrentTime(0);
      };
      
      const handleError = (e) => {
        console.error('Audio error:', e);
        setError('Failed to load audio file');
        setLoading(false);
      };

      const handleLoadStart = () => {
        setLoading(true);
      };

      const handleCanPlay = () => {
        setLoading(false);
        // Auto-play when audio is ready if autoPlay is enabled
        if (autoPlay) {
          audio.play()
            .then(() => setPlaying(true))
            .catch((err) => {
              console.error('Auto-play error:', err);
              setError('Failed to auto-play audio');
            });
        }
      };
      
      audio.addEventListener('loadedmetadata', handleLoadedMetadata);
      audio.addEventListener('timeupdate', handleTimeUpdate);
      audio.addEventListener('ended', handleEnded);
      audio.addEventListener('error', handleError);
      audio.addEventListener('loadstart', handleLoadStart);
      audio.addEventListener('canplay', handleCanPlay);
      
      return () => {
        audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
        audio.removeEventListener('timeupdate', handleTimeUpdate);
        audio.removeEventListener('ended', handleEnded);
        audio.removeEventListener('error', handleError);
        audio.removeEventListener('loadstart', handleLoadStart);
        audio.removeEventListener('canplay', handleCanPlay);
        audio.pause();
        audio.src = '';
      };
    }
  }, [audioUrl]);

  // Update audio source when URL changes
  useEffect(() => {
    if (audioRef.current && audioUrl) {
      audioRef.current.src = audioUrl;
      setCurrentTime(0);
      setPlaying(false);
      setError(null);
    }
  }, [audioUrl]);

  // Update volume
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  // Update playback rate
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackRate;
    }
  }, [playbackRate]);

  const handlePlayPause = useCallback(() => {
    if (!audioRef.current || error) return;
    
    if (playing) {
      audioRef.current.pause();
      setPlaying(false);
    } else {
      audioRef.current.play()
        .then(() => setPlaying(true))
        .catch((err) => {
          console.error('Play error:', err);
          setError('Failed to play audio');
        });
    }
  }, [playing, error]);

  const handleStop = useCallback(() => {
    if (!audioRef.current) return;
    
    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    setPlaying(false);
    setCurrentTime(0);
  }, []);

  const handleSeek = useCallback((_, newValue) => {
    if (!audioRef.current) return;
    
    const time = (newValue / 100) * duration;
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  }, [duration]);

  const handleDownload = useCallback(async () => {
    if (!audioUrl || !filename) return;

    try {
      const response = await fetch(audioUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download error:', err);
      setError('Failed to download file');
    }
  }, [audioUrl, filename]);

  const formatTime = useCallback((time) => {
    if (!isFinite(time)) return '0:00';
    
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }, []);

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  if (!audioUrl) {
    return (
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Audio Player
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Generate speech to see audio controls here.
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Box mb={2} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">
          Audio Player
        </Typography>
        {generationTime && (
          <Chip 
            label={`Generated in ${generationTime.toFixed(1)}s`} 
            size="small" 
            color="success"
          />
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box mb={2}>
          <LinearProgress />
          <Typography variant="caption" color="text.secondary">
            Loading audio...
          </Typography>
        </Box>
      )}

      {/* Main controls */}
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <Tooltip title={playing ? 'Pause' : 'Play'}>
          <IconButton 
            onClick={handlePlayPause} 
            disabled={!audioUrl || error || loading}
            color="primary"
            size="large"
          >
            {playing ? <Pause /> : <PlayArrow />}
          </IconButton>
        </Tooltip>

        <Tooltip title="Stop">
          <IconButton 
            onClick={handleStop} 
            disabled={!audioUrl || error || loading}
            size="large"
          >
            <Stop />
          </IconButton>
        </Tooltip>

        <Tooltip title="Restart">
          <IconButton 
            onClick={() => handleSeek(null, 0)} 
            disabled={!audioUrl || error || loading}
            size="large"
          >
            <Replay />
          </IconButton>
        </Tooltip>

        <Box flex={1} mx={2}>
          <Slider
            value={progress}
            onChange={handleSeek}
            disabled={!audioUrl || error || loading}
            sx={{ height: 4 }}
          />
          <Box display="flex" justifyContent="space-between" mt={0.5}>
            <Typography variant="caption" color="text.secondary">
              {formatTime(currentTime)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {formatTime(duration)}
            </Typography>
          </Box>
        </Box>

        <Tooltip title="Download">
          <IconButton 
            onClick={handleDownload}
            disabled={!audioUrl || error}
            size="large"
          >
            <Download />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Volume and Speed controls */}
      <Box display="flex" alignItems="center" gap={3}>
        {/* Volume control */}
        <Box display="flex" alignItems="center" gap={1}>
          <VolumeUp color="action" />
          <Slider
            value={volume * 100}
            onChange={(_, newValue) => setVolume(newValue / 100)}
            sx={{ width: 100 }}
            disabled={!audioUrl || error}
          />
          <Typography variant="caption" color="text.secondary" minWidth={30}>
            {Math.round(volume * 100)}%
          </Typography>
        </Box>

        {/* Playback speed control */}
        <Box display="flex" alignItems="center" gap={1}>
          <Speed color="action" />
          <Slider
            value={playbackRate}
            onChange={(_, newValue) => setPlaybackRate(newValue)}
            min={0.5}
            max={2}
            step={0.1}
            sx={{ width: 100 }}
            disabled={!audioUrl || error}
            marks={[
              { value: 0.5, label: '0.5x' },
              { value: 1, label: '1x' },
              { value: 1.5, label: '1.5x' },
              { value: 2, label: '2x' }
            ]}
          />
          <Typography variant="caption" color="text.secondary" minWidth={35}>
            {playbackRate.toFixed(1)}x
          </Typography>
        </Box>
      </Box>

      {filename && (
        <Box mt={2}>
          <Typography variant="caption" color="text.secondary">
            File: {filename}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default AudioControls;