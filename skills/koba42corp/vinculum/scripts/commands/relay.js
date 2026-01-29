/**
 * Relay commands for vinculum
 * Manages the local relay daemon
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');
const formatting = require('../utils/formatting');

const RELAY_SCRIPT = path.join(__dirname, '..', 'relay-simple.js');
const DATA_DIR = process.env.CLAWDBOT_DATA_DIR ||
  path.join(process.env.HOME, '.local', 'share', 'clawdbot', 'vinculum');
const PID_FILE = path.join(DATA_DIR, 'relay.pid');

/**
 * Get relay status
 */
function getRelayStatus() {
  if (!fs.existsSync(PID_FILE)) {
    return { running: false };
  }

  const pid = parseInt(fs.readFileSync(PID_FILE, 'utf8'));
  
  try {
    process.kill(pid, 0);
    return { running: true, pid };
  } catch (e) {
    // Stale PID file
    try { fs.unlinkSync(PID_FILE); } catch {}
    return { running: false };
  }
}

/**
 * Get relay health info
 */
async function getRelayHealth(port = 8765) {
  return new Promise((resolve) => {
    const req = http.get(`http://localhost:${port}/health`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve(null);
        }
      });
    });
    req.on('error', () => resolve(null));
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(null);
    });
  });
}

/**
 * Start the relay daemon
 */
async function startRelay(context) {
  const { configManager } = context;
  const config = await configManager.get();
  
  const status = getRelayStatus();
  if (status.running) {
    return formatting.formatWarning(
      `Relay already running (PID ${status.pid})\n\n` +
      `Use \`/link relay restart\` to restart.`
    );
  }

  const port = config.relay?.port || 8765;
  
  // Ensure data directory exists
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }

  // Start the relay in background
  const child = spawn('node', [RELAY_SCRIPT, 'start', String(port)], {
    detached: true,
    stdio: 'ignore',
    env: { ...process.env, GUN_RELAY_FOREGROUND: '' }
  });
  
  child.unref();

  // Wait for it to start
  await new Promise(r => setTimeout(r, 1500));
  
  const newStatus = getRelayStatus();
  if (newStatus.running) {
    // Update config with relay info
    await configManager.set({
      relay: {
        ...config.relay,
        port,
        auto_start: true
      },
      peers: [`http://localhost:${port}/gun`]
    });
    
    return formatting.formatSuccess(
      `Relay started on port ${port}\n\n` +
      `• PID: ${newStatus.pid}\n` +
      `• Local URL: \`http://localhost:${port}/gun\`\n` +
      `• Multicast: enabled for local network\n\n` +
      `Other devices can connect using:\n` +
      `\`/link config relay-peer http://<your-ip>:${port}/gun\``
    );
  } else {
    return formatting.formatError(
      `Failed to start relay. Check logs with \`/link relay logs\``
    );
  }
}

/**
 * Stop the relay daemon
 */
async function stopRelay(context) {
  const status = getRelayStatus();
  
  if (!status.running) {
    return formatting.formatWarning(`Relay is not running.`);
  }

  try {
    process.kill(status.pid, 'SIGTERM');
    await new Promise(r => setTimeout(r, 1000));
    
    // Verify it stopped
    const newStatus = getRelayStatus();
    if (!newStatus.running) {
      return formatting.formatSuccess(`Relay stopped.`);
    } else {
      // Force kill
      process.kill(status.pid, 'SIGKILL');
      return formatting.formatSuccess(`Relay force-stopped.`);
    }
  } catch (e) {
    return formatting.formatError(`Failed to stop relay: ${e.message}`);
  }
}

/**
 * Restart the relay
 */
async function restartRelay(context) {
  await stopRelay(context);
  await new Promise(r => setTimeout(r, 500));
  return startRelay(context);
}

/**
 * Show relay status
 */
async function relayStatus(context) {
  const { configManager } = context;
  const config = await configManager.get();
  const port = config.relay?.port || 8765;
  
  const status = getRelayStatus();
  
  if (!status.running) {
    return `📡 **Relay Status**\n\n` +
      `Status: 🔴 Not running\n\n` +
      `Start with \`/link relay start\``;
  }

  const health = await getRelayHealth(port);
  
  let response = `📡 **Relay Status**\n\n` +
    `Status: 🟢 Running\n` +
    `PID: ${status.pid}\n` +
    `Port: ${port}\n`;

  if (health) {
    const uptime = Math.floor(health.uptime / 1000);
    const hours = Math.floor(uptime / 3600);
    const mins = Math.floor((uptime % 3600) / 60);
    const secs = uptime % 60;
    
    response += `Uptime: ${hours}h ${mins}m ${secs}s\n`;
    response += `Connections: ${health.connections}\n`;
  }

  response += `\n**Local Network**\n`;
  response += `• Multicast: enabled\n`;
  response += `• URL: \`http://localhost:${port}/gun\`\n`;

  // Get local IP for network info
  try {
    const nets = require('os').networkInterfaces();
    for (const name of Object.keys(nets)) {
      for (const net of nets[name]) {
        if (net.family === 'IPv4' && !net.internal) {
          response += `• LAN: \`http://${net.address}:${port}/gun\`\n`;
          break;
        }
      }
    }
  } catch {}

  return response;
}

/**
 * Show relay logs
 */
async function relayLogs(lines, context) {
  const LOG_FILE = path.join(DATA_DIR, 'relay.log');
  
  if (!fs.existsSync(LOG_FILE)) {
    return formatting.formatWarning(`No relay logs found.`);
  }
  
  const count = parseInt(lines) || 20;
  const content = fs.readFileSync(LOG_FILE, 'utf8');
  const logLines = content.split('\n').filter(Boolean).slice(-count);
  
  if (logLines.length === 0) {
    return formatting.formatWarning(`Relay log is empty.`);
  }
  
  return `📋 **Relay Logs** (last ${logLines.length})\n\n` +
    '```\n' + logLines.join('\n') + '\n```';
}

/**
 * Configure relay port
 */
async function setRelayPort(port, context) {
  const { configManager } = context;
  
  const portNum = parseInt(port);
  if (isNaN(portNum) || portNum < 1024 || portNum > 65535) {
    return formatting.formatError(
      `Invalid port. Must be between 1024 and 65535.`
    );
  }

  const config = await configManager.get();
  await configManager.set({
    relay: { ...config.relay, port: portNum }
  });

  const status = getRelayStatus();
  if (status.running) {
    return formatting.formatSuccess(
      `Relay port set to ${portNum}.\n\n` +
      `Restart relay with \`/link relay restart\` to apply.`
    );
  }
  
  return formatting.formatSuccess(`Relay port set to ${portNum}.`);
}

/**
 * Add a remote peer
 */
async function addPeer(url, context) {
  const { configManager } = context;
  
  if (!url || !url.startsWith('http')) {
    return formatting.formatError(
      `Invalid peer URL. Must be http:// or https://\n\n` +
      `Example: \`/link relay peer http://192.168.1.100:8765/gun\``
    );
  }

  const config = await configManager.get();
  const peers = config.peers || [];
  
  if (peers.includes(url)) {
    return formatting.formatWarning(`Peer already configured: ${url}`);
  }

  peers.push(url);
  await configManager.set({ peers });

  return formatting.formatSuccess(
    `Added peer: ${url}\n\n` +
    `Reconnect with \`/link off\` then \`/link on\` to use new peer.`
  );
}

/**
 * Remove a peer
 */
async function removePeer(url, context) {
  const { configManager } = context;
  const config = await configManager.get();
  
  const peers = (config.peers || []).filter(p => p !== url);
  await configManager.set({ peers });

  return formatting.formatSuccess(`Removed peer: ${url}`);
}

/**
 * List peers
 */
async function listPeers(context) {
  const { configManager } = context;
  const config = await configManager.get();
  
  const peers = config.peers || [];
  
  if (peers.length === 0) {
    return `📡 **Configured Peers**\n\n` +
      `No peers configured.\n\n` +
      `Add with \`/link relay peer <url>\``;
  }

  return `📡 **Configured Peers**\n\n` +
    peers.map(p => `• ${p}`).join('\n');
}

module.exports = {
  startRelay,
  stopRelay,
  restartRelay,
  relayStatus,
  relayLogs,
  setRelayPort,
  addPeer,
  removePeer,
  listPeers,
  getRelayStatus
};
