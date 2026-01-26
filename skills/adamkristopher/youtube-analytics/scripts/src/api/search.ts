/**
 * Search API - YouTube search functionality
 */

import { getClient } from '../core/client.js';
import { saveResult } from '../core/storage.js';
import { getSettings } from '../config/settings.js';

/**
 * Search options
 */
export interface SearchOptions {
  maxResults?: number;
  publishedAfter?: string;
  publishedBefore?: string;
  order?: 'date' | 'rating' | 'relevance' | 'title' | 'videoCount' | 'viewCount';
  save?: boolean;
}

/**
 * Search result item
 */
export interface SearchResultItem {
  id: {
    kind: string;
    videoId?: string;
    channelId?: string;
    playlistId?: string;
  };
  snippet: {
    title: string;
    description: string;
    publishedAt: string;
    channelId: string;
    channelTitle: string;
    thumbnails?: {
      default?: { url: string };
      medium?: { url: string };
      high?: { url: string };
    };
  };
}

/**
 * Search response
 */
export interface SearchResponse {
  items: SearchResultItem[];
  pageInfo?: {
    totalResults: number;
    resultsPerPage: number;
  };
  nextPageToken?: string;
  prevPageToken?: string;
}

/**
 * Search for videos
 *
 * @param query - Search query string
 * @param options - Optional settings
 * @returns Search results
 */
export async function searchVideos(query: string, options: SearchOptions = {}): Promise<SearchResponse> {
  const settings = getSettings();
  const {
    maxResults = settings.defaultMaxResults,
    publishedAfter,
    publishedBefore,
    order = 'relevance',
    save = true,
  } = options;

  const client = getClient();

  const response = await client.search.list({
    q: query,
    type: ['video'],
    part: ['snippet'],
    maxResults,
    order,
    ...(publishedAfter && { publishedAfter }),
    ...(publishedBefore && { publishedBefore }),
  });

  const result: SearchResponse = {
    items: (response.data.items || []).map(item => ({
      id: {
        kind: item.id?.kind || '',
        videoId: item.id?.videoId,
        channelId: item.id?.channelId,
        playlistId: item.id?.playlistId,
      },
      snippet: {
        title: item.snippet?.title || '',
        description: item.snippet?.description || '',
        publishedAt: item.snippet?.publishedAt || '',
        channelId: item.snippet?.channelId || '',
        channelTitle: item.snippet?.channelTitle || '',
        thumbnails: item.snippet?.thumbnails as SearchResultItem['snippet']['thumbnails'],
      },
    })),
    pageInfo: response.data.pageInfo as SearchResponse['pageInfo'],
    nextPageToken: response.data.nextPageToken || undefined,
    prevPageToken: response.data.prevPageToken || undefined,
  };

  if (save) {
    const sanitizedQuery = query.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30);
    saveResult(result, 'search', 'videos', sanitizedQuery);
  }

  return result;
}

/**
 * Search for channels
 *
 * @param query - Search query string
 * @param options - Optional settings
 * @returns Search results
 */
export async function searchChannels(query: string, options: SearchOptions = {}): Promise<SearchResponse> {
  const settings = getSettings();
  const {
    maxResults = settings.defaultMaxResults,
    order = 'relevance',
    save = true,
  } = options;

  const client = getClient();

  const response = await client.search.list({
    q: query,
    type: ['channel'],
    part: ['snippet'],
    maxResults,
    order,
  });

  const result: SearchResponse = {
    items: (response.data.items || []).map(item => ({
      id: {
        kind: item.id?.kind || '',
        videoId: item.id?.videoId,
        channelId: item.id?.channelId,
        playlistId: item.id?.playlistId,
      },
      snippet: {
        title: item.snippet?.title || '',
        description: item.snippet?.description || '',
        publishedAt: item.snippet?.publishedAt || '',
        channelId: item.snippet?.channelId || '',
        channelTitle: item.snippet?.channelTitle || '',
        thumbnails: item.snippet?.thumbnails as SearchResultItem['snippet']['thumbnails'],
      },
    })),
    pageInfo: response.data.pageInfo as SearchResponse['pageInfo'],
    nextPageToken: response.data.nextPageToken || undefined,
    prevPageToken: response.data.prevPageToken || undefined,
  };

  if (save) {
    const sanitizedQuery = query.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30);
    saveResult(result, 'search', 'channels', sanitizedQuery);
  }

  return result;
}
