import React from 'react';
import { useForm } from 'react-hook-form';
import { Box, Button, TextField, Typography, InputLabel, Input, FormHelperText } from '@mui/material';

export default function ArticleInput({ onSubmit }) {
  const { register, handleSubmit, formState: { errors }, reset } = useForm();

  const handleFormSubmit = (data) => {
    onSubmit(data);
    reset();
  };

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)} sx={{ mt: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>Analyze an Article</Typography>
      <TextField
        label="Article URL"
        fullWidth
        margin="normal"
        {...register('url', {
          pattern: {
            value: /^(https?:\/\/)?([\w\-]+\.)+[\w\-]+(\/[\w\-./?%&=]*)?$/,
            message: 'Enter a valid URL',
          },
        })}
        error={!!errors.url}
        helperText={errors.url ? errors.url.message : 'Paste a news article URL'}
      />
      <InputLabel htmlFor="file-upload" sx={{ mt: 2 }}>Or upload a file</InputLabel>
      <Input
        id="file-upload"
        type="file"
        inputProps={{ accept: '.txt,.pdf,.docx' }}
        {...register('file', {
          validate: file => {
            if (file && file.length > 0) {
              const allowed = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
              return allowed.includes(file[0].type) || 'Unsupported file type';
            }
            return true;
          }
        })}
      />
      <FormHelperText error={!!errors.file}>{errors.file ? errors.file.message : 'Accepted: .txt, .pdf, .docx'}</FormHelperText>
      <Button type="submit" variant="contained" sx={{ mt: 2 }}>Analyze</Button>
    </Box>
  );
} 