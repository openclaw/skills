/**
 * Data schema helpers for gun-sync
 * Defines the structure of shared data in the Gun graph
 */

/**
 * Create an agent identity object
 * @param {Object} params
 * @returns {Object} Agent identity
 */
function createAgentIdentity({ name, instanceId, owner = 'unknown', channel = 'local' }) {
  return {
    name: name || 'Agent',
    instance_id: instanceId || String(Date.now()),
    owner: owner,
    channel: channel,
    created: Date.now(),
    last_seen: Date.now()
  };
}

/**
 * Create an agent status object
 * @param {Object} params
 * @returns {Object} Agent status
 */
function createAgentStatus({ online = true, currentTask = '' }) {
  return {
    online: online ? 1 : 0,  // Gun prefers primitives
    current_task: currentTask || '',
    task_started: currentTask ? Date.now() : 0,
    updated: Date.now()
  };
}

/**
 * Create an activity log entry
 * @param {Object} params
 * @returns {Object} Activity entry
 */
function createActivityEntry({ agent, action, summary, tags = [], filesTouched = [] }) {
  const id = `${Date.now()}-${agent || 'anon'}`;
  return {
    id,
    agent: agent || 'anonymous',
    action: action || 'activity',
    summary: summary || '',
    // Gun doesn't handle arrays - join as comma-separated
    tags: Array.isArray(tags) ? tags.join(',') : (tags || ''),
    files_touched: Array.isArray(filesTouched) ? filesTouched.join(',') : (filesTouched || ''),
    timestamp: Date.now()
  };
}

/**
 * Create a shared memory entry
 * @param {Object} params
 * @returns {Object} Memory entry
 */
function createMemoryEntry({ content, learnedBy, context = '', tags = [] }) {
  const id = `mem-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
  return {
    id,
    content: content || '',
    learned_by: learnedBy || 'unknown',
    context: context || '',
    tags: Array.isArray(tags) ? tags.join(',') : (tags || ''),
    timestamp: Date.now()
  };
}

/**
 * Create a decision entry
 * @param {Object} params
 * @returns {Object} Decision entry
 */
function createDecisionEntry({ topic, decision, decidedBy }) {
  const id = `dec-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
  return {
    id,
    topic: topic || '',
    decision: decision || '',
    decided_by: decidedBy || 'unknown',
    acknowledged_by: decidedBy || 'unknown',  // Start with decider, comma-separate to add more
    timestamp: Date.now()
  };
}

/**
 * Create an inter-agent message
 * @param {Object} params
 * @returns {Object} Message entry
 */
function createMessage({ from, to, type, content }) {
  const id = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
  return {
    id,
    from: from || 'unknown',
    to: to || 'all',       // agent name or 'all'
    type: type || 'notification',  // 'request', 'response', 'notification'
    content: content || '',
    timestamp: Date.now(),
    read: 0  // Gun prefers numbers to booleans
  };
}

/**
 * Get the Gun path for an agent
 * @param {string} namespaceId
 * @param {string} agentId
 * @returns {string[]} Path segments
 */
function getAgentPath(namespaceId, agentId) {
  return ['clawdbot-network', namespaceId, 'agents', agentId];
}

/**
 * Get the Gun path for shared activity
 * @param {string} namespaceId
 * @returns {string[]} Path segments
 */
function getActivityPath(namespaceId) {
  return ['clawdbot-network', namespaceId, 'shared', 'activity'];
}

/**
 * Get the Gun path for shared memory
 * @param {string} namespaceId
 * @returns {string[]} Path segments
 */
function getMemoryPath(namespaceId) {
  return ['clawdbot-network', namespaceId, 'shared', 'memory'];
}

/**
 * Get the Gun path for shared decisions
 * @param {string} namespaceId
 * @returns {string[]} Path segments
 */
function getDecisionsPath(namespaceId) {
  return ['clawdbot-network', namespaceId, 'shared', 'decisions'];
}

/**
 * Get the Gun path for messages
 * @param {string} namespaceId
 * @returns {string[]} Path segments
 */
function getMessagesPath(namespaceId) {
  return ['clawdbot-network', namespaceId, 'messages'];
}

module.exports = {
  createAgentIdentity,
  createAgentStatus,
  createActivityEntry,
  createMemoryEntry,
  createDecisionEntry,
  createMessage,
  getAgentPath,
  getActivityPath,
  getMemoryPath,
  getDecisionsPath,
  getMessagesPath
};
