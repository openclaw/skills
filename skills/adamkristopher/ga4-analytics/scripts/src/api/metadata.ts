/**
 * Metadata API - Available dimensions and metrics
 */

import { getClient, getPropertyId } from '../core/client.js';
import { saveResult } from '../core/storage.js';

/**
 * Dimension metadata
 */
export interface DimensionMetadata {
  apiName: string;
  uiName: string;
  description: string;
}

/**
 * Metric metadata
 */
export interface MetricMetadata {
  apiName: string;
  uiName: string;
  description: string;
}

/**
 * Full property metadata response
 */
export interface MetadataResponse {
  name?: string;
  dimensions?: DimensionMetadata[];
  metrics?: MetricMetadata[];
}

/**
 * Get all available dimensions for the property
 */
export async function getAvailableDimensions(save = true): Promise<MetadataResponse> {
  const client = getClient();
  const property = getPropertyId();

  const [response] = await client.getMetadata({
    name: `${property}/metadata`,
  });

  const result = {
    dimensions: response.dimensions || [],
  };

  if (save) {
    saveResult(result, 'metadata', 'dimensions');
  }

  return result as MetadataResponse;
}

/**
 * Get all available metrics for the property
 */
export async function getAvailableMetrics(save = true): Promise<MetadataResponse> {
  const client = getClient();
  const property = getPropertyId();

  const [response] = await client.getMetadata({
    name: `${property}/metadata`,
  });

  const result = {
    metrics: response.metrics || [],
  };

  if (save) {
    saveResult(result, 'metadata', 'metrics');
  }

  return result as MetadataResponse;
}

/**
 * Get full property metadata (dimensions and metrics)
 */
export async function getPropertyMetadata(save = true): Promise<MetadataResponse> {
  const client = getClient();
  const property = getPropertyId();

  const [response] = await client.getMetadata({
    name: `${property}/metadata`,
  });

  if (save) {
    saveResult(response, 'metadata', 'full');
  }

  return response as MetadataResponse;
}
