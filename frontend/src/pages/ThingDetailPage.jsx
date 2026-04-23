import React from 'react';
import { Box, Typography, Grid, IconButton, CircularProgress } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function ThingDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: images, isLoading } = useQuery({
    queryKey: ['thing_images', id],
    queryFn: () => api.getThingImages(id),
  });

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
        <IconButton onClick={() => navigate('/things')}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h5" fontWeight="500">
          {id}
        </Typography>
      </Box>

      {isLoading ? (
        <CircularProgress />
      ) : (
        <Grid container spacing={1}>
          {images?.map((img) => (
            <Grid item xs={6} sm={4} md={3} lg={2.4} key={img.id}>
              <Box sx={{ 
                position: 'relative', paddingTop: '100%', borderRadius: 3, overflow: 'hidden',
                boxShadow: 1,
                transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease',
                '&:hover': { transform: 'scale(1.02)', boxShadow: 4, zIndex: 10 },
              }}>
                <img 
                  src={api.getThumbnailUrl(img.id)} 
                  alt={id} 
                  style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }} 
                  onError={(e) => { e.target.src = 'https://via.placeholder.com/300?text=Not+Found' }}
                />
              </Box>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
