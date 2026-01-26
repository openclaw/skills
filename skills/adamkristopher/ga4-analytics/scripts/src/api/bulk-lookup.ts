/**
 * Bulk URL Lookup - Get GA4 metrics for specific page paths
 *
 * This module provides a convenient way to look up analytics data
 * for a list of specific URLs, similar to a bulk URL lookup field.
 */

import { getClient, getPropertyId } from '../core/client.js';
import { saveResult } from '../core/storage.js';
import { getSettings } from '../config/settings.js';
import type { ReportResponse, DateRange } from './reports.js';

/**
 * Options for bulk URL lookup
 */
export interface BulkLookupOptions {
  /** Date range (e.g., "7d", "30d") or explicit dates */
  dateRange?: string | DateRange;
  /** Custom metrics to retrieve (defaults to standard page metrics) */
  metrics?: string[];
  /** Whether to save results to file (default: true) */
  save?: boolean;
}

/**
 * Dimension filter expression for GA4 API
 */
export interface DimensionFilterExpression {
  filter: {
    fieldName: string;
    inListFilter?: {
      values: string[];
      caseSensitive?: boolean;
    };
    stringFilter?: {
      matchType: string;
      value: string;
      caseSensitive?: boolean;
    };
  };
}

/**
 * Default metrics for bulk URL lookup
 */
const DEFAULT_METRICS = [
  'screenPageViews',
  'activeUsers',
  'averageSessionDuration',
  'bounceRate',
  'engagementRate',
];

/**
 * Normalize URLs to ensure consistent format
 *
 * - Trims whitespace
 * - Adds leading slash if missing
 * - Preserves trailing slashes
 *
 * @param urls - Array of URLs to normalize
 * @returns Normalized URL array
 */
export function normalizeUrls(urls: string[]): string[] {
  return urls.map(url => {
    // Trim whitespace
    let normalized = url.trim();

    // Add leading slash if missing
    if (!normalized.startsWith('/')) {
      normalized = '/' + normalized;
    }

    return normalized;
  });
}

/**
 * Build a dimension filter expression for the given URLs
 *
 * @param urls - Array of page paths to filter by
 * @returns Filter expression or null if no URLs provided
 */
export function buildUrlFilter(urls: string[]): DimensionFilterExpression | null {
  if (urls.length === 0) {
    return null;
  }

  return {
    filter: {
      fieldName: 'pagePath',
      inListFilter: {
        values: urls,
        caseSensitive: false,
      },
    },
  };
}

/**
 * Parse shorthand date range (e.g., "7d", "30d") to GA4 date range format
 */
function parseDateRange(range: string | DateRange | undefined): DateRange {
  if (!range) {
    const settings = getSettings();
    range = settings.defaultDateRange;
  }

  if (typeof range === 'object') {
    return range;
  }

  // Parse shorthand like "7d", "30d", "90d"
  const match = range.match(/^(\d+)d$/);
  if (match) {
    const days = parseInt(match[1], 10);
    return {
      startDate: `${days}daysAgo`,
      endDate: 'today',
    };
  }

  // Default to 30 days
  return {
    startDate: '30daysAgo',
    endDate: 'today',
  };
}

/**
 * Get GA4 metrics for specific page paths (bulk URL lookup)
 *
 * @param urls - Array of page paths to look up (e.g., ['/pricing', '/about'])
 * @param options - Optional configuration
 * @returns Report response with metrics for the specified URLs
 *
 * @example
 * ```typescript
 * // Get metrics for specific pages
 * const result = await getMetricsForUrls(['/pricing', '/about', '/blog']);
 *
 * // With custom date range and metrics
 * const result = await getMetricsForUrls(['/pricing'], {
 *   dateRange: '7d',
 *   metrics: ['sessions', 'bounceRate'],
 * });
 * ```
 */
export async function getMetricsForUrls(
  urls: string[],
  options: BulkLookupOptions = {}
): Promise<ReportResponse> {
  const { dateRange, metrics = DEFAULT_METRICS, save = true } = options;

  // Normalize URLs
  const normalizedUrls = normalizeUrls(urls);

  // Handle empty URL array
  if (normalizedUrls.length === 0) {
    return {
      rows: [],
      rowCount: 0,
    };
  }

  // Build filter
  const dimensionFilter = buildUrlFilter(normalizedUrls);

  // Get client and property
  const client = getClient();
  const property = getPropertyId();
  const parsedDateRange = parseDateRange(dateRange);

  // Build and execute request
  const request = {
    property,
    dateRanges: [parsedDateRange],
    dimensions: [{ name: 'pagePath' }, { name: 'pageTitle' }],
    metrics: metrics.map(name => ({ name })),
    dimensionFilter,
  };

  const [response] = await client.runReport(request);

  // Save results if requested
  if (save) {
    const dateStr = typeof dateRange === 'string' ? dateRange : 'custom';
    saveResult(response, 'reports', 'bulk_url_lookup', dateStr);
  }

  return response as ReportResponse;
}
