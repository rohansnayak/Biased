import React from 'react';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';

export default function AnalysisStatus({ status, polling, error }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 2 }}>
      {polling && <CircularProgress sx={{ mb: 2 }} />}
      <Typography variant="body1">
        {status}
      </Typography>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
    </Box>
  );
} 