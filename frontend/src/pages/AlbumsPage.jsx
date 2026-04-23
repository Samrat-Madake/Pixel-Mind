import React from 'react';
import { Box, Typography } from '@mui/material';

export default function AlbumsPage() {
  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Typography variant="h5" fontWeight="500" sx={{ mb: 3 }}>Albums</Typography>
      <Typography variant="body1" color="text.secondary">
        Your albums will appear here.
      </Typography>
    </Box>
  );
}
