import React from 'react';
import { Box, Typography, Grid, IconButton, CircularProgress } from '@mui/material';
import VisibilityOffOutlinedIcon from '@mui/icons-material/VisibilityOffOutlined';
import DeleteIcon from '@mui/icons-material/Delete';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function PeoplePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const { data: people, isLoading, isError } = useQuery({
    queryKey: ['people'],
    queryFn: () => api.getPeople(),
  });

  const deleteMutation = useMutation({
    mutationFn: (clusterId) => api.deletePerson(clusterId),
    onSuccess: () => {
      queryClient.invalidateQueries(['people']);
    }
  });

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight="500">People</Typography>
        {/* <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, cursor: 'pointer', color: 'text.secondary' }}>
          <VisibilityOffOutlinedIcon fontSize="small" />
          <Typography variant="body2" fontWeight="500">Hide faces from memories</Typography>
        </Box> */}
      </Box>

      {isLoading && <CircularProgress />}
      {isError && <Typography color="error">Failed to load people clusters.</Typography>}

      {people && (
        <Grid container spacing={1}>
          {people.map((person) => (
            <Grid item xs={6} sm={4} md={3} lg={2.4} xl={2} key={person.id}>
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
                  src={api.getThumbnailUrl(person.thumbnail_image_id)} 
                  alt={person.label} 
                  style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.5s ease' }} 
                  onClick={() => navigate(`/people/${person.id}`)}
                  onError={(e) => { e.target.src = 'https://via.placeholder.com/200?text=No+Face' }}
                  onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                  onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                />
                
                <IconButton 
                  sx={{ 
                    position: 'absolute', top: 8, right: 8, 
                    bgcolor: 'rgba(0,0,0,0.4)', color: '#fff', 
                    backdropFilter: 'blur(4px)',
                    transition: 'all 0.2s',
                    '&:hover': { bgcolor: 'error.main', transform: 'scale(1.1)' }, 
                    zIndex: 2 
                  }}
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteMutation.mutate(person.id);
                  }}
                  disabled={deleteMutation.isLoading}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>

                <Box 
                  onClick={() => navigate(`/people/${person.id}`)}
                  sx={{ 
                    position: 'absolute', bottom: 0, left: 0, right: 0, p: 1.5, 
                    background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%)', 
                    color: '#fff', textAlign: 'center',
                    pointerEvents: 'none'
                  }}
                >
                  <Typography variant="body2" fontWeight="bold" sx={{ textShadow: '0 2px 4px rgba(0,0,0,0.5)' }} noWrap>
                    {person.label}
                  </Typography>
                  <Typography variant="caption" display="block" sx={{ opacity: 0.8 }}>
                    {person.face_count} photos
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
