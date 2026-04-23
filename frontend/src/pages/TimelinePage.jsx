import React from 'react';
import { Box, Typography, Grid, Card, CardMedia, CardActionArea, IconButton, Tooltip, CircularProgress } from '@mui/material';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function TimelinePage() {
  const { data: photos, isLoading, isError } = useQuery({
    queryKey: ['timeline'],
    queryFn: () => api.search(''), // Empty query to get all
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (isError) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="error">Failed to load photos. Is the backend running?</Typography>
      </Box>
    );
  }

  // Group photos by a mock date for now, or just display them all
  // In a real scenario, you'd group by photo metadata date
  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Typography variant="h5" fontWeight="bold" sx={{ mb: 3 }}>Photos</Typography>

      <Box sx={{ mb: 4 }}>
        <Grid container spacing={1}>
          {photos && photos.length > 0 ? (
            photos.map((photo) => (
              <Grid item xs={6} sm={4} md={3} lg={2.4} key={photo.id}>
                <Box sx={{ 
                  position: 'relative', paddingTop: '100%', borderRadius: 3, overflow: 'hidden', cursor: 'pointer', 
                  boxShadow: 1,
                  transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease',
                  '&:hover': { transform: 'scale(1.02)', boxShadow: 4, zIndex: 10 },
                  '&:hover .overlay': { opacity: 1 } 
                }}>
                  <img 
                    src={api.getThumbnailUrl(photo.id)} 
                    alt="timeline item" 
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }} 
                    onError={(e) => { e.target.src = 'https://via.placeholder.com/300?text=Not+Found' }}
                  />
                  <Box className="overlay" sx={{ 
                    position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, 
                    background: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0) 30%)', 
                    opacity: 0, transition: 'opacity 0.2s', zIndex: 1 
                  }}>
                     <IconButton size="small" sx={{ position: 'absolute', top: 8, left: 8, color: '#fff', '&:hover': { color: 'primary.light' } }}>
                       <CheckCircleOutlineIcon fontSize="small" />
                     </IconButton>
                  </Box>
                </Box>
              </Grid>
            ))
          ) : (
            <Typography color="text.secondary" sx={{ mt: 2 }}>No photos found. Try indexing a folder.</Typography>
          )}
        </Grid>
      </Box>
    </Box>
  );
}
