/**
 * Storage Module - Auto-save results to JSON files with metadata
 */

import { existsSync, mkdirSync, writeFileSync, readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import { getSettings } from '../config/settings.js';

/**
 * Metadata wrapper for saved results
 */
export interface ResultMetadata {
  savedAt: string;
  category: string;
  operation: string;
  propertyId: string;
  extraInfo?: string;
}

/**
 * Wrapped result with metadata
 */
export interface SavedResult<T = unknown> {
  metadata: ResultMetadata;
  data: T;
}

/**
 * Generate timestamp string for filenames: YYYYMMDD_HHMMSS
 */
function getTimestamp(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  return `${year}${month}${day}_${hours}${minutes}${seconds}`;
}

/**
 * Sanitize string for use in filename
 */
function sanitizeFilename(str: string): string {
  return str.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase();
}

/**
 * Save result data to a JSON file with metadata wrapper
 *
 * @param data - The data to save
 * @param category - Category directory (e.g., 'reports', 'realtime')
 * @param operation - Operation name (e.g., 'page_views', 'traffic_sources')
 * @param extraInfo - Optional extra info for filename
 * @returns The full path to the saved file
 */
export function saveResult<T>(
  data: T,
  category: string,
  operation: string,
  extraInfo?: string
): string {
  const settings = getSettings();
  const categoryDir = join(settings.resultsDir, category);

  // Ensure category directory exists
  if (!existsSync(categoryDir)) {
    mkdirSync(categoryDir, { recursive: true });
  }

  // Build filename
  const timestamp = getTimestamp();
  const sanitizedOperation = sanitizeFilename(operation);
  const sanitizedExtra = extraInfo ? `__${sanitizeFilename(extraInfo)}` : '';
  const filename = `${timestamp}__${sanitizedOperation}${sanitizedExtra}.json`;
  const filepath = join(categoryDir, filename);

  // Build wrapped result
  const result: SavedResult<T> = {
    metadata: {
      savedAt: new Date().toISOString(),
      category,
      operation,
      propertyId: settings.propertyId,
      ...(extraInfo && { extraInfo }),
    },
    data,
  };

  // Write to file
  writeFileSync(filepath, JSON.stringify(result, null, 2), 'utf-8');

  return filepath;
}

/**
 * Load a saved result from a JSON file
 *
 * @param filepath - Path to the JSON file
 * @returns The parsed result or null if file doesn't exist
 */
export function loadResult<T = unknown>(filepath: string): SavedResult<T> | null {
  if (!existsSync(filepath)) {
    return null;
  }

  try {
    const content = readFileSync(filepath, 'utf-8');
    return JSON.parse(content) as SavedResult<T>;
  } catch {
    return null;
  }
}

/**
 * List saved result files for a category
 *
 * @param category - Category to list results for
 * @param limit - Maximum number of results to return
 * @returns Array of file paths, sorted by date descending (newest first)
 */
export function listResults(category: string, limit?: number): string[] {
  const settings = getSettings();
  const categoryDir = join(settings.resultsDir, category);

  if (!existsSync(categoryDir)) {
    return [];
  }

  const files = readdirSync(categoryDir)
    .filter(f => f.endsWith('.json'))
    .map(f => join(categoryDir, f))
    .sort((a, b) => {
      // Sort by filename (which starts with timestamp) descending
      const nameA = a.split('/').pop() || '';
      const nameB = b.split('/').pop() || '';
      return nameB.localeCompare(nameA);
    });

  if (limit !== undefined) {
    return files.slice(0, limit);
  }

  return files;
}

/**
 * Get the most recent result for a category/operation
 *
 * @param category - Category to search
 * @param operation - Optional operation to filter by
 * @returns The most recent result or null
 */
export function getLatestResult<T = unknown>(
  category: string,
  operation?: string
): SavedResult<T> | null {
  let files = listResults(category);

  if (operation) {
    const sanitized = sanitizeFilename(operation);
    files = files.filter(f => f.includes(`__${sanitized}`));
  }

  if (files.length === 0) {
    return null;
  }

  return loadResult<T>(files[0]);
}
