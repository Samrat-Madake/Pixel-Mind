import React from 'react';
import { Box, Typography, Grid } from '@mui/material';

const documentCategories = [
  { id: 1, name: 'Books & magazines', image: 'https://via.placeholder.com/200x200/3c4043/ffffff?text=Books' },
  { id: 2, name: 'Event information', image: 'https://via.placeholder.com/200x200/3c4043/ffffff?text=Event' },
  { id: 3, name: 'Identity', image: 'https://via.placeholder.com/200x200/3c4043/ffffff?text=Identity' },
  { id: 4, name: 'Notes', image: 'https://via.placeholder.com/200x200/3c4043/ffffff?text=Notes' },
  { id: 5, name: 'Payment methods', image: 'https://via.placeholder.com/200x200/3c4043/ffffff?text=Payment' },
  { id: 6, name: 'Receipts', image: 'https://via.placeholder.com/200x200/3c4043/ffffff?text=Receipts' },
  { id: 7, name: 'Recipes & menus', image: 'https://via.placeholder.com/200x200/3c4043/ffffff?text=Recipes' },
  { id: 8, name: 'Social', image: 'https://via.placeholder.com/200x200/3c4043/ffffff?text=Social' },
];

export default function DocumentsPage() {
  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Typography variant="h5" fontWeight="500" sx={{ mb: 3 }}>Documents</Typography>

      <Grid container spacing={0}>
        {documentCategories.map((category) => (
          <Grid item xs={6} sm={4} md={3} lg={2.4} xl={2} key={category.id}>
            <Box sx={{ position: 'relative', paddingTop: '100%', overflow: 'hidden', cursor: 'pointer', border: '1px solid', borderColor: 'background.default' }}>
              <img 
                src={category.image} 
                alt={category.name} 
                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }} 
              />
              <Box sx={{ position: 'absolute', bottom: 0, left: 0, right: 0, p: 1, background: 'linear-gradient(transparent, rgba(0,0,0,0.8))', color: '#fff', textAlign: 'center' }}>
                <Typography variant="body2" fontWeight="bold" noWrap>{category.name}</Typography>
              </Box>
            </Box>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
