import React, { useState } from 'react';
import { Box, Typography, Grid, IconButton, CircularProgress, Button, TextField, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export default function PersonDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState('');

  const { data: images, isLoading } = useQuery({
    queryKey: ['person_images', id],
    queryFn: () => api.getPersonImages(id),
  });

  const { data: people } = useQuery({
    queryKey: ['people'],
    queryFn: () => api.getPeople(),
  });

  const person = people?.find(p => p.id.toString() === id);
  const displayName = person ? person.label : `Person Cluster ${id}`;

  const renameMutation = useMutation({
    mutationFn: (label) => api.labelPerson(id, label),
    onSuccess: () => {
      queryClient.invalidateQueries(['people']);
      setIsRenaming(false);
    }
  });

  const handleRename = () => {
    if (newName.trim()) {
      renameMutation.mutate(newName.trim());
    }
  };

  const removeImageMutation = useMutation({
    mutationFn: (imageId) => api.removePersonImage(id, imageId),
    onSuccess: () => {
      queryClient.invalidateQueries(['person_images', id]);
      queryClient.invalidateQueries(['people']);
    }
  });

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
        <IconButton onClick={() => navigate('/people')}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h5" fontWeight="500">
          {displayName}
        </Typography>
        <IconButton onClick={() => setIsRenaming(true)} size="small">
          <EditIcon fontSize="small" />
        </IconButton>
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
                '&:hover .overlay': { opacity: 1 } 
              }}>
                <img 
                  src={api.getThumbnailUrl(img.id)} 
                  alt="person" 
                  style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }} 
                  onError={(e) => { e.target.src = 'https://via.placeholder.com/300?text=Not+Found' }}
                />
                <Box className="overlay" sx={{ 
                  position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, 
                  background: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0) 30%)', 
                  opacity: 0, transition: 'opacity 0.2s', zIndex: 1 
                }}>
                   <IconButton 
                     size="small" 
                     onClick={() => removeImageMutation.mutate(img.id)}
                     disabled={removeImageMutation.isLoading}
                     title="Remove from this person"
                     sx={{ position: 'absolute', top: 8, right: 8, color: '#fff', '&:hover': { color: 'error.main' } }}
                   >
                     <Box component="span" sx={{ fontSize: '1rem', fontWeight: 'bold' }}>X</Box>
                   </IconButton>
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={isRenaming} onClose={() => setIsRenaming(false)}>
        <DialogTitle>Rename Person</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            variant="outlined"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsRenaming(false)}>Cancel</Button>
          <Button onClick={handleRename} variant="contained" disabled={renameMutation.isLoading}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
