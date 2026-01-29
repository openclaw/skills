/**
 * Pairing code utilities for gun-sync
 * Encodes/decodes namespace + encryption key into shareable codes
 */

const crypto = require('crypto');

/**
 * Generate a new namespace ID
 * @returns {string} Random namespace ID
 */
function generateNamespaceId() {
  const prefix = 'cbot';
  const random = crypto.randomBytes(6).toString('hex');
  return `${prefix}-${random}`;
}

/**
 * Generate a new encryption key
 * @returns {string} Random 32-byte hex key
 */
function generateEncryptionKey() {
  return crypto.randomBytes(32).toString('hex');
}

/**
 * Create a pairing code from namespace and key
 * @param {string} namespaceId 
 * @param {string} encryptionKey 
 * @returns {string} Base64 encoded pairing code
 */
function createPairingCode(namespaceId, encryptionKey) {
  const payload = JSON.stringify({
    n: namespaceId,
    k: encryptionKey,
    v: 1  // version
  });
  return Buffer.from(payload).toString('base64url');
}

/**
 * Parse a pairing code into namespace and key
 * @param {string} pairingCode 
 * @returns {{ namespaceId: string, encryptionKey: string } | null}
 */
function parsePairingCode(pairingCode) {
  try {
    const payload = Buffer.from(pairingCode, 'base64url').toString('utf8');
    const data = JSON.parse(payload);
    
    if (!data.n || !data.k) {
      return null;
    }
    
    return {
      namespaceId: data.n,
      encryptionKey: data.k,
      version: data.v || 1
    };
  } catch (err) {
    return null;
  }
}

/**
 * Generate a complete new network (namespace + key + code)
 * @returns {{ namespaceId: string, encryptionKey: string, pairingCode: string }}
 */
function generateNewNetwork() {
  const namespaceId = generateNamespaceId();
  const encryptionKey = generateEncryptionKey();
  const pairingCode = createPairingCode(namespaceId, encryptionKey);
  
  return {
    namespaceId,
    encryptionKey,
    pairingCode
  };
}

/**
 * Validate a pairing code format
 * @param {string} code 
 * @returns {boolean}
 */
function isValidPairingCode(code) {
  if (!code || typeof code !== 'string') return false;
  const parsed = parsePairingCode(code);
  return parsed !== null && parsed.namespaceId && parsed.encryptionKey;
}

module.exports = {
  generateNamespaceId,
  generateEncryptionKey,
  createPairingCode,
  parsePairingCode,
  generateNewNetwork,
  isValidPairingCode
};
