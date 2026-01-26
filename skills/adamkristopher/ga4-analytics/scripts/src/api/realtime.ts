/**
 * Realtime API - Live GA4 data
 */

import { getClient, getPropertyId } from '../core/client.js';
import { saveResult } from '../core/storage.js';

/**
 * Realtime report response structure
 */
export interface RealtimeResponse {
  dimensionHeaders?: Array<{ name: string }>;
  metricHeaders?: Array<{ name: string }>;
  rows?: Array<{
    dimensionValues: Array<{ value: string }>;
    metricValues: Array<{ value: string }>;
  }>;
  rowCount?: number;
}

/**
 * Get current active users
 */
export async function getActiveUsers(save = true): Promise<RealtimeResponse> {
  const client = getClient();
  const property = getPropertyId();

  const [response] = await client.runRealtimeReport({
    property,
    dimensions: [{ name: 'unifiedScreenName' }],
    metrics: [{ name: 'activeUsers' }],
  });

  if (save) {
    saveResult(response, 'realtime', 'active_users');
  }

  return response as RealtimeResponse;
}

/**
 * Get current event data
 */
export async function getRealtimeEvents(save = true): Promise<RealtimeResponse> {
  const client = getClient();
  const property = getPropertyId();

  const [response] = await client.runRealtimeReport({
    property,
    dimensions: [{ name: 'eventName' }],
    metrics: [{ name: 'eventCount' }],
  });

  if (save) {
    saveResult(response, 'realtime', 'events');
  }

  return response as RealtimeResponse;
}

/**
 * Get currently viewed pages
 */
export async function getRealtimePages(save = true): Promise<RealtimeResponse> {
  const client = getClient();
  const property = getPropertyId();

  const [response] = await client.runRealtimeReport({
    property,
    dimensions: [{ name: 'unifiedScreenName' }],
    metrics: [{ name: 'screenPageViews' }],
  });

  if (save) {
    saveResult(response, 'realtime', 'pages');
  }

  return response as RealtimeResponse;
}

/**
 * Get realtime traffic sources
 */
export async function getRealtimeSources(save = true): Promise<RealtimeResponse> {
  const client = getClient();
  const property = getPropertyId();

  const [response] = await client.runRealtimeReport({
    property,
    dimensions: [{ name: 'firstUserSource' }, { name: 'firstUserMedium' }],
    metrics: [{ name: 'activeUsers' }],
  });

  if (save) {
    saveResult(response, 'realtime', 'sources');
  }

  return response as RealtimeResponse;
}
