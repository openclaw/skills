/**
 * GA4 API Client - Singleton wrapper for BetaAnalyticsDataClient
 * Also includes Search Console and Indexing API clients
 */

import { BetaAnalyticsDataClient } from '@google-analytics/data';
import { searchconsole } from '@googleapis/searchconsole';
import { indexing } from '@googleapis/indexing';
import { google } from 'googleapis';
import { getSettings, validateSettings } from '../config/settings.js';

// Singleton client instances
let clientInstance: BetaAnalyticsDataClient | null = null;
let searchConsoleClientInstance: ReturnType<typeof searchconsole> | null = null;
let indexingClientInstance: ReturnType<typeof indexing> | null = null;

/**
 * Get the GA4 Analytics Data API client (singleton)
 *
 * @returns The BetaAnalyticsDataClient instance
 * @throws Error if credentials are invalid
 */
export function getClient(): BetaAnalyticsDataClient {
  if (clientInstance) {
    return clientInstance;
  }

  const validation = validateSettings();
  if (!validation.valid) {
    throw new Error(`Invalid GA4 credentials: ${validation.errors.join(', ')}`);
  }

  const settings = getSettings();

  clientInstance = new BetaAnalyticsDataClient({
    credentials: {
      client_email: settings.clientEmail,
      private_key: settings.privateKey,
    },
  });

  return clientInstance;
}

/**
 * Get the GA4 property ID formatted for API calls
 *
 * @returns Property ID with "properties/" prefix
 */
export function getPropertyId(): string {
  const settings = getSettings();
  return `properties/${settings.propertyId}`;
}

/**
 * Reset the client singleton (useful for testing)
 */
export function resetClient(): void {
  clientInstance = null;
  searchConsoleClientInstance = null;
  indexingClientInstance = null;
}

/**
 * Get Google Auth client for Search Console and Indexing APIs
 */
function getGoogleAuth() {
  const settings = getSettings();
  return new google.auth.GoogleAuth({
    credentials: {
      client_email: settings.clientEmail,
      private_key: settings.privateKey,
    },
    scopes: [
      'https://www.googleapis.com/auth/webmasters.readonly',
      'https://www.googleapis.com/auth/indexing',
    ],
  });
}

/**
 * Get the Search Console API client (singleton)
 *
 * @returns The Search Console client instance
 * @throws Error if credentials are invalid
 */
export function getSearchConsoleClient(): ReturnType<typeof searchconsole> {
  if (searchConsoleClientInstance) {
    return searchConsoleClientInstance;
  }

  const validation = validateSettings();
  if (!validation.valid) {
    throw new Error(`Invalid credentials: ${validation.errors.join(', ')}`);
  }

  const auth = getGoogleAuth();
  searchConsoleClientInstance = searchconsole({ version: 'v1', auth });

  return searchConsoleClientInstance;
}

/**
 * Get the Indexing API client (singleton)
 *
 * @returns The Indexing client instance
 * @throws Error if credentials are invalid
 */
export function getIndexingClient(): ReturnType<typeof indexing> {
  if (indexingClientInstance) {
    return indexingClientInstance;
  }

  const validation = validateSettings();
  if (!validation.valid) {
    throw new Error(`Invalid credentials: ${validation.errors.join(', ')}`);
  }

  const auth = getGoogleAuth();
  indexingClientInstance = indexing({ version: 'v3', auth });

  return indexingClientInstance;
}

/**
 * Get the Search Console site URL
 *
 * @returns Site URL from settings
 */
export function getSiteUrl(): string {
  const settings = getSettings();
  return settings.siteUrl;
}
