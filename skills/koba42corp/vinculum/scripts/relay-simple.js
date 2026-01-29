#!/usr/bin/env node
/**
 * Simple Gun relay using Gun's native server module
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const DATA_DIR = process.env.CLAWDBOT_DATA_DIR ||
  path.join(process.env.HOME, '.local', 'share', 'clawdbot', 'vinculum');
const PID_FILE = path.join(DATA_DIR, 'relay.pid');
const LOG_FILE = path.join(DATA_DIR, 'relay.log');

const PORT = parseInt(process.argv[2]) || 8765;

// Ensure data dir exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Suppress Gun's welcome message by patching console.log temporarily
const origLog = console.log;
let suppressWelcome = true;
console.log = function(...args) {
  if (suppressWelcome && args[0] && typeof args[0] === 'string' && 
      (args[0].includes('Hello wonderful') || args[0].includes('AXE relay'))) {
    return;
  }
  origLog.apply(console, args);
};

// Create HTTP server
const server = http.createServer((req, res) => {
  if (req.url === '/health' || req.url === '/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      uptime: process.uptime() * 1000,
      port: PORT
    }));
    return;
  }
  res.writeHead(200);
  res.end('Vinculum Relay');
});

// Use Gun's native server module - this properly handles WebSockets
const Gun = require('gun');
require('gun/axe'); // Enable peer discovery

const gun = Gun({
  web: server,
  file: path.join(DATA_DIR, 'relay-data'),
  axe: true
});

// Re-enable normal logging
suppressWelcome = false;

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  fs.appendFileSync(LOG_FILE, line);
  if (process.env.GUN_RELAY_FOREGROUND) {
    process.stdout.write(line);
  }
}

// Start server
server.listen(PORT, '0.0.0.0', () => {
  fs.writeFileSync(PID_FILE, String(process.pid));
  
  log(`Relay started on port ${PORT}`);
  log(`PID: ${process.pid}`);
  log(`Data: ${DATA_DIR}`);
  
  console.log(`Gun relay running on port ${PORT} (PID ${process.pid})`);
});

// Handle shutdown
process.on('SIGTERM', () => {
  log('Stopping relay...');
  server.close();
  if (fs.existsSync(PID_FILE)) fs.unlinkSync(PID_FILE);
  process.exit(0);
});

process.on('SIGINT', () => {
  log('Stopping relay...');
  server.close();
  if (fs.existsSync(PID_FILE)) fs.unlinkSync(PID_FILE);
  process.exit(0);
});

// Keep alive
setInterval(() => {}, 60000);
