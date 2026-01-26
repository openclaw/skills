/**
 * Indexing API - Request re-indexing and URL inspection
 */

import { getIndexingClient, getSearchConsoleClient, getSiteUrl } from '../core/client.js';
import { saveResult } from '../core/storage.js';

/**
 * Indexing request options
 */
export interface IndexingOptions {
  save?: boolean;
}

/**
 * URL notification result
 */
export interface UrlNotificationResult {
  url: string;
  type: 'URL_UPDATED' | 'URL_DELETED';
  notifyTime: string;
}

/**
 * URL inspection result
 */
export interface UrlInspectionResult {
  inspectionResultLink?: string;
  indexStatus: {
    verdict: 'PASS' | 'FAIL' | 'NEUTRAL';
    coverageState: string;
    robotsTxtState?: string;
    indexingState?: string;
    lastCrawlTime?: string;
    pageFetchState?: string;
    googleCanonical?: string;
    userCanonical?: string;
    crawledAs?: string;
  };
  mobileUsability?: {
    verdict: string;
    issues?: unknown[];
  };
  richResults?: {
    verdict: string;
    detectedItems?: unknown[];
  };
}

/**
 * Request indexing for a single URL (notify Google to re-crawl)
 *
 * @param url - The URL to request indexing for
 * @param options - Optional settings (save to file, etc.)
 * @returns Notification result with timestamp
 */
export async function requestIndexing(url: string, options: IndexingOptions = {}): Promise<UrlNotificationResult> {
  const { save = true } = options;

  const client = getIndexingClient();

  const response = await client.urlNotifications.publish({
    requestBody: {
      url,
      type: 'URL_UPDATED',
    },
  });

  const result: UrlNotificationResult = {
    url: response.data.urlNotificationMetadata?.url || url,
    type: 'URL_UPDATED',
    notifyTime: response.data.urlNotificationMetadata?.latestUpdate?.notifyTime || new Date().toISOString(),
  };

  if (save) {
    saveResult(result, 'indexing', 'request_indexing');
  }

  return result;
}

/**
 * Request indexing for multiple URLs
 *
 * @param urls - Array of URLs to request indexing for
 * @param options - Optional settings
 * @returns Array of notification results
 */
export async function requestIndexingBatch(urls: string[], options: IndexingOptions = {}): Promise<UrlNotificationResult[]> {
  const { save = true } = options;

  const results: UrlNotificationResult[] = [];

  // Process URLs sequentially to avoid rate limiting
  for (const url of urls) {
    const result = await requestIndexing(url, { save: false });
    results.push(result);
  }

  if (save) {
    saveResult(results, 'indexing', 'batch_indexing');
  }

  return results;
}

/**
 * Request URL removal from index
 *
 * @param url - The URL to request removal for
 * @param options - Optional settings
 * @returns Notification result
 */
export async function removeFromIndex(url: string, options: IndexingOptions = {}): Promise<UrlNotificationResult> {
  const { save = true } = options;

  const client = getIndexingClient();

  const response = await client.urlNotifications.publish({
    requestBody: {
      url,
      type: 'URL_DELETED',
    },
  });

  const result: UrlNotificationResult = {
    url: response.data.urlNotificationMetadata?.url || url,
    type: 'URL_DELETED',
    notifyTime: response.data.urlNotificationMetadata?.latestRemove?.notifyTime || new Date().toISOString(),
  };

  if (save) {
    saveResult(result, 'indexing', 'remove_from_index');
  }

  return result;
}

/**
 * Inspect a URL to check its index status
 *
 * @param url - The URL to inspect
 * @param options - Optional settings
 * @returns URL inspection result with index status
 */
export async function inspectUrl(url: string, options: IndexingOptions = {}): Promise<UrlInspectionResult> {
  const { save = true } = options;

  const client = getSearchConsoleClient();
  const siteUrl = getSiteUrl();

  const response = await client.urlInspection.index.inspect({
    requestBody: {
      inspectionUrl: url,
      siteUrl,
    },
  });

  const inspectionResult = response.data.inspectionResult;

  const result: UrlInspectionResult = {
    inspectionResultLink: inspectionResult?.inspectionResultLink || undefined,
    indexStatus: {
      verdict: (inspectionResult?.indexStatusResult?.verdict as 'PASS' | 'FAIL' | 'NEUTRAL') || 'NEUTRAL',
      coverageState: inspectionResult?.indexStatusResult?.coverageState || 'Unknown',
      robotsTxtState: inspectionResult?.indexStatusResult?.robotsTxtState || undefined,
      indexingState: inspectionResult?.indexStatusResult?.indexingState || undefined,
      lastCrawlTime: inspectionResult?.indexStatusResult?.lastCrawlTime || undefined,
      pageFetchState: inspectionResult?.indexStatusResult?.pageFetchState || undefined,
      googleCanonical: inspectionResult?.indexStatusResult?.googleCanonical || undefined,
      userCanonical: inspectionResult?.indexStatusResult?.userCanonical || undefined,
      crawledAs: inspectionResult?.indexStatusResult?.crawledAs || undefined,
    },
    mobileUsability: inspectionResult?.mobileUsabilityResult
      ? {
          verdict: inspectionResult.mobileUsabilityResult.verdict || 'NEUTRAL',
          issues: inspectionResult.mobileUsabilityResult.issues || [],
        }
      : undefined,
    richResults: inspectionResult?.richResultsResult
      ? {
          verdict: inspectionResult.richResultsResult.verdict || 'NEUTRAL',
          detectedItems: inspectionResult.richResultsResult.detectedItems || [],
        }
      : undefined,
  };

  if (save) {
    saveResult(result, 'indexing', 'url_inspection');
  }

  return result;
}
