/**
 * Init commands for vinculum
 * Handles /link init, /link invite, /link leave
 */

const pairingCode = require('../utils/pairing-code');
const formatting = require('../utils/formatting');

/**
 * Initialize a new namespace
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function initNamespace(context) {
  const { adapter, configManager } = context;
  
  // Check if already connected
  const currentConfig = await configManager.get();
  if (currentConfig.namespace) {
    return formatting.formatError(
      `Already connected to namespace: \`${currentConfig.namespace}\`\n\n` +
      `Use \`/link leave\` first to disconnect.`
    );
  }
  
  // Generate new network
  const network = pairingCode.generateNewNetwork();
  
  // Save to config
  await configManager.set({
    enabled: true,
    namespace: network.namespaceId,
    encryption_key: network.encryptionKey
  });
  
  // Connect adapter
  await adapter.connect(network.namespaceId, network.encryptionKey, {
    name: currentConfig.agent_name || 'Clawdbot',
    instanceId: context.instanceId,
    owner: context.owner,
    channel: context.channel
  });
  
  return formatting.formatInitSuccess({
    namespaceId: network.namespaceId,
    pairingCode: network.pairingCode
  });
}

/**
 * Generate a new invite code for current namespace
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function generateInvite(context) {
  const { configManager } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace || !config.encryption_key) {
    return formatting.formatError(
      `Not connected to any network.\n\n` +
      `Use \`/link init\` to create one.`
    );
  }
  
  const code = pairingCode.createPairingCode(
    config.namespace,
    config.encryption_key
  );
  
  return `🔗 **Invite Code**

Share this with other Clawdbot instances:

\`\`\`
${code}
\`\`\`

This code provides access to namespace \`${config.namespace}\`.
Anyone with this code can read and write to shared context.`;
}

/**
 * Leave current namespace
 * @param {Object} context
 * @returns {Promise<string>}
 */
async function leaveNamespace(context) {
  const { adapter, configManager } = context;
  
  const config = await configManager.get();
  
  if (!config.namespace) {
    return formatting.formatError(`Not connected to any network.`);
  }
  
  const oldNamespace = config.namespace;
  
  // Disconnect adapter
  await adapter.disconnect();
  
  // Clear namespace from config
  await configManager.set({
    enabled: false,
    namespace: null,
    encryption_key: null
  });
  
  return formatting.formatSuccess(
    `Left namespace \`${oldNamespace}\`.\n\n` +
    `Local data preserved. Use \`/link init\` to create new network or \`/link join\` to rejoin.`
  );
}

module.exports = {
  initNamespace,
  generateInvite,
  leaveNamespace
};
