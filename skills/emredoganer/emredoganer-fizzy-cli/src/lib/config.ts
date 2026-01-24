import Conf from 'conf';
import crypto from 'crypto';
import os from 'os';
import type { FizzyConfig } from '../types/index.js';

// =============================================================================
// Encryption utilities for secure token storage
// =============================================================================

/**
 * Generate a machine-specific encryption key
 * This provides better security than plain text while not requiring external dependencies
 * Note: For maximum security, consider using system keychain (macOS Keychain, Windows Credential Manager)
 */
function getEncryptionKey(): Buffer {
  const machineId = `${os.hostname()}-${os.userInfo().username}-fizzy-cli-tokens`;
  return crypto.createHash('sha256').update(machineId).digest();
}

/**
 * Encrypt a string using AES-256-CBC
 * @param text Plain text to encrypt
 * @returns Encrypted string in format "iv:encryptedData"
 */
function encrypt(text: string): string {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', getEncryptionKey(), iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

/**
 * Decrypt a string that was encrypted with encrypt()
 * @param text Encrypted string in format "iv:encryptedData"
 * @returns Decrypted plain text
 */
function decrypt(text: string): string {
  try {
    const [ivHex, encrypted] = text.split(':');
    if (!ivHex || !encrypted) {
      throw new Error('Invalid encrypted format');
    }
    const iv = Buffer.from(ivHex, 'hex');
    const decipher = crypto.createDecipheriv('aes-256-cbc', getEncryptionKey(), iv);
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  } catch {
    // If decryption fails, the data might be in plain text (legacy)
    // Return as-is to allow migration
    return text;
  }
}

/**
 * Check if a string appears to be encrypted (has iv:data format)
 */
function isEncrypted(text: string): boolean {
  if (!text) return false;
  const parts = text.split(':');
  // Encrypted format: 32 char hex IV + ':' + encrypted data
  return parts.length === 2 && parts[0].length === 32 && /^[0-9a-f]+$/i.test(parts[0]);
}

// =============================================================================
// Configuration store
// =============================================================================

const config = new Conf<FizzyConfig>({
  projectName: 'fizzy-cli',
  schema: {
    token: { type: 'string' },
    currentAccountSlug: { type: 'string' }
  }
});

// =============================================================================
// Token management with encryption
// =============================================================================

export function getToken(): string | undefined {
  // Environment variable takes precedence and is returned as-is
  const envToken = process.env.FIZZY_ACCESS_TOKEN;
  if (envToken) return envToken;

  const storedToken = config.get('token');
  if (!storedToken) return undefined;

  // Decrypt if encrypted, otherwise return as-is (legacy support)
  return isEncrypted(storedToken) ? decrypt(storedToken) : storedToken;
}

export function setToken(token: string): void {
  // Encrypt the token before storing
  config.set('token', encrypt(token));
}

export function clearToken(): void {
  config.delete('token');
}

// =============================================================================
// Account management
// =============================================================================

export function getCurrentAccountSlug(): string | undefined {
  return config.get('currentAccountSlug') || process.env.FIZZY_ACCOUNT_SLUG;
}

export function setCurrentAccountSlug(slug: string): void {
  config.set('currentAccountSlug', slug);
}

// =============================================================================
// Utility functions
// =============================================================================

export function clearAll(): void {
  config.clear();
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

export { config };
