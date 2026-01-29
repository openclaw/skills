/**
 * Response formatting utilities for vinculum commands
 */

/**
 * Format a quick status response
 * @param {Object} status
 * @returns {string}
 */
function formatQuickStatus({ enabled, peerCount, lastSync }) {
  const statusEmoji = enabled ? '📡' : '⏸️';
  const statusText = enabled ? 'ON' : 'OFF';
  const peerText = peerCount === 1 ? '1 peer' : `${peerCount} peers`;
  const syncText = lastSync ? formatTimeAgo(lastSync) : 'never';
  
  return `${statusEmoji} **Sync: ${statusText}**
Peers: ${peerText}
Last sync: ${syncText}`;
}

/**
 * Format a detailed status response
 * @param {Object} status
 * @returns {string}
 */
function formatDetailedStatus({ 
  enabled, 
  namespaceId, 
  peers, 
  lastPush, 
  lastPull, 
  config,
  stats 
}) {
  const lines = ['📡 **Vinculum Status**', ''];
  
  // Network section
  lines.push('**Network**');
  lines.push(`Collective: \`${namespaceId || 'Not connected'}\``);
  lines.push(`Status: ${enabled ? '🟢 Connected' : '🔴 Disconnected'}`);
  lines.push('');
  
  // Peers section
  lines.push('**Peers**');
  if (peers && peers.length > 0) {
    peers.forEach(peer => {
      const status = peer.online ? '🟢' : '⚫';
      const lastSeen = peer.last_seen ? formatTimeAgo(peer.last_seen) : 'unknown';
      lines.push(`• ${peer.name} — ${status} (last: ${lastSeen})`);
    });
  } else {
    lines.push('• No peers connected');
  }
  lines.push('');
  
  // Sync queue section
  lines.push('**Sync**');
  lines.push(`Last push: ${lastPush ? formatTimeAgo(lastPush) : 'never'}`);
  lines.push(`Last pull: ${lastPull ? formatTimeAgo(lastPull) : 'never'}`);
  lines.push('');
  
  // Configuration section
  if (config) {
    lines.push('**Configuration**');
    lines.push(`Share activity: ${config.shareActivity ? 'ON' : 'OFF'}`);
    lines.push(`Share memory: ${config.shareMemory ? 'ON' : 'OFF'}`);
    lines.push(`Share decisions: ${config.shareDecisions ? 'ON' : 'OFF'}`);
    lines.push(`Sync interval: ${config.syncInterval}s`);
    lines.push('');
  }
  
  // Stats section
  if (stats) {
    lines.push('**Stats**');
    lines.push(`Activity entries: ${stats.activityCount || 0}`);
    lines.push(`Shared memories: ${stats.memoryCount || 0}`);
    lines.push(`Decisions: ${stats.decisionCount || 0}`);
  }
  
  return lines.join('\n');
}

/**
 * Format init success response
 * @param {Object} params
 * @returns {string}
 */
function formatInitSuccess({ namespaceId, pairingCode }) {
  return `🔗 **Collective Initialized**

Collective created: \`${namespaceId}\`
Encryption: AES-256 via Gun SEA

**Your pairing code:**
\`\`\`
${pairingCode}
\`\`\`

Share this with your other Clawdbot instances.
Use \`/link invite\` to generate additional codes.

Sync is **ON** by default. Use \`/link off\` to pause.`;
}

/**
 * Format join success response
 * @param {Object} params
 * @returns {string}
 */
function formatJoinSuccess({ namespaceId, peers, entryCount }) {
  const peerList = peers.length > 0 
    ? peers.map(p => `• ${p.name} (${p.online ? 'online' : 'offline'})`).join('\n')
    : '• No other peers found yet';
    
  return `🔗 **Joined Network**

✅ Connected to namespace: \`${namespaceId}\`
✅ Initial sync complete (${entryCount} entries)

**Peers:**
${peerList}

Use \`/link status\` anytime to check connection.`;
}

/**
 * Format peer list response
 * @param {Array} peers
 * @returns {string}
 */
function formatPeerList(peers) {
  if (!peers || peers.length === 0) {
    return '👥 **No peers connected**\n\nUse `/link invite` to get a pairing code.';
  }
  
  const lines = ['👥 **Connected Peers**', ''];
  
  peers.forEach(peer => {
    const status = peer.online ? '🟢 Online' : '⚫ Offline';
    const task = peer.current_task ? `\n   └ Working on: ${peer.current_task}` : '';
    const lastSeen = peer.last_seen ? `\n   └ Last seen: ${formatTimeAgo(peer.last_seen)}` : '';
    
    lines.push(`**${peer.name}** — ${status}${task}${lastSeen}`);
    lines.push('');
  });
  
  return lines.join('\n');
}

/**
 * Format activity list response
 * @param {Array} activities
 * @param {string} filterAgent
 * @returns {string}
 */
function formatActivityList(activities, filterAgent = null) {
  if (!activities || activities.length === 0) {
    return '📋 **No recent activity**';
  }
  
  const title = filterAgent 
    ? `📋 **Activity: ${filterAgent}**`
    : '📋 **Recent Network Activity**';
    
  const lines = [title, ''];
  
  // Group by date
  const grouped = {};
  activities.forEach(act => {
    const date = new Date(act.timestamp).toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
    if (!grouped[date]) grouped[date] = [];
    grouped[date].push(act);
  });
  
  Object.entries(grouped).forEach(([date, acts]) => {
    lines.push(`**${date}**`);
    acts.forEach(act => {
      const time = new Date(act.timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
      const emoji = act.action === 'completed' ? '✅' : 
                    act.action === 'started' ? '🔄' : '❌';
      lines.push(`• ${time} — ${emoji} ${act.agent}: ${act.summary}`);
    });
    lines.push('');
  });
  
  return lines.join('\n');
}

/**
 * Format decisions list response
 * @param {Array} decisions
 * @returns {string}
 */
function formatDecisionsList(decisions) {
  if (!decisions || decisions.length === 0) {
    return '📜 **No shared decisions**';
  }
  
  const lines = ['📜 **Shared Decisions**', ''];
  
  decisions.forEach(dec => {
    const date = new Date(dec.timestamp).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
    const acks = dec.acknowledged_by ? dec.acknowledged_by.join(', ') : dec.decided_by;
    
    lines.push(`**${dec.topic}**`);
    lines.push(`└ ${dec.decision}`);
    lines.push(`└ Decided by: ${dec.decided_by} (${date})`);
    lines.push(`└ Acknowledged: ${acks}`);
    lines.push('');
  });
  
  return lines.join('\n');
}

/**
 * Format config response
 * @param {Object} config
 * @returns {string}
 */
function formatConfig(config) {
  return `⚙️ **Sync Configuration**

**Sharing**
Share activity: ${config.shareActivity ? '✅ ON' : '❌ OFF'}
Share memory: ${config.shareMemory ? '✅ ON' : '❌ OFF'}
Share decisions: ${config.shareDecisions ? '✅ ON' : '❌ OFF'}

**Sync**
Auto-sync: ${config.autoSync ? '✅ ON' : '❌ OFF'}
Interval: ${config.syncInterval} seconds

**Agent**
Name: ${config.agentName}
Collective: \`${config.namespaceId || 'Not connected'}\`

Use \`/link config <setting> <value>\` to change.`;
}

/**
 * Format time ago string
 * @param {number} timestamp
 * @returns {string}
 */
function formatTimeAgo(timestamp) {
  const seconds = Math.floor((Date.now() - timestamp) / 1000);
  
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

/**
 * Format error response
 * @param {string} message
 * @returns {string}
 */
function formatError(message) {
  return `❌ **Error**\n\n${message}`;
}

/**
 * Format success response
 * @param {string} message
 * @returns {string}
 */
function formatSuccess(message) {
  return `✅ ${message}`;
}

/**
 * Format warning response
 * @param {string} message
 * @returns {string}
 */
function formatWarning(message) {
  return `⚠️ ${message}`;
}

/**
 * Format info response
 * @param {string} message
 * @returns {string}
 */
function formatInfo(message) {
  return `ℹ️ ${message}`;
}

module.exports = {
  formatQuickStatus,
  formatDetailedStatus,
  formatInitSuccess,
  formatJoinSuccess,
  formatPeerList,
  formatActivityList,
  formatDecisionsList,
  formatConfig,
  formatTimeAgo,
  formatError,
  formatSuccess,
  formatWarning,
  formatInfo
};
