/**
 * YouTube API Client - Singleton wrapper for YouTube Data API v3
 */

import { google, youtube_v3 } from 'googleapis';
import { getSettings, validateSettings } from '../config/settings.js';

// Singleton client instance
let clientInstance: youtube_v3.Youtube | null = null;

/**
 * Get the YouTube Data API v3 client (singleton)
 *
 * @returns The YouTube client instance
 * @throws Error if credentials are invalid
 */
export function getClient(): youtube_v3.Youtube {
  if (clientInstance) {
    return clientInstance;
  }

  const validation = validateSettings();
  if (!validation.valid) {
    throw new Error(`Invalid YouTube credentials: ${validation.errors.join(', ')}`);
  }

  const settings = getSettings();

  clientInstance = google.youtube({
    version: 'v3',
    auth: settings.apiKey,
  });

  return clientInstance;
}

/**
 * Get the YouTube API key from settings
 *
 * @returns API key string
 */
export function getApiKey(): string {
  const settings = getSettings();
  return settings.apiKey;
}

/**
 * Reset the client singleton (useful for testing)
 */
export function resetClient(): void {
  clientInstance = null;
}
