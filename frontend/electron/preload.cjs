const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Add IPC methods here as needed
  onIndexingProgress: (callback) => ipcRenderer.on('indexing-progress', callback),
  selectFolder: () => ipcRenderer.invoke('dialog:openDirectory'),
});
