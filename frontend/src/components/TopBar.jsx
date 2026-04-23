import React, { useState } from 'react';
import { AppBar, Toolbar, InputBase, IconButton, Box, Avatar } from '@mui/material';
import { alpha, styled } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import AppsIcon from '@mui/icons-material/Apps';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useThemeToggle } from '../theme/ThemeContext';
import { useNavigate } from 'react-router-dom';

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: 8,
  backgroundColor: theme.palette.mode === 'dark' ? '#3c4043' : '#f1f3f4',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? '#4a4d51' : '#e8eaed',
  },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(3),
    width: '720px',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: theme.palette.text.secondary,
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  width: '100%',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1.5, 1, 1.5, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
  },
}));

export default function TopBar() {
  const { mode, toggleColorMode } = useThemeToggle();
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <AppBar position="static">
      <Toolbar sx={{ justifyContent: 'space-between', px: 2 }}>
        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center' }}>
          <Search>
            <SearchIconWrapper>
              <SearchIcon />
            </SearchIconWrapper>
            <StyledInputBase
              placeholder='Search "India"'
              inputProps={{ 'aria-label': 'search' }}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleSearch}
            />
          </Search>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* <IconButton color="inherit">
            <AddIcon />
          </IconButton> */}
          <IconButton color="inherit" onClick={toggleColorMode}>
            {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
          {/* <IconButton color="inherit">
            <HelpOutlineIcon />
          </IconButton> */}
          {/* <IconButton color="inherit">
            <SettingsOutlinedIcon />
          </IconButton> */}
          {/* <IconButton color="inherit">
            <AppsIcon />
          </IconButton> */}
          {/* <IconButton sx={{ ml: 1 }}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: '#1e8e3e' }}>S</Avatar>
          </IconButton> */}
        </Box>
      </Toolbar>
    </AppBar>
  );
}
