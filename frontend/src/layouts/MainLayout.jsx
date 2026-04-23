import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';

export default function MainLayout() {
  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <TopBar />
        <Box component="main" sx={{ flexGrow: 1, overflowY: 'auto', p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
