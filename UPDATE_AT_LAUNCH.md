# Update at Launch Implementation

This document describes the automatic update mechanism added to the Surface FRU Selector Electron application.

## Overview

The application now automatically checks for updates when it launches (in production builds). If an update is available, the user is notified and can choose to install it immediately or defer the installation.

## Components Added

### 1. **`src/main/updater.ts`** - Update Handler Module
- Initializes the electron-updater with logging support
- Checks for updates on application launch
- Handles update lifecycle events:
  - `checking-for-update` — Logs when checking begins
  - `update-available` — Logs when a new version is available
  - `update-not-available` — Logs when the app is up-to-date
  - `update-downloaded` — Shows user dialog asking to restart and install
  - `error` — Logs any update-related errors

### 2. **`src/main/index.ts`** - Main Process Integration
- Imports `initializeUpdater` from the updater module
- Calls `initializeUpdater()` on app launch (production builds only)
- Skips updater initialization in development mode

### 3. **`package.json`** - Dependencies & Configuration
Added:
- `electron-updater: ^6.0.0` — Handles automatic updates
- `electron-log: ^5.0.0` — Structured logging for update events
- `publish` configuration pointing to GitHub releases (customize as needed)

## How It Works

1. **On Launch**: When the app starts in production mode, `initializeUpdater()` is called
2. **Auto Check**: The updater immediately checks for new releases
3. **User Notification**: If an update is available:
   - A dialog appears: "Version X.X.X is ready to install"
   - User can choose "Restart Now" or "Later"
4. **Install**: If "Restart Now" is selected, the app quits and installs the update
5. **Logging**: All events are logged to help troubleshoot update issues

## Configuration

### Publish Provider
The `build.publish` section in `package.json` is configured for GitHub:
```json
"publish": {
  "provider": "github",
  "owner": "microsoft",
  "repo": "fru-selector"
}
```

**To use a different provider** (S3, Azure, etc.), update the `publish` section in `package.json`.

## Development

Updates are disabled in development mode to avoid interfering with local development workflows. To test updates:
1. Build a production release: `npm run build`
2. Start with `npm start`

## Logs

Update-related logs are written to:
- Windows: `%APPDATA%/FRU Selector/logs/main.log`
- macOS: `~/Library/Logs/FRU Selector/main.log`
- Linux: `~/.config/FRU Selector/logs/main.log`

## Building & Testing

```bash
# Install dependencies
npm install

# Build the main process
npm run build:main

# Build the full application
npm run build

# Start the application
npm start
```

## Future Enhancements

- Add progress indicator during downloads
- Allow users to view release notes before updating
- Implement staged rollouts for large user bases
- Add custom update server support
