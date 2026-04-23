import React, { useState } from 'react';
import { Box, Typography, Card, CardContent, Button, Grid, CircularProgress, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export default function DuplicatesPage() {
  const queryClient = useQueryClient();
  const { data: duplicates, isLoading, isError } = useQuery({
    queryKey: ['duplicates'],
    queryFn: () => api.getDuplicates(),
  });

  const deleteMutation = useMutation({
    mutationFn: (imageId) => api.deleteDuplicate(imageId),
    onSuccess: () => {
      queryClient.invalidateQueries(['duplicates']);
    }
  });

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Typography variant="h5" fontWeight="500" sx={{ mb: 3 }}>Find & Remove Duplicates</Typography>
      
      {isLoading && <CircularProgress />}
      {isError && <Typography color="error">Failed to load duplicates.</Typography>}
      
      {duplicates && duplicates.length === 0 && (
        <Typography color="text.secondary">No duplicates found! Great job organizing.</Typography>
      )}

      {duplicates && duplicates.length > 0 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {duplicates.map((group, index) => (
            <Card key={index} variant="outlined" sx={{ bgcolor: 'background.paper' }}>
              <CardContent>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>Exact Match Group {index + 1}</Typography>
                <Grid container spacing={2}>
                  {group.map((img) => (
                    <Grid item xs={6} sm={4} md={3} key={img.id}>
                      <Box sx={{ 
                        position: 'relative', paddingTop: '100%', borderRadius: 3, overflow: 'hidden', 
                        border: '2px solid transparent', 
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                        '&:hover': { 
                          borderColor: 'error.main',
                          transform: 'scale(1.02)',
                          boxShadow: 4,
                          zIndex: 10
                        } 
                      }}>
                        <img 
                          src={api.getThumbnailUrl(img.id)} 
                          alt="duplicate" 
                          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }} 
                        />
                        <IconButton 
                          sx={{ 
                            position: 'absolute', top: 8, right: 8, 
                            bgcolor: 'rgba(0,0,0,0.5)', color: '#fff', 
                            backdropFilter: 'blur(4px)',
                            transition: 'all 0.2s',
                            '&:hover': { bgcolor: 'error.main', transform: 'scale(1.1)' } 
                          }}
                          size="small"
                          onClick={() => deleteMutation.mutate(img.id)}
                          disabled={deleteMutation.isLoading}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Box>
                      <Typography variant="caption" display="block" noWrap sx={{ mt: 1 }}>{img.file_path.split(/[\\/]/).pop()}</Typography>
                      <Typography variant="caption" color="text.secondary">{img.file_size_bytes} bytes</Typography>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
}
