import React, { useState, useEffect } from 'react';
import { Box, Typography, Chip, CircularProgress } from '@mui/material';
import { Memory, GraphicEq, Computer } from '@mui/icons-material';
import { ttsApi } from '../services/api';

const StatusBar = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const statusData = await ttsApi.getStatus();
        setStatus(statusData);
      } catch (error) {
        console.error('Failed to fetch status:', error);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll status every 10 seconds
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box display="flex" alignItems="center" p={1}>
        <CircularProgress size={16} />
        <Typography variant="caption" ml={1}>
          Loading status...
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="space-between"
      p={1}
      sx={{
        borderTop: 1,
        borderColor: 'divider',
        backgroundColor: 'background.paper',
        minHeight: 48
      }}
    >
      <Box display="flex" alignItems="center" gap={2}>
        {/* GPU Status */}
        <Chip
          icon={<GraphicEq />}
          label={status?.gpu_available ? 'GPU Ready' : 'CPU Only'}
          color={status?.gpu_available ? 'success' : 'warning'}
          size="small"
        />

        {/* Model Status */}
        <Chip
          icon={<Memory />}
          label={status?.model_loaded ? 'Model Loaded' : 'Model Unloaded'}
          color={status?.model_loaded ? 'info' : 'default'}
          size="small"
        />

        {/* VRAM Usage */}
        {status?.gpu_available && (
          <Typography variant="caption" color="text.secondary">
            VRAM: {status.vram_usage_mb?.toFixed(0)}MB ({status.vram_usage_percent?.toFixed(1)}%)
          </Typography>
        )}
      </Box>

      <Box display="flex" alignItems="center" gap={1}>
        <Computer fontSize="small" color="action" />
        <Typography variant="caption" color="text.secondary">
          Voices: {status?.available_voices?.length || 0}
        </Typography>
      </Box>
    </Box>
  );
};

export default StatusBar;