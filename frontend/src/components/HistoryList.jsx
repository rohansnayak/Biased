import React from 'react';
import { List, ListItem, ListItemText, Typography, Divider } from '@mui/material';

export default function HistoryList({ history }) {
  if (!history || history.length === 0) {
    return <Typography variant="body2" sx={{ mt: 2 }}>No past analyses found.</Typography>;
  }
  return (
    <List sx={{ mt: 2 }}>
      {history.map((item, idx) => (
        <React.Fragment key={item.id || idx}>
          <ListItem alignItems="flex-start">
            <ListItemText
              primary={item.url || 'Uploaded File'}
              secondary={
                <>
                  <Typography component="span" variant="body2" color="text.primary">
                    Bias: {item.bias_label} | Sentiment: {item.sentiment_label}
                  </Typography>
                  <br />
                  <Typography component="span" variant="caption" color="text.secondary">
                    Submitted: {item.submitted_at}
                  </Typography>
                </>
              }
            />
          </ListItem>
          {idx < history.length - 1 && <Divider component="li" />}
        </React.Fragment>
      ))}
    </List>
  );
} 