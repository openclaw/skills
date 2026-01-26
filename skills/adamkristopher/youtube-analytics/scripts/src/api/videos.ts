/**
 * Videos API - YouTube video data retrieval
 */

import { getClient } from '../core/client.js';
import { saveResult } from '../core/storage.js';
import { getChannel } from './channels.js';

/**
 * Video options
 */
export interface VideoOptions {
  save?: boolean;
}

/**
 * Channel videos options
 */
export interface ChannelVideosOptions {
  maxResults?: number;
  save?: boolean;
}

/**
 * Video response with normalized data
 */
export interface VideoResponse {
  id: string;
  title: string;
  description: string;
  publishedAt: string;
  channelId: string;
  channelTitle: string;
  tags?: string[];
  thumbnails?: {
    default?: { url: string };
    medium?: { url: string };
    high?: { url: string };
  };
  statistics: {
    viewCount: string;
    likeCount: string;
    commentCount: string;
  };
  duration?: string;
}

/**
 * Simplified video statistics
 */
export interface VideoStats {
  views: number;
  likes: number;
  comments: number;
}

/**
 * Get video by ID
 *
 * @param videoId - YouTube video ID
 * @param options - Optional settings
 * @returns Video data
 */
export async function getVideo(videoId: string, options: VideoOptions = {}): Promise<VideoResponse> {
  const { save = true } = options;

  const client = getClient();

  const response = await client.videos.list({
    id: [videoId],
    part: ['snippet', 'statistics', 'contentDetails'],
  });

  const item = response.data.items?.[0];
  if (!item) {
    throw new Error(`Video not found: ${videoId}`);
  }

  const result: VideoResponse = {
    id: item.id || videoId,
    title: item.snippet?.title || '',
    description: item.snippet?.description || '',
    publishedAt: item.snippet?.publishedAt || '',
    channelId: item.snippet?.channelId || '',
    channelTitle: item.snippet?.channelTitle || '',
    tags: item.snippet?.tags,
    thumbnails: item.snippet?.thumbnails as VideoResponse['thumbnails'],
    statistics: {
      viewCount: item.statistics?.viewCount || '0',
      likeCount: item.statistics?.likeCount || '0',
      commentCount: item.statistics?.commentCount || '0',
    },
    duration: item.contentDetails?.duration,
  };

  if (save) {
    saveResult(result, 'videos', 'video', videoId);
  }

  return result;
}

/**
 * Get simplified video statistics
 *
 * @param videoId - YouTube video ID
 * @returns Simplified stats with numbers
 */
export async function getVideoStats(videoId: string): Promise<VideoStats> {
  const video = await getVideo(videoId, { save: false });

  return {
    views: parseInt(video.statistics.viewCount, 10),
    likes: parseInt(video.statistics.likeCount, 10),
    comments: parseInt(video.statistics.commentCount, 10),
  };
}

/**
 * Get multiple videos in a single API call
 *
 * @param videoIds - Array of video IDs
 * @param options - Optional settings
 * @returns Array of video data
 */
export async function getMultipleVideos(videoIds: string[], options: VideoOptions = {}): Promise<VideoResponse[]> {
  const { save = true } = options;

  const client = getClient();

  const response = await client.videos.list({
    id: videoIds,
    part: ['snippet', 'statistics', 'contentDetails'],
  });

  const results: VideoResponse[] = (response.data.items || []).map(item => ({
    id: item.id || '',
    title: item.snippet?.title || '',
    description: item.snippet?.description || '',
    publishedAt: item.snippet?.publishedAt || '',
    channelId: item.snippet?.channelId || '',
    channelTitle: item.snippet?.channelTitle || '',
    tags: item.snippet?.tags,
    thumbnails: item.snippet?.thumbnails as VideoResponse['thumbnails'],
    statistics: {
      viewCount: item.statistics?.viewCount || '0',
      likeCount: item.statistics?.likeCount || '0',
      commentCount: item.statistics?.commentCount || '0',
    },
    duration: item.contentDetails?.duration,
  }));

  if (save) {
    saveResult(results, 'videos', 'multiple_videos');
  }

  return results;
}

/**
 * Get videos from a channel's uploads playlist
 *
 * @param channelId - YouTube channel ID
 * @param options - Optional settings including maxResults
 * @returns Array of video data
 */
export async function getChannelVideos(channelId: string, options: ChannelVideosOptions = {}): Promise<VideoResponse[]> {
  const { maxResults = 50, save = true } = options;

  const client = getClient();

  // First, get the channel's uploads playlist ID
  const channel = await getChannel(channelId, { save: false });
  const uploadsPlaylistId = channel.uploadsPlaylistId;

  if (!uploadsPlaylistId) {
    throw new Error(`Could not find uploads playlist for channel: ${channelId}`);
  }

  // Get playlist items
  const playlistResponse = await client.playlistItems.list({
    playlistId: uploadsPlaylistId,
    part: ['snippet'],
    maxResults,
  });

  // Extract video IDs
  const videoIds = (playlistResponse.data.items || [])
    .map(item => item.snippet?.resourceId?.videoId)
    .filter((id): id is string => !!id);

  if (videoIds.length === 0) {
    return [];
  }

  // Get full video details
  const videos = await getMultipleVideos(videoIds, { save: false });

  if (save) {
    saveResult(videos, 'videos', 'channel_videos', channelId);
  }

  return videos;
}
