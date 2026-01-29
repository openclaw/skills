/**
 * Gun.js adapter for Clawdbot context sharing
 * Handles connection, encryption, and data sync
 * 
 * Note: Uses flat keys and set() for VM loader compatibility with Node v22+
 */

const Gun = require('./gun-loader');
const schema = require('./utils/schema');

class GunAdapter {
  constructor(config = {}) {
    this.config = {
      peers: config.peers || [],
      localStorage: config.localStorage !== false,
      radisk: config.radisk !== false,
      ...config
    };
    
    this.gun = null;
    this.namespaceId = null;
    this.encryptionKey = null;
    this.agentId = null;
    this.agentName = null;
    this.connected = false;
    this.listeners = new Map();
  }

  /**
   * Initialize Gun instance
   */
  async init(options = {}) {
    const gunOptions = {
      peers: this.config.peers,
      localStorage: this.config.localStorage,
      radisk: this.config.radisk,
      axe: false, // Disable multicast for cleaner operation
      ...options
    };

    this.gun = Gun(gunOptions);
    return this;
  }

  /**
   * Build a flat key for this namespace
   */
  key(...parts) {
    return `cbot:${this.namespaceId}:${parts.join(':')}`;
  }

  /**
   * Get a node by flat key
   */
  node(...parts) {
    return this.gun.get(this.key(...parts));
  }

  /**
   * Connect to a namespace with encryption key
   */
  async connect(namespaceId, encryptionKey, agentInfo) {
    if (!this.gun) {
      await this.init();
    }

    this.namespaceId = namespaceId;
    this.encryptionKey = encryptionKey;
    this.agentId = agentInfo.instanceId;
    this.agentName = agentInfo.name;

    // Register this agent
    await this.registerAgent(agentInfo);
    
    this.connected = true;
    this._startHeartbeat();
    
    return this;
  }

  /**
   * Disconnect from the network
   */
  async disconnect() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    
    if (this.namespaceId && this.agentId) {
      await this.updateAgentStatus({ online: false });
    }
    
    this.connected = false;
  }

  /**
   * Register this agent in the network
   */
  async registerAgent(agentInfo) {
    const identity = schema.createAgentIdentity(agentInfo);
    const status = schema.createAgentStatus({ online: true });

    // Store agent identity (flat key)
    this.node('agent', this.agentId).put({
      ...identity,
      ...status,
      type: 'agent'
    });

    // Add to agents collection using set()
    this.gun.get(this.key('agents')).set({
      id: this.agentId,
      name: agentInfo.name,
      added: Date.now()
    });
    
    await new Promise(r => setTimeout(r, 100));
  }

  /**
   * Update agent status
   */
  async updateAgentStatus(statusUpdate) {
    const status = {
      online: statusUpdate.online ? 1 : 0,
      current_task: statusUpdate.currentTask || '',
      task_started: statusUpdate.currentTask ? Date.now() : 0,
      updated: Date.now()
    };

    this.node('agent', this.agentId).put(status);
    await new Promise(r => setTimeout(r, 50));
  }

  /**
   * Log an activity
   */
  async logActivity(activityData) {
    const entry = schema.createActivityEntry({
      agent: this.agentName,
      ...activityData
    });

    // Store entry data
    this.node('activity', entry.id).put(entry);
    
    // Add to activity collection
    this.gun.get(this.key('activities')).set({
      id: entry.id,
      agent: entry.agent,
      timestamp: entry.timestamp
    });

    await new Promise(r => setTimeout(r, 50));
    return entry;
  }

  /**
   * Share a memory entry
   */
  async shareMemory(memoryData) {
    const entry = schema.createMemoryEntry({
      learnedBy: this.agentName,
      ...memoryData
    });

    this.node('memory', entry.id).put(entry);
    this.gun.get(this.key('memories')).set({
      id: entry.id,
      learned_by: entry.learned_by,
      timestamp: entry.timestamp
    });

    await new Promise(r => setTimeout(r, 50));
    return entry;
  }

  /**
   * Record a decision
   */
  async recordDecision(decisionData) {
    const entry = schema.createDecisionEntry({
      decidedBy: this.agentName,
      ...decisionData
    });

    this.node('decision', entry.id).put(entry);
    this.gun.get(this.key('decisions')).set({
      id: entry.id,
      topic: entry.topic,
      timestamp: entry.timestamp
    });

    await new Promise(r => setTimeout(r, 50));
    return entry;
  }

  /**
   * Send a message to another agent
   */
  async sendMessage(messageData) {
    const entry = schema.createMessage({
      from: this.agentName,
      ...messageData
    });

    this.node('message', entry.id).put(entry);
    this.gun.get(this.key('messages')).set({
      id: entry.id,
      from: entry.from,
      to: entry.to,
      timestamp: entry.timestamp
    });

    await new Promise(r => setTimeout(r, 50));
    return entry;
  }

  /**
   * Get all agents in the network
   */
  async getAgents() {
    return new Promise((resolve) => {
      const agents = [];
      const seen = new Set();
      
      this.gun.get(this.key('agents')).map().once((data, key) => {
        if (data && key !== '_' && data.id && !seen.has(data.id)) {
          seen.add(data.id);
          // Fetch full agent data
          this.node('agent', data.id).once(agent => {
            if (agent) {
              agents.push({ id: data.id, ...agent });
            }
          });
        }
      });

      setTimeout(() => resolve(agents), 600);
    });
  }

  /**
   * Get recent activity
   */
  async getActivity(limit = 20, agentFilter = null) {
    return new Promise((resolve) => {
      const activities = [];
      const seen = new Set();
      
      this.gun.get(this.key('activities')).map().once((ref, key) => {
        if (ref && key !== '_' && ref.id && !seen.has(ref.id)) {
          seen.add(ref.id);
          this.node('activity', ref.id).once(data => {
            if (data && (!agentFilter || data.agent === agentFilter)) {
              activities.push(data);
            }
          });
        }
      });

      setTimeout(() => {
        activities.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
        resolve(activities.slice(0, limit));
      }, 600);
    });
  }

  /**
   * Get shared memories
   */
  async getMemories(limit = 50) {
    return new Promise((resolve) => {
      const memories = [];
      const seen = new Set();
      
      this.gun.get(this.key('memories')).map().once((ref, key) => {
        if (ref && key !== '_' && ref.id && !seen.has(ref.id)) {
          seen.add(ref.id);
          this.node('memory', ref.id).once(data => {
            if (data) memories.push(data);
          });
        }
      });

      setTimeout(() => {
        memories.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
        resolve(memories.slice(0, limit));
      }, 600);
    });
  }

  /**
   * Get shared decisions
   */
  async getDecisions() {
    return new Promise((resolve) => {
      const decisions = [];
      const seen = new Set();
      
      this.gun.get(this.key('decisions')).map().once((ref, key) => {
        if (ref && key !== '_' && ref.id && !seen.has(ref.id)) {
          seen.add(ref.id);
          this.node('decision', ref.id).once(data => {
            if (data) decisions.push(data);
          });
        }
      });

      setTimeout(() => {
        decisions.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
        resolve(decisions);
      }, 600);
    });
  }

  /**
   * Subscribe to activity updates
   */
  onActivity(callback) {
    this.gun.get(this.key('activities')).map().on((ref, key) => {
      if (ref && key !== '_' && ref.id) {
        this.node('activity', ref.id).once(data => {
          if (data && data.agent !== this.agentName) {
            callback(data);
          }
        });
      }
    });
  }

  /**
   * Subscribe to peer status updates
   */
  onPeerStatus(callback) {
    this.gun.get(this.key('agents')).map().on((ref, key) => {
      if (ref && key !== '_' && ref.id && ref.id !== this.agentId) {
        this.node('agent', ref.id).on((data) => {
          if (data) callback(ref.id, data);
        });
      }
    });
  }

  /**
   * Subscribe to messages for this agent
   */
  onMessage(callback) {
    this.gun.get(this.key('messages')).map().on((ref, key) => {
      if (ref && key !== '_' && ref.id) {
        this.node('message', ref.id).once(data => {
          if (data && (data.to === this.agentName || data.to === 'all')) {
            if (data.from !== this.agentName && !data.read) {
              callback(data);
            }
          }
        });
      }
    });
  }

  /**
   * Start heartbeat to update last_seen
   */
  _startHeartbeat() {
    this.heartbeatInterval = setInterval(async () => {
      if (this.connected) {
        await this.updateAgentStatus({ 
          online: true,
          currentTask: null
        });
      }
    }, 30000);
  }

  /**
   * Get network stats
   */
  async getStats() {
    const [activities, memories, decisions] = await Promise.all([
      this.getActivity(1000),
      this.getMemories(1000),
      this.getDecisions()
    ]);

    return {
      activityCount: activities.length,
      memoryCount: memories.length,
      decisionCount: decisions.length
    };
  }
}

module.exports = GunAdapter;
