import { autoUpdater } from 'electron-updater';
import { dialog, app } from 'electron';
import log from 'electron-log';

// Configure logging
autoUpdater.logger = log;

export function initializeUpdater() {
  // Check for updates on launch
  autoUpdater.checkForUpdatesAndNotify().catch((err) => {
    log.error('Failed to check for updates:', err);
  });

  // Handle update downloaded
  autoUpdater.on('update-downloaded', (info) => {
    log.info('Update downloaded:', info.version);
    
    dialog
      .showMessageBox({
        type: 'info',
        title: 'Update Available',
        message: `Version ${info.version} is ready to install`,
        detail: 'The update will be installed when you restart the application.',
        buttons: ['Restart Now', 'Later'],
      })
      .then((result) => {
        if (result.response === 0) {
          autoUpdater.quitAndInstall();
        }
      });
  });

  // Handle update errors
  autoUpdater.on('error', (err) => {
    log.error('Update error:', err);
  });

  // Handle checking for update
  autoUpdater.on('checking-for-update', () => {
    log.info('Checking for updates...');
  });

  // Handle update available
  autoUpdater.on('update-available', (info) => {
    log.info('Update available:', info.version);
  });

  // Handle update not available
  autoUpdater.on('update-not-available', () => {
    log.info('No updates available');
  });
}

export function checkForUpdates() {
  autoUpdater.checkForUpdates();
}
