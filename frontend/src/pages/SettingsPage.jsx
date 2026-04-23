import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField, Button, LinearProgress, Paper, Divider } from '@mui/material';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function SettingsPage() {
  const [folderPath, setFolderPath] = useState('');
  const [isIndexing, setIsIndexing] = useState(false);

  const startMutation = useMutation({
    mutationFn: (path) => api.startIndexing(path),
    onSuccess: () => setIsIndexing(true),
  });

  const { data: progress } = useQuery({
    queryKey: ['index_progress'],
    queryFn: () => api.getIndexProgress(),
    refetchInterval: isIndexing ? 2000 : false, // Poll every 2s if indexing
  });

  useEffect(() => {
    if (progress && progress.status === 'completed' && isIndexing) {
      setIsIndexing(false);
    }
  }, [progress, isIndexing]);

  const handleStart = () => {
    if (folderPath.trim()) {
      startMutation.mutate(folderPath.trim());
    }
  };

  const handleSelectFolder = async () => {
    if (window.electronAPI && window.electronAPI.selectFolder) {
      const folder = await window.electronAPI.selectFolder();
      if (folder) {
        setFolderPath(folder);
      }
    } else {
      alert("Folder selection is only supported in the desktop app.");
    }
  };

  return (
    <Box sx={{ maxWidth: '800px', mx: 'auto', p: 3 }}>
      <Typography variant="h5" fontWeight="500" sx={{ mb: 4 }}>Settings & Ingestion</Typography>

      <Paper variant="outlined" sx={{ p: 3, mb: 4, bgcolor: 'background.paper' }}>
        <Typography variant="h6" sx={{ mb: 1 }}>Index Local Photos</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Select a local directory on your PC to ingest photos. 
          PixelMind will index them, extract metadata, cluster faces, and calculate embeddings.
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField 
            fullWidth 
            label="Directory Path" 
            variant="outlined" 
            value={folderPath}
            onChange={(e) => setFolderPath(e.target.value)}
            disabled={isIndexing}
            InputProps={{
              startAdornment: <FolderOpenIcon sx={{ color: 'text.secondary', mr: 1 }} />
            }}
          />
          <Button 
            variant="outlined" 
            size="large" 
            onClick={handleSelectFolder}
            disabled={isIndexing}
            sx={{ minWidth: '120px' }}
          >
            Browse
          </Button>
          <Button 
            variant="contained" 
            size="large" 
            startIcon={<PlayArrowIcon />}
            onClick={handleStart}
            disabled={isIndexing || !folderPath.trim()}
          >
            Start
          </Button>
        </Box>

        {(isIndexing || (progress && progress.status === 'indexing')) && (
          <Box sx={{ mt: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" fontWeight="bold">Indexing Progress</Typography>
              <Typography variant="body2">{progress?.current_step || 'Initializing...'}</Typography>
            </Box>
            <LinearProgress 
              variant={progress?.total_items ? "determinate" : "indeterminate"} 
              value={progress?.total_items ? (progress.processed_items / progress.total_items) * 100 : 0} 
              sx={{ height: 10, borderRadius: 5 }}
            />
            {progress?.total_items && (
              <Typography variant="caption" sx={{ display: 'block', mt: 1, textAlign: 'right' }}>
                {progress.processed_items} / {progress.total_items} items processed
              </Typography>
            )}
          </Box>
        )}
      </Paper>
    </Box>
  );
}
