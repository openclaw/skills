/**
 * Search Console API - Google Search Console data retrieval
 */

import { getSearchConsoleClient, getSiteUrl } from '../core/client.js';
import { saveResult } from '../core/storage.js';
import { getSettings } from '../config/settings.js';

/**
 * Date range configuration for Search Console
 */
export interface SearchConsoleDateRange {
  startDate: string;
  endDate: string;
}

/**
 * Search analytics query options
 */
export interface SearchAnalyticsOptions {
  dimensions?: string[];
  dateRange?: string | SearchConsoleDateRange;
  rowLimit?: number;
  startRow?: number;
  save?: boolean;
}

/**
 * Search analytics row structure
 */
export interface SearchAnalyticsRow {
  keys: string[];
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

/**
 * Search analytics response structure
 */
export interface SearchAnalyticsResponse {
  rows?: SearchAnalyticsRow[];
  responseAggregationType?: string;
}

/**
 * Parse shorthand date range (e.g., "7d", "30d") to Search Console date format
 * Note: Search Console requires YYYY-MM-DD format, not GA4's "NdaysAgo" format
 */
export function parseSearchConsoleDateRange(range: string | SearchConsoleDateRange | undefined): SearchConsoleDateRange {
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
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    return {
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0],
    };
  }

  // Default to 30 days
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 30);

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  };
}

/**
 * Query search analytics data
 */
export async function querySearchAnalytics(options: SearchAnalyticsOptions): Promise<SearchAnalyticsResponse> {
  const {
    dimensions = ['query'],
    dateRange,
    rowLimit = 1000,
    startRow = 0,
    save = true,
  } = options;

  const client = getSearchConsoleClient();
  const siteUrl = getSiteUrl();
  const parsedDateRange = parseSearchConsoleDateRange(dateRange);

  const response = await client.searchanalytics.query({
    siteUrl,
    requestBody: {
      startDate: parsedDateRange.startDate,
      endDate: parsedDateRange.endDate,
      dimensions,
      rowLimit,
      startRow,
    },
  });

  const result = response.data as SearchAnalyticsResponse;

  if (save) {
    const operation = dimensions.join('_') || 'query';
    const extra = typeof dateRange === 'string' ? dateRange : undefined;
    saveResult(result, 'searchconsole', operation, extra);
  }

  return result;
}

/**
 * Get top search queries
 */
export async function getTopQueries(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
  return querySearchAnalytics({
    dimensions: ['query'],
    dateRange,
    rowLimit: 100,
  });
}

/**
 * Get top pages by search performance
 */
export async function getTopPages(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
  return querySearchAnalytics({
    dimensions: ['page'],
    dateRange,
    rowLimit: 100,
  });
}

/**
 * Get search performance by device type
 */
export async function getDevicePerformance(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
  return querySearchAnalytics({
    dimensions: ['device'],
    dateRange,
  });
}

/**
 * Get search performance by country
 */
export async function getCountryPerformance(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
  return querySearchAnalytics({
    dimensions: ['country'],
    dateRange,
    rowLimit: 50,
  });
}

/**
 * Get search appearance data (rich results, AMP, etc.)
 */
export async function getSearchAppearance(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
  return querySearchAnalytics({
    dimensions: ['searchAppearance'],
    dateRange,
  });
}
