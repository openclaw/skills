/**
 * Join command for gun-sync
 * Handles /link join <code>
 */

const pairingCode = require('../utils/pairing-code');
const formatting = require('../utils/formatting');

/**
 * Join an existing namespace
 * @param {string} code - Pairing code
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function joinNamespace(code, context) {
  const { adapter, configManager } = context;
  
  // Validate code provided
  if (!code) {
    return formatting.formatError(
      `Missing pairing code.\n\n` +
      `Usage: \`/link join <pairing-code>\`\n\n` +
      `Get a pairing code from \`/link invite\` on another bot.`
    );
  }
  
  // Check if already connected
  const currentConfig = await configManager.get();
  if (currentConfig.namespace) {
    return formatting.formatError(
      `Already connected to namespace: \`${currentConfig.namespace}\`\n\n` +
      `Use \`/link leave\` first to disconnect.`
    );
  }
  
  // Parse pairing code
  const parsed = pairingCode.parsePairingCode(code);
  
  if (!parsed) {
    return formatting.formatError(
      `Invalid pairing code.\n\n` +
      `Make sure you copied the full code from the other bot.`
    );
  }
  
  // Save to config
  await configManager.set({
    enabled: true,
    namespace: parsed.namespaceId,
    encryption_key: parsed.encryptionKey
  });
  
  // Connect adapter
  await adapter.connect(parsed.namespaceId, parsed.encryptionKey, {
    name: currentConfig.agent_name || 'Clawdbot',
    instanceId: context.instanceId,
    owner: context.owner,
    channel: context.channel
  });
  
  // Get peers and initial sync info
  const agents = await adapter.getAgents();
  const stats = await adapter.getStats();
  
  // Filter out self
  const peers = agents
    .filter(a => a.id !== context.instanceId)
    .map(a => ({
      name: a.identity?.name || a.id,
      online: a.status?.online || false
    }));
  
  const entryCount = stats.activityCount + stats.memoryCount + stats.decisionCount;
  
  return formatting.formatJoinSuccess({
    namespaceId: parsed.namespaceId,
    peers,
    entryCount
  });
}

module.exports = {
  joinNamespace
};
