#!/usr/bin/env node
/**
 * Gun Relay Daemon for local network sync
 * Runs as a background service for peer-to-peer sync
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// For the relay, we need full Gun with WebSocket support
// Suppress the welcome message
const originalLog = console.log;
console.log = function(...args) {
  if (args[0] && typeof args[0] === 'string' && args[0].includes('Hello wonderful person')) {
    return;
  }
  originalLog.apply(console, args);
};

// Use Gun's server entry point which has better WS support
let Gun;
try {
  // Try the server build first
  Gun = require('gun/gun');
} catch {
  // Fall back to loader if needed
  Gun = require('./gun-loader');
}

// Config paths
const CONFIG_DIR = process.env.CLAWDBOT_CONFIG_DIR || 
  path.join(process.env.HOME, '.config', 'clawdbot');
const DATA_DIR = process.env.CLAWDBOT_DATA_DIR ||
  path.join(process.env.HOME, '.local', 'share', 'clawdbot', 'gun-sync');
const PID_FILE = path.join(DATA_DIR, 'relay.pid');
const LOG_FILE = path.join(DATA_DIR, 'relay.log');

// Default config
const DEFAULT_PORT = 8765;
const DEFAULT_MULTICAST = '233.255.255.255';

class RelayDaemon {
  constructor(options = {}) {
    this.port = options.port || DEFAULT_PORT;
    this.multicast = options.multicast || DEFAULT_MULTICAST;
    this.dataDir = options.dataDir || DATA_DIR;
    this.server = null;
    this.gun = null;
    this.startTime = null;
    this.connections = 0;
  }

  log(level, message) {
    const timestamp = new Date().toISOString();
    const line = `[${timestamp}] [${level.toUpperCase()}] ${message}\n`;
    
    // Write to log file
    fs.appendFileSync(LOG_FILE, line);
    
    // Also console if not daemonized
    if (process.env.GUN_RELAY_FOREGROUND) {
      process.stdout.write(line);
    }
  }

  async start() {
    // Ensure directories exist
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }

    // Check if already running
    if (fs.existsSync(PID_FILE)) {
      const oldPid = parseInt(fs.readFileSync(PID_FILE, 'utf8'));
      try {
        process.kill(oldPid, 0); // Check if process exists
        console.log(`Relay already running (PID ${oldPid})`);
        process.exit(1);
      } catch (e) {
        // Process doesn't exist, clean up stale PID file
        fs.unlinkSync(PID_FILE);
      }
    }

    // Create HTTP server for WebSocket relay
    this.server = http.createServer((req, res) => {
      // Health check endpoint
      if (req.url === '/health' || req.url === '/status') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          status: 'ok',
          uptime: Date.now() - this.startTime,
          connections: this.connections,
          port: this.port
        }));
        return;
      }
      
      // Gun handles WebSocket upgrades
      res.writeHead(200);
      res.end('Gun Relay Server');
    });

    // Initialize Gun with relay settings
    this.gun = Gun({
      web: this.server,
      file: path.join(this.dataDir, 'relay-data'),
      radisk: true,
      localStorage: false,
      axe: true,  // Enable AXE for peer discovery
      multicast: {
        addr: this.multicast,
        port: this.port
      }
    });

    // Track connections
    this.server.on('connection', () => {
      this.connections++;
      this.log('info', `New connection (total: ${this.connections})`);
    });

    // Start listening
    return new Promise((resolve, reject) => {
      this.server.listen(this.port, '0.0.0.0', () => {
        this.startTime = Date.now();
        
        // Write PID file
        fs.writeFileSync(PID_FILE, String(process.pid));
        
        this.log('info', `Gun relay started on port ${this.port}`);
        this.log('info', `Multicast: ${this.multicast}:${this.port}`);
        this.log('info', `Data dir: ${this.dataDir}`);
        this.log('info', `PID: ${process.pid}`);
        
        resolve();
      });

      this.server.on('error', (err) => {
        this.log('error', `Server error: ${err.message}`);
        reject(err);
      });
    });
  }

  async stop() {
    this.log('info', 'Stopping relay...');
    
    if (this.server) {
      this.server.close();
    }
    
    if (fs.existsSync(PID_FILE)) {
      fs.unlinkSync(PID_FILE);
    }
    
    this.log('info', 'Relay stopped');
  }

  static getStatus() {
    if (!fs.existsSync(PID_FILE)) {
      return { running: false };
    }

    const pid = parseInt(fs.readFileSync(PID_FILE, 'utf8'));
    
    try {
      process.kill(pid, 0);
      return { running: true, pid };
    } catch (e) {
      // Stale PID file
      fs.unlinkSync(PID_FILE);
      return { running: false };
    }
  }

  static async stopRunning() {
    const status = RelayDaemon.getStatus();
    if (!status.running) {
      return false;
    }

    try {
      process.kill(status.pid, 'SIGTERM');
      // Wait for it to stop
      await new Promise(r => setTimeout(r, 1000));
      return true;
    } catch (e) {
      return false;
    }
  }

  static getLogs(lines = 50) {
    if (!fs.existsSync(LOG_FILE)) {
      return [];
    }
    
    const content = fs.readFileSync(LOG_FILE, 'utf8');
    return content.split('\n').filter(Boolean).slice(-lines);
  }
}

// CLI handling
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'start';

  switch (command) {
    case 'start': {
      const port = parseInt(args[1]) || DEFAULT_PORT;
      const daemon = new RelayDaemon({ port });
      
      // Handle shutdown
      process.on('SIGTERM', () => daemon.stop().then(() => process.exit(0)));
      process.on('SIGINT', () => daemon.stop().then(() => process.exit(0)));
      
      await daemon.start();
      console.log(`Gun relay running on port ${port}`);
      
      // Keep process alive with a heartbeat timer
      setInterval(() => {
        // Just keep the event loop alive
      }, 60000);
      break;
    }

    case 'stop': {
      const stopped = await RelayDaemon.stopRunning();
      console.log(stopped ? 'Relay stopped' : 'Relay not running');
      process.exit(0);
    }

    case 'status': {
      const status = RelayDaemon.getStatus();
      if (status.running) {
        console.log(`Relay running (PID ${status.pid})`);
        
        // Try to get health info
        try {
          const http = require('http');
          const req = http.get(`http://localhost:${DEFAULT_PORT}/health`, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
              const info = JSON.parse(data);
              console.log(`Uptime: ${Math.floor(info.uptime / 1000)}s`);
              console.log(`Connections: ${info.connections}`);
              process.exit(0);
            });
          });
          req.on('error', () => process.exit(0));
        } catch (e) {
          process.exit(0);
        }
      } else {
        console.log('Relay not running');
        process.exit(0);
      }
      break;
    }

    case 'logs': {
      const lines = parseInt(args[1]) || 50;
      const logs = RelayDaemon.getLogs(lines);
      logs.forEach(line => console.log(line));
      process.exit(0);
    }

    case 'restart': {
      await RelayDaemon.stopRunning();
      await new Promise(r => setTimeout(r, 500));
      const daemon = new RelayDaemon();
      await daemon.start();
      console.log('Relay restarted');
      break;
    }

    default:
      console.log(`
Gun Relay Daemon

Usage:
  relay-daemon start [port]   Start the relay (default port: 8765)
  relay-daemon stop           Stop the relay
  relay-daemon status         Check relay status
  relay-daemon logs [n]       Show last n log lines
  relay-daemon restart        Restart the relay
`);
      process.exit(0);
  }
}

// Export for programmatic use
module.exports = RelayDaemon;

// Run if executed directly
if (require.main === module) {
  main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
}
