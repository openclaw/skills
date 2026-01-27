#!/usr/bin/env node
/**
 * security-monitor.cjs - Real-time security monitoring for Clawdbot
 * Usage: node monitor.js [--interval 60] [--daemon] [--threats=...]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const LOG_DIR = '/root/clawd/clawdbot-security/logs';
const STATE_FILE = '/root/clawd/clawdbot-security/.monitor-state.json';
const ALERT_LOG = path.join(LOG_DIR, 'alerts.log');

// State
let state = {
  lastCheck: Date.now(),
  failedLogins: {},
  apiCalls: {},
  portScans: {},
  alerts: []
};

// Load state
function loadState() {
  try {
    state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch {
    state = {
      lastCheck: Date.now(),
      failedLogins: {},
      apiCalls: {},
      portScans: {},
      alerts: []
    };
  }
}

// Save state
function saveState() {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// Logger
function log(level, message, details = {}) {
  const entry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    details
  };
  
  const logLine = JSON.stringify(entry);
  console.log(`[${entry.timestamp}] ${level}: ${message}`);
  
  // Write to alert log
  try {
    fs.appendFileSync(ALERT_LOG, logLine + '\n');
  } catch {
    // Ignore logging errors
  }
  
  // Store in state
  state.alerts.unshift(entry);
  state.alerts = state.alerts.slice(0, 100); // Keep last 100
  
  // Telegram alert on critical
  if (level === 'CRITICAL' || level === 'HIGH') {
    // TODO: Send Telegram alert
  }
}

// === MONITORS ===

function checkFailedLogins() {
  // Check auth logs for failed login attempts
  try {
    const authLog = execSync('tail -100 /var/log/auth.log 2>/dev/null || tail -100 /var/log/syslog 2>/dev/null || echo ""', 
      { encoding: 'utf8', timeout: 5000 });
    
    const failedPattern = /Failed password|Failed login|Authentication failure/gi;
    const matches = authLog.match(failedPattern) || [];
    
    const now = Date.now();
    const window = 3600000; // 1 hour
    
    for (const match of matches) {
      // Extract IP if possible
      const ipMatch = match.match(/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/);
      if (ipMatch) {
        const ip = ipMatch[0];
        state.failedLogins[ip] = state.failedLogins[ip] || [];
        state.failedLogins[ip].push(now);
        
        // Clean old entries
        state.failedLogins[ip] = state.failedLogins[ip].filter(t => now - t < window);
        
        // Alert on threshold
        if (state.failedLogins[ip].length >= 5) {
          log('HIGH', 'Brute force detection', { 
            ip, 
            attempts: state.failedLogins[ip].length,
            window: '1 hour'
          });
        }
      }
    }
  } catch {
    // Auth log not accessible - skip
  }
}

function checkOpenPorts() {
  // Quick port check - are expected ports still open?
  const expectedPorts = [22, 80, 443, 3000, 8080];
  
  try {
    const ssOutput = execSync('ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || echo ""', 
      { encoding: 'utf8', timeout: 5000 });
    
    const foundPorts = [];
    const portMatch = ssOutput.match(/:(\d+)\s/g);
    
    if (portMatch) {
      for (const p of portMatch) {
        const port = parseInt(p.replace(/[:\s]/g, ''));
        if (port > 0) foundPorts.push(port);
      }
    }
    
    // Check for unexpected ports
    const unexpected = foundPorts.filter(p => !expectedPorts.includes(p));
    
    if (unexpected.length > 0 && unexpected.length < foundPorts.length) {
      log('MEDIUM', 'Unexpected ports detected', { 
        unexpected: unexpected.slice(0, 10),
        expected: expectedPorts
      });
    }
  } catch {
    // Can't check ports - skip
  }
}

function checkProcessAnomalies() {
  // Check for unusual processes
  try {
    const psOutput = execSync('ps aux 2>/dev/null | grep -v "^USER" || echo ""', 
      { encoding: 'utf8', timeout: 5000 });
    
    const lines = psOutput.split('\n').filter(l => l.trim());
    const processCount = lines.length;
    
    // Alert if significantly more processes than usual
    if (state.lastProcessCount && processCount > state.lastProcessCount * 1.5) {
      log('MEDIUM', 'Process count spike detected', {
        current: processCount,
        previous: state.lastProcessCount,
        increase: `${Math.round((processCount - state.lastProcessCount) / state.lastProcessCount * 100)}%`
      });
    }
    
    state.lastProcessCount = processCount;
  } catch {
    // Can't check processes
  }
}

function checkFileChanges() {
  // Check for unexpected file changes
  const watchPaths = [
    '/root/clawd/skills/.env',
    '/root/clawd/config',
    '/root/clawd/.env'
  ];
  
  for (const watchPath of watchPaths) {
    try {
      const stats = fs.statSync(watchPath);
      const mtime = stats.mtimeMs;
      
      if (state.lastMtimes && state.lastMtimes[watchPath]) {
        if (mtime > state.lastMtimes[watchPath] && mtime > state.lastCheck) {
          log('HIGH', 'File modified', {
            file: watchPath,
            time: new Date(mtime).toISOString()
          });
        }
      }
      
      state.lastMtimes = state.lastMtimes || {};
      state.lastMtimes[watchPath] = mtime;
    } catch {
      // File doesn't exist - skip
    }
  }
}

function checkApiKeyUsage() {
  // Check for unusual API key usage patterns
  // This is a simplified check - real implementation would need API integration
  
  try {
    const envContent = fs.readFileSync('/root/clawd/skills/.env', 'utf8');
    
    if (envContent.includes('TWITTER') || envContent.includes('KAPSO')) {
      log('INFO', 'API credentials present', {
        services: envContent.match(/(?:TWITTER|KAPSO|WHATSAPP)/g) || []
      });
    }
  } catch {
    // Can't read env
  }
}

function checkDockerHealth() {
  // Check Docker container health
  try {
    const dockerPs = execSync('docker ps --format json 2>/dev/null || docker ps 2>/dev/null || echo ""', 
      { encoding: 'utf8', timeout: 5000 });
    
    if (dockerPs.includes('unhealthy') || dockerPs.includes('Exited')) {
      log('MEDIUM', 'Container issue detected', {
        status: dockerPs.includes('unhealthy') ? 'unhealthy' : 'exited'
      });
    }
  } catch {
    // Docker not available
  }
}

// === MAIN ===

async function runMonitor(options = {}) {
  const { 
    interval = 60, 
    daemon = false,
    threats = 'all',
    logPath = ALERT_LOG
  } = options;
  
  // Ensure log directory exists
  if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
  }
  
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║       CLAWDBOT SECURITY MONITOR v1.0                       ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
  
  console.log(`Monitoring interval: ${interval}s`);
  console.log(`Threats: ${threats}`);
  console.log(`Alert log: ${ALERT_LOG}\n`);
  
  if (daemon) {
    console.log('Running in daemon mode. Press Ctrl+C to stop.\n');
  }
  
  loadState();
  
  const runChecks = () => {
    const now = Date.now();
    console.log(`\n[${new Date().toISOString()}] Running security checks...`);
    
    checkFailedLogins();
    checkOpenPorts();
    checkProcessAnomalies();
    checkFileChanges();
    checkApiKeyUsage();
    checkDockerHealth();
    
    state.lastCheck = now;
    saveState();
    
    const alertCount = state.alerts.filter(a => 
      new Date(a.timestamp).getTime() > now - 3600000
    ).length;
    
    console.log(`[${new Date().toISOString()}] Checks complete. ${alertCount} alerts in last hour.`);
  };
  
  // Initial run
  runChecks();
  
  if (daemon) {
    // Continuous monitoring
    setInterval(runChecks, interval * 1000);
  }
}

// Run if called directly
if (require.main === module) {
  const args = process.argv.slice(2);
  
  const options = {
    interval: parseInt(args.find(a => a.startsWith('--interval='))?.[1] ||
                  args.find(a => a.startsWith('--interval '))?.[1] || '60'),
    daemon: args.includes('--daemon'),
    threats: args.find(a => a.startsWith('--threats='))?.[1] || 'all'
  };
  
  runMonitor(options).catch(e => {
    console.error('Monitor error:', e.message);
    process.exit(1);
  });
}

module.exports = { runMonitor, checkFailedLogins, checkOpenPorts, checkProcessAnomalies, checkFileChanges };
