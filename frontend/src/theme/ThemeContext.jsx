import React, { createContext, useState, useMemo, useContext } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const ThemeToggleContext = createContext({
  toggleColorMode: () => {},
  mode: 'dark'
});

export const useThemeToggle = () => useContext(ThemeToggleContext);

export const ThemeToggleProvider = ({ children }) => {
  const [mode, setMode] = useState('dark');

  const colorMode = useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
      },
      mode
    }),
    [mode],
  );

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'light'
            ? {
                primary: { main: '#1a73e8' },
                background: { default: '#ffffff', paper: '#f8f9fa' },
                text: { primary: '#202124', secondary: '#5f6368' }
              }
            : {
                primary: { main: '#8ab4f8' },
                background: { default: '#202124', paper: '#292a2d' },
                text: { primary: '#e8eaed', secondary: '#9aa0a6' }
              }),
        },
        typography: {
          fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
        },
        components: {
          MuiDrawer: {
            styleOverrides: {
              paper: {
                backgroundColor: mode === 'dark' ? '#202124' : '#ffffff',
                borderRight: 'none',
              }
            }
          },
          MuiAppBar: {
            styleOverrides: {
              root: {
                backgroundColor: mode === 'dark' ? '#202124' : '#ffffff',
                color: mode === 'dark' ? '#e8eaed' : '#202124',
                boxShadow: 'none',
                borderBottom: mode === 'dark' ? '1px solid #3c4043' : '1px solid #e0e0e0',
              }
            }
          }
        }
      }),
    [mode],
  );

  return (
    <ThemeToggleContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeToggleContext.Provider>
  );
};
