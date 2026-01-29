/**
 * Status commands for gun-sync
 * Handles /link and /link status
 */

const formatting = require('../utils/formatting');

/**
 * Quick status check
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function quickStatus(context) {
  const { adapter, configManager, syncState } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace) {
    return `📡 **Sync: NOT CONFIGURED**

Use \`/link init\` to create a collective, or
\`/link join <code>\` to join an existing one.`;
  }
  
  // Get peer count
  let peerCount = 0;
  if (adapter.connected) {
    const agents = await adapter.getAgents();
    peerCount = agents.filter(a => 
      a.id !== context.instanceId && 
      a.status?.online
    ).length;
  }
  
  return formatting.formatQuickStatus({
    enabled: config.enabled && adapter.connected,
    peerCount,
    lastSync: syncState?.lastSync || null
  });
}

/**
 * Detailed status
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function detailedStatus(context) {
  const { adapter, configManager, syncState } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace) {
    return `📡 **Vinculum Status**

**Network**
Collective: Not connected
Status: 🔴 Disconnected

Use \`/link init\` to create a collective, or
\`/link join <code>\` to join an existing one.`;
  }
  
  // Get peers
  let peers = [];
  let stats = { activityCount: 0, memoryCount: 0, decisionCount: 0 };
  
  if (adapter.connected) {
    const agents = await adapter.getAgents();
    peers = agents
      .filter(a => a.id !== context.instanceId)
      .map(a => ({
        name: a.identity?.name || a.id,
        online: a.status?.online || false,
        current_task: a.status?.current_task || null,
        last_seen: a.status?.updated || a.identity?.last_seen
      }));
    
    stats = await adapter.getStats();
  }
  
  return formatting.formatDetailedStatus({
    enabled: config.enabled && adapter.connected,
    namespaceId: config.namespace,
    peers,
    lastPush: syncState?.lastPush || null,
    lastPull: syncState?.lastPull || null,
    config: {
      shareActivity: config.share?.activity !== false,
      shareMemory: config.share?.memory !== false,
      shareDecisions: config.share?.decisions !== false,
      syncInterval: config.sync_interval || 30
    },
    stats
  });
}

module.exports = {
  quickStatus,
  detailedStatus
};
