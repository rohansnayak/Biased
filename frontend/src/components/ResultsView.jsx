import React from 'react';
import { Card, CardContent, Typography, Chip, Box } from '@mui/material';

export default function ResultsView({ results }) {
  if (!results) return null;
  const { bias_score, bias_label, sentiment_score, sentiment_label, language_flags } = results;
  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6">Analysis Results</Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body1">Bias Score: <Chip label={bias_score} color="primary" /> ({bias_label})</Typography>
          <Typography variant="body1" sx={{ mt: 1 }}>Sentiment: <Chip label={sentiment_label + ' (' + sentiment_score + ')'} color="secondary" /></Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>Loaded Language:</Typography>
          {language_flags && language_flags.length > 0 ? (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
              {language_flags.map((flag, idx) => (
                <Chip key={idx} label={flag.snippet} variant="outlined" />
              ))}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">No loaded language detected.</Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
} 