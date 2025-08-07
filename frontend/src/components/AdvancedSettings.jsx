import React, { useState, useCallback } from 'react';
import {
  Paper,
  Typography,
  Box,
  Slider,
  FormControl,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton
} from '@mui/material';
import { ExpandMore, Settings, Info } from '@mui/icons-material';

const AdvancedSettings = ({ settings, onSettingsChange }) => {
  const [expanded, setExpanded] = useState(false);

  const handleChange = useCallback((setting, value) => {
    onSettingsChange({
      ...settings,
      [setting]: value
    });
  }, [settings, onSettingsChange]);

  const handleExpandChange = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded]);

  return (
    <Paper elevation={2}>
      <Accordion expanded={expanded} onChange={handleExpandChange}>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box display="flex" alignItems="center">
            <Settings sx={{ mr: 1 }} />
            <Typography variant="h6">Advanced Settings</Typography>
          </Box>
        </AccordionSummary>
        
        <AccordionDetails>
          <Box sx={{ px: 1 }}>
            {/* Exaggeration Control */}
            <Box mb={3}>
              <Box display="flex" alignItems="center" mb={1}>
                <Typography variant="subtitle2">
                  Emotion Intensity
                </Typography>
                <Tooltip title="Controls how expressive and emotional the generated voice sounds. Higher values create more dramatic speech.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <Info fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <Slider
                value={settings.exaggeration}
                onChange={(_, value) => handleChange('exaggeration', value)}
                min={0}
                max={1}
                step={0.1}
                marks={[
                  { value: 0, label: 'Neutral' },
                  { value: 0.5, label: 'Balanced' },
                  { value: 1, label: 'Expressive' }
                ]}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
              />
              
              <Typography variant="caption" color="text.secondary">
                Current: {Math.round(settings.exaggeration * 100)}% - {
                  settings.exaggeration <= 0.3 ? 'Neutral and calm' :
                  settings.exaggeration <= 0.7 ? 'Moderately expressive' :
                  'Highly expressive and dramatic'
                }
              </Typography>
            </Box>

            {/* CFG Weight Control */}
            <Box mb={2}>
              <Box display="flex" alignItems="center" mb={1}>
                <Typography variant="subtitle2">
                  Voice Guidance
                </Typography>
                <Tooltip title="Controls how closely the AI follows the voice characteristics. Higher values make the voice more consistent but potentially less natural.">
                  <IconButton size="small" sx={{ ml: 0.5 }}>
                    <Info fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <Slider
                value={settings.cfgWeight}
                onChange={(_, value) => handleChange('cfgWeight', value)}
                min={0}
                max={1}
                step={0.1}
                marks={[
                  { value: 0, label: 'Natural' },
                  { value: 0.5, label: 'Balanced' },
                  { value: 1, label: 'Precise' }
                ]}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
              />
              
              <Typography variant="caption" color="text.secondary">
                Current: {Math.round(settings.cfgWeight * 100)}% - {
                  settings.cfgWeight <= 0.3 ? 'More natural, less consistent' :
                  settings.cfgWeight <= 0.7 ? 'Good balance of quality and consistency' :
                  'Very consistent, potentially less natural'
                }
              </Typography>
            </Box>

            <Box mt={3} p={2} sx={{ backgroundColor: 'action.hover', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Tips:</strong> Start with default settings (50% each) and adjust based on your needs. 
                For voice cloning, higher guidance values often work better. For creative content, try higher emotion intensity.
              </Typography>
            </Box>
          </Box>
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default AdvancedSettings;