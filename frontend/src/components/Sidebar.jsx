import React from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Typography, Box, Divider, LinearProgress, Button } from '@mui/material';
import { NavLink } from 'react-router-dom';
import PhotoIcon from '@mui/icons-material/Photo';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import PhotoAlbumIcon from '@mui/icons-material/PhotoAlbum';
import DescriptionIcon from '@mui/icons-material/Description';
import BurstModeIcon from '@mui/icons-material/BurstMode';
import StarOutlineIcon from '@mui/icons-material/StarOutline';
import FaceIcon from '@mui/icons-material/Face';
import PlaceIcon from '@mui/icons-material/Place';
import CloudOutlinedIcon from '@mui/icons-material/CloudOutlined';
import SettingsIcon from '@mui/icons-material/Settings';

const drawerWidth = 260;

export default function Sidebar() {
  const menuItems1 = [
    { text: 'Photos', icon: <PhotoIcon />, path: '/' },
    // { text: 'Updates', icon: <NotificationsNoneIcon />, path: '/updates' },
  ];

  const menuItems2 = [
    { text: 'Things', icon: <PhotoAlbumIcon />, path: '/things' },
    // { text: 'Documents', icon: <DescriptionIcon />, path: '/documents' },
    // { text: 'Duplicates', icon: <BurstModeIcon />, path: '/duplicates' },
    // { text: 'Favorites', icon: <StarOutlineIcon />, path: '/favorites' },
    { text: 'People', icon: <FaceIcon />, path: '/people' },
    { text: 'Social Graph', icon: <PlaceIcon />, path: '/graph' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <img src="/Pixel Mind Logo.png" alt="Logo" style={{ width: 85, height: 85 }} />
        <Typography variant="h6" sx={{ fontSize: '20px', color: 'text.primary' }}>Pixel Mind</Typography> 
      </Box>

      <Box sx={{ overflow: 'auto', px: 1, flex: 1 }}>
        <List>
          {menuItems1.map((item) => (
            <ListItem 
              button 
              component={NavLink} 
              to={item.path} 
              key={item.text}
              sx={{
                borderRadius: '0 24px 24px 0',
                mb: 0.5,
                '&.active': {
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  '& .MuiListItemIcon-root': { color: 'inherit' }
                }
              }}
            >
              <ListItemIcon sx={{ color: 'text.secondary' }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }} />
            </ListItem>
          ))}
        </List>
        <Typography variant="caption" sx={{ px: 3, py: 1, display: 'block', color: 'text.secondary', fontWeight: 500 }}>
          Collections
        </Typography>
        <List>
          {menuItems2.map((item) => (
            <ListItem 
              button 
              component={NavLink} 
              to={item.path} 
              key={item.text}
              sx={{
                borderRadius: '0 24px 24px 0',
                mb: 0.5,
                '&.active': {
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  '& .MuiListItemIcon-root': { color: 'inherit' }
                }
              }}
            >
              <ListItemIcon sx={{ color: 'text.secondary' }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }} />
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 2 }} />
        
        {/* <Box sx={{ px: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1, color: 'text.secondary' }}>
            <CloudOutlinedIcon />
            <Typography variant="body2" fontWeight={500}>Storage</Typography>
          </Box>
          <LinearProgress variant="determinate" value={100} color="error" sx={{ height: 4, borderRadius: 2, mb: 1 }} />
          <Typography variant="caption" color="text.secondary">
            16.2 GB of 15 GB used
          </Typography>
          <Button variant="outlined" sx={{ mt: 2, borderRadius: 6, textTransform: 'none', width: '100%' }}>
            Unlock storage discount
          </Button>
        </Box> */}
      </Box>
      {/* <Box sx={{ p: 2 }}>
         <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', gap: 1, fontSize: '0.7rem' }}>
            <span>Privacy</span> · <span>Terms</span> · <span>Policy</span>
         </Typography>
      </Box> */}
    </Drawer>
  );
}
