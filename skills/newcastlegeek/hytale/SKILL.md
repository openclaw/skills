# Hytale Server Skill

Manage a local Hytale dedicated server using the official downloader and screen.

## Requirements
- Java 21+ (Installed)
- Screen (Installed)
- Hytale Downloader (User must provide)
- Credentials (User must provide `hytale-downloader-credentials.json` in `~/hytale_server`)

## Setup

1. **Download the Hytale Downloader:**
   - Get the zip from: `https://downloader.hytale.com/hytale-downloader.zip`
   - Unzip it and place `hytale-downloader-linux-amd64` in `~/hytale_server/`.
   - Make it executable: `chmod +x ~/hytale_server/hytale-downloader-linux-amd64`

2. **Add Credentials:**
   - Place your `hytale-downloader-credentials.json` in `~/hytale_server/`.

## Commands

### `hytale start`
Starts the server in a detached screen session.
- **Run:** `/home/clawd/.npm-global/lib/node_modules/clawdbot/skills/hytale/hytale.sh start`

### `hytale stop`
Gracefully stops the server.
- **Run:** `/home/clawd/.npm-global/lib/node_modules/clawdbot/skills/hytale/hytale.sh stop`

### `hytale update`
Downloads or updates the server files using the Hytale Downloader.
- **Run:** `/home/clawd/.npm-global/lib/node_modules/clawdbot/skills/hytale/hytale.sh update`

### `hytale status`
Checks if the server process is running.
- **Run:** `/home/clawd/.npm-global/lib/node_modules/clawdbot/skills/hytale/hytale.sh status`
