import React from 'react';
import { Box, Typography, Grid, IconButton, CircularProgress } from '@mui/material';
import { useSearchParams } from 'react-router-dom';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function SearchPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q');

  const { data: results, isLoading, isError } = useQuery({
    queryKey: ['search', query],
    queryFn: () => api.search(query, { k: 5 }),
    enabled: !!query,
  });

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      {query ? (
        <>
          <Typography variant="h5" sx={{ mb: 4 }}>Search results for "{query}"</Typography>
          
          {isLoading && <CircularProgress />}
          {isError && <Typography color="error">Search failed.</Typography>}
          
          {results && (
            <Grid container spacing={1}>
              {results.length > 0 ? (
                results.map((photo) => (
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
                        alt="search result" 
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
                <Typography color="text.secondary">No results found for your query.</Typography>
              )}
            </Grid>
          )}
        </>
      ) : (
        <Typography variant="h5" color="text.secondary" sx={{ textAlign: 'center', mt: 10 }}>
          Search your photos
        </Typography>
      )}
    </Box>
  );
}
