import React from 'react';
import { Box, Typography, Grid, CircularProgress } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function ThingsPage() {
  const navigate = useNavigate();
  
  const { data: things, isLoading, isError } = useQuery({
    queryKey: ['things'],
    queryFn: () => api.getThings(),
  });

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight="500">Things</Typography>
      </Box>

      {isLoading && <CircularProgress />}
      {isError && <Typography color="error">Failed to load things categories.</Typography>}

      {things && (
        <Grid container spacing={2}>
          {things.map((thing) => (
            <Grid item xs={6} sm={4} md={3} lg={2.4} xl={2} key={thing.id}>
              <Box 
                sx={{ 
                  position: 'relative', 
                  paddingTop: '100%', 
                  overflow: 'hidden', 
                  cursor: 'pointer', 
                  borderRadius: 4,
                  boxShadow: 2,
                  transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-6px)',
                    boxShadow: 6,
                  }
                }}
              >
                <img 
                  src={api.getThumbnailUrl(thing.thumbnail_image_id)} 
                  alt={thing.label} 
                  style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.5s ease' }} 
                  onClick={() => navigate(`/things/${thing.id}`)}
                  onError={(e) => { e.target.src = 'https://via.placeholder.com/200?text=No+Preview' }}
                  onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                  onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                />

                <Box 
                  onClick={() => navigate(`/things/${thing.id}`)}
                  sx={{ 
                    position: 'absolute', bottom: 0, left: 0, right: 0, p: 1.5, 
                    background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%)', 
                    color: '#fff', textAlign: 'center',
                    pointerEvents: 'none'
                  }}
                >
                  <Typography variant="body2" fontWeight="bold" sx={{ textShadow: '0 2px 4px rgba(0,0,0,0.5)' }} noWrap>
                    {thing.label}
                  </Typography>
                  <Typography variant="caption" display="block" sx={{ opacity: 0.8 }}>
                    {thing.image_count} photos
                  </Typography>
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
