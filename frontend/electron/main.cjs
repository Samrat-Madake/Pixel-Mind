const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let backendProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    backgroundColor: '#0c0c11',
    icon: path.join(__dirname, 'icon.png'),
    show: false,
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

ipcMain.handle('dialog:openDirectory', async () => {
  if (!mainWindow) return null;
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  if (canceled) {
    return null;
  } else {
    return filePaths[0];
  }
});

function startBackend() {
  const isProd = app.isPackaged;
  let pythonExecutable;
  let mainScript;
  let options = {
    env: { 
      ...process.env, 
      KMP_DUPLICATE_LIB_OK: 'TRUE',
      PYTHONUNBUFFERED: '1'
    }
  };

  if (isProd) {
    // In production, the backend is a compiled EXE provided as an extra resource
    pythonExecutable = path.join(process.resourcesPath, 'pixelmind_backend', 'pixelmind_backend.exe');
    mainScript = null; 
    options.cwd = path.join(process.resourcesPath, 'pixelmind_backend'); // Run inside the backend folder
  } else {
    // In development, use the local venv and script
    pythonExecutable = path.join(__dirname, '../../../venv/Scripts/python.exe');
    mainScript = path.join(__dirname, '../../backend/api/main.py');
    options.cwd = path.join(__dirname, '../../../');
  }

  const args = mainScript ? [mainScript] : [];
  
  try {
    backendProcess = spawn(pythonExecutable, args, options);

    backendProcess.on('error', (err) => {
      dialog.showErrorBox('Backend Start Error', `Failed to start AI engine: ${err.message}\nPath: ${pythonExecutable}`);
    });

    backendProcess.stdout.on('data', (data) => {
      console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
      console.error(`Backend Error: ${data}`);
      // Only show error box if it's a fatal crash, not just warnings
      if (data.toString().includes('Traceback') || data.toString().includes('Error:')) {
        // We don't want to spam dialogs for every warning
      }
    });

    backendProcess.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        dialog.showErrorBox('Backend Crashed', ` AI engine exited unexpectedly with code ${code}. The app might not function correctly.`);
      }
    });
  } catch (err) {
    dialog.showErrorBox('Critical Error', `Could not spawn backend process: ${err.message}`);
  }
}

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (backendProcess) backendProcess.kill();
    app.quit();
  }
});

app.on('quit', () => {
  if (backendProcess) backendProcess.kill();
});
