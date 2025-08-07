const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  showSaveDialog: () => ipcRenderer.invoke('show-save-dialog'),
  showOpenDialog: () => ipcRenderer.invoke('show-open-dialog'),
  
  // Platform information
  platform: process.platform,
  
  // Node.js path utilities (safe subset)
  path: {
    join: (...args) => require('path').join(...args),
    basename: (p) => require('path').basename(p),
    dirname: (p) => require('path').dirname(p),
    extname: (p) => require('path').extname(p)
  }
});