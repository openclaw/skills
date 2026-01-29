/**
 * Vinculum Skill for Clawdbot
 * Shared consciousness between bot instances
 * 
 * @module vinculum
 */

const fs = require('fs');
const path = require('path');
const yaml = require('yaml');
const GunAdapter = require('./gun-adapter');
const commands = require('./commands');

// Default config path
const CONFIG_DIR = process.env.CLAWDBOT_CONFIG_DIR || 
  path.join(process.env.HOME, '.config', 'clawdbot');
const CONFIG_FILE = path.join(CONFIG_DIR, 'vinculum.yaml');

// Load default config
const DEFAULTS_FILE = path.join(__dirname, '..', 'config', 'defaults.yaml');

/**
 * Simple YAML config manager
 */
class ConfigManager {
  constructor(configPath) {
    this.configPath = configPath;
    this.config = null;
  }
  
  async load() {
    // Load defaults
    let defaults = {};
    if (fs.existsSync(DEFAULTS_FILE)) {
      defaults = yaml.parse(fs.readFileSync(DEFAULTS_FILE, 'utf8'));
    }
    
    // Load user config
    let userConfig = {};
    if (fs.existsSync(this.configPath)) {
      userConfig = yaml.parse(fs.readFileSync(this.configPath, 'utf8'));
    }
    
    this.config = { ...defaults, ...userConfig };
    return this.config;
  }
  
  async get() {
    if (!this.config) {
      await this.load();
    }
    return this.config;
  }
  
  async set(updates) {
    if (!this.config) {
      await this.load();
    }
    
    this.config = { ...this.config, ...updates };
    
    // Ensure directory exists
    const dir = path.dirname(this.configPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    // Write config
    fs.writeFileSync(this.configPath, yaml.stringify(this.config));
    
    return this.config;
  }
}

/**
 * Vinculum skill instance - the collective consciousness
 */
class Vinculum {
  constructor() {
    this.adapter = new GunAdapter();
    this.configManager = new ConfigManager(CONFIG_FILE);
    this.linkState = {
      lastPush: null,
      lastPull: null,
      logs: []
    };
    this.initialized = false;
  }
  
  /**
   * Initialize the Vinculum
   * @param {Object} context - Clawdbot context
   */
  async init(context = {}) {
    if (this.initialized) return;
    
    // Load config
    const config = await this.configManager.get();
    
    // Resolve data directory
    const dataDir = (config.data_dir || '~/.local/share/clawdbot/vinculum')
      .replace(/^~/, process.env.HOME);
    
    // Ensure data directory exists
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
    
    // Auto-start relay if configured
    if (config.relay?.auto_start) {
      await this._ensureRelayRunning(config);
    }
    
    // Build peer list (include local relay if running)
    const peers = [...(config.peers || [])];
    const relayPort = config.relay?.port || 8765;
    const localRelay = `http://localhost:${relayPort}/gun`;
    if (!peers.includes(localRelay) && this._isRelayRunning()) {
      peers.unshift(localRelay);
    }
    
    // Initialize adapter
    await this.adapter.init({
      peers,
      file: path.join(dataDir, 'collective-data'),
      localStorage: false,
      radisk: true,
      axe: true  // Enable local network discovery
    });
    
    // Auto-connect if configured
    if (config.enabled && config.namespace && config.encryption_key) {
      try {
        await this.adapter.connect(config.namespace, config.encryption_key, {
          name: config.drone_name || config.agent_name || 'Drone',
          instanceId: context.instanceId || generateInstanceId(),
          owner: context.owner || 'unknown',
          channel: context.channel || 'unknown'
        });
        this.log('info', `Linked to collective: ${config.namespace}`);
      } catch (err) {
        this.log('error', `Failed to link: ${err.message}`);
      }
    }
    
    this.initialized = true;
  }
  
  /**
   * Check if relay is running
   */
  _isRelayRunning() {
    const pidFile = path.join(
      process.env.HOME, '.local', 'share', 'clawdbot', 'vinculum', 'relay.pid'
    );
    if (!fs.existsSync(pidFile)) return false;
    
    try {
      const pid = parseInt(fs.readFileSync(pidFile, 'utf8'));
      process.kill(pid, 0);
      return true;
    } catch {
      return false;
    }
  }
  
  /**
   * Ensure relay is running
   */
  async _ensureRelayRunning(config) {
    if (this._isRelayRunning()) return;
    
    const port = config.relay?.port || 8765;
    const relayScript = path.join(__dirname, 'relay-simple.js');
    
    try {
      const { spawn } = require('child_process');
      const child = spawn('node', [relayScript, String(port)], {
        detached: true,
        stdio: 'ignore'
      });
      child.unref();
      
      // Wait for startup
      await new Promise(r => setTimeout(r, 1500));
      this.log('info', `Auto-started Vinculum relay on port ${port}`);
    } catch (err) {
      this.log('error', `Failed to auto-start relay: ${err.message}`);
    }
  }
  
  /**
   * Handle a /link command
   * @param {string} input - Full command input
   * @param {Object} context - Execution context
   * @returns {Promise<string>} Response message
   */
  async handleCommand(input, context = {}) {
    // Ensure initialized
    await this.init(context);
    
    // Build command context
    const cmdContext = {
      adapter: this.adapter,
      configManager: this.configManager,
      syncState: this.linkState,
      instanceId: context.instanceId || generateInstanceId(),
      owner: context.owner || 'unknown',
      channel: context.channel || 'telegram'
    };
    
    try {
      return await commands.handleCommand(input, cmdContext);
    } catch (err) {
      this.log('error', `Command error: ${err.message}`);
      return `❌ **Error**\n\n${err.message}`;
    }
  }
  
  /**
   * Log an activity to the collective
   * @param {Object} activity
   */
  async logActivity(activity) {
    const config = await this.configManager.get();
    
    if (!config.enabled || !config.share?.activity) {
      return;
    }
    
    if (this.adapter.connected) {
      await this.adapter.logActivity(activity);
      this.linkState.lastPush = Date.now();
    }
  }
  
  /**
   * Share a memory with the collective
   * @param {Object} memory
   */
  async shareMemory(memory) {
    const config = await this.configManager.get();
    
    if (!config.enabled || !config.share?.memory) {
      return;
    }
    
    if (this.adapter.connected) {
      await this.adapter.shareMemory(memory);
      this.linkState.lastPush = Date.now();
    }
  }
  
  /**
   * Record a collective decision
   * @param {Object} decision
   */
  async recordDecision(decision) {
    const config = await this.configManager.get();
    
    if (!config.enabled || !config.share?.decisions) {
      return;
    }
    
    if (this.adapter.connected) {
      await this.adapter.recordDecision(decision);
      this.linkState.lastPush = Date.now();
    }
  }
  
  /**
   * Update current task status
   * @param {string} task
   */
  async updateTask(task) {
    if (this.adapter.connected) {
      await this.adapter.updateAgentStatus({ 
        online: true,
        current_task: task 
      });
    }
  }
  
  /**
   * Get activity from other drones
   * @param {number} limit
   * @returns {Promise<Array>}
   */
  async getCollectiveActivity(limit = 20) {
    if (!this.adapter.connected) return [];
    return this.adapter.getActivity(limit);
  }
  
  /**
   * Get connected drones
   * @returns {Promise<Array>}
   */
  async getDrones() {
    if (!this.adapter.connected) return [];
    const agents = await this.adapter.getAgents();
    return agents.filter(a => a.id !== this.adapter.agentId);
  }
  
  /**
   * Add a log entry
   * @param {string} level
   * @param {string} message
   */
  log(level, message) {
    this.linkState.logs.push({
      timestamp: Date.now(),
      level,
      message
    });
    
    // Keep only last 100 logs
    if (this.linkState.logs.length > 100) {
      this.linkState.logs = this.linkState.logs.slice(-100);
    }
  }
  
  /**
   * Disconnect from the collective
   */
  async disconnect() {
    if (this.adapter.connected) {
      await this.adapter.disconnect();
    }
  }
}

/**
 * Generate a unique drone ID
 * @returns {string}
 */
function generateInstanceId() {
  const hostname = require('os').hostname();
  const random = Math.random().toString(36).substr(2, 6);
  return `${hostname}-${random}`;
}

// Export singleton instance
const vinculum = new Vinculum();

module.exports = vinculum;
module.exports.Vinculum = Vinculum;
module.exports.GunAdapter = GunAdapter;
module.exports.ConfigManager = ConfigManager;
