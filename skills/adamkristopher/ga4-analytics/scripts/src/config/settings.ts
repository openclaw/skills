/**
 * Settings Module - Environment configuration for GA4 API
 */

import { config } from 'dotenv';
import { join } from 'path';

// Load .env file from current working directory
config();

/**
 * Settings interface for GA4 API configuration
 */
export interface Settings {
  /** GA4 Property ID */
  propertyId: string;
  /** Service account email */
  clientEmail: string;
  /** Service account private key */
  privateKey: string;
  /** Default date range for reports (e.g., "30d", "7d") */
  defaultDateRange: string;
  /** Directory path for storing results */
  resultsDir: string;
  /** Search Console site URL (e.g., "https://example.com") */
  siteUrl: string;
}

/**
 * Validation result from validateSettings()
 */
export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

/**
 * Get current settings from environment variables
 */
export function getSettings(): Settings {
  return {
    propertyId: process.env.GA4_PROPERTY_ID || '',
    clientEmail: process.env.GA4_CLIENT_EMAIL || '',
    privateKey: (process.env.GA4_PRIVATE_KEY || '').replace(/\\n/g, '\n'),
    defaultDateRange: process.env.GA4_DEFAULT_DATE_RANGE || '30d',
    resultsDir: join(process.cwd(), 'results'),
    siteUrl: process.env.SEARCH_CONSOLE_SITE_URL || '',
  };
}

/**
 * Validate that all required settings are present
 */
export function validateSettings(): ValidationResult {
  const settings = getSettings();
  const errors: string[] = [];

  if (!settings.propertyId) {
    errors.push('GA4_PROPERTY_ID is required');
  }

  if (!settings.clientEmail) {
    errors.push('GA4_CLIENT_EMAIL is required');
  }

  if (!settings.privateKey) {
    errors.push('GA4_PRIVATE_KEY is required');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
