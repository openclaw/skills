/**
 * Settings Module - Environment configuration for YouTube Data API v3
 */

import { config } from 'dotenv';
import { join } from 'path';

// Load .env file from current working directory
config();

/**
 * Settings interface for YouTube API configuration
 */
export interface Settings {
  /** YouTube Data API v3 key */
  apiKey: string;
  /** Default max results for list queries */
  defaultMaxResults: number;
  /** Directory path for storing results */
  resultsDir: string;
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
    apiKey: process.env.YOUTUBE_API_KEY || '',
    defaultMaxResults: parseInt(process.env.YOUTUBE_DEFAULT_MAX_RESULTS || '50', 10),
    resultsDir: join(process.cwd(), 'results'),
  };
}

/**
 * Validate that all required settings are present
 */
export function validateSettings(): ValidationResult {
  const settings = getSettings();
  const errors: string[] = [];

  if (!settings.apiKey) {
    errors.push('YOUTUBE_API_KEY is required');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
