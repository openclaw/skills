/**
 * YouTube Analytics Toolkit - Main Entry Point
 *
 * Simple interface for YouTube Data API v3 analysis.
 * All results are automatically saved to the /results directory with timestamps.
 *
 * Usage:
 *   import { getChannelStats, searchVideos } from './index.js';
 *   const stats = await getChannelStats('UCxxxxxxxx');
 */

// Re-export all API functions
export * from './api/channels.js';
export * from './api/videos.js';
export * from './api/search.js';

// Re-export core utilities
export { getClient, getApiKey, resetClient } from './core/client.js';
export { saveResult, loadResult, listResults, getLatestResult } from './core/storage.js';
export { getSettings, validateSettings } from './config/settings.js';

// Import for orchestration functions
import { getChannel, getChannelStats, getMultipleChannels } from './api/channels.js';
import { getVideo, getVideoStats, getMultipleVideos, getChannelVideos } from './api/videos.js';
import { searchVideos } from './api/search.js';
import { saveResult } from './core/storage.js';

// ============================================================================
// HIGH-LEVEL ORCHESTRATION FUNCTIONS
// ============================================================================

/**
 * Channel analysis result
 */
export interface ChannelAnalysis {
  channel: Awaited<ReturnType<typeof getChannel>>;
  recentVideos: Awaited<ReturnType<typeof getChannelVideos>>;
  stats: {
    subscribers: number;
    totalViews: number;
    videoCount: number;
    avgViewsPerVideo: number;
  };
}

/**
 * Comprehensive channel analysis - get channel info, recent videos, and calculated stats
 *
 * @param channelId - YouTube channel ID
 * @returns Channel data with recent videos and calculated metrics
 */
export async function analyzeChannel(channelId: string): Promise<ChannelAnalysis> {
  console.log('\n📺 Analyzing channel...');

  console.log('  → Getting channel info...');
  const channel = await getChannel(channelId, { save: false });

  console.log('  → Getting recent videos...');
  const recentVideos = await getChannelVideos(channelId, { maxResults: 50, save: false });

  // Calculate average views
  const totalVideoViews = recentVideos.reduce((sum, v) => sum + parseInt(v.statistics.viewCount, 10), 0);
  const avgViewsPerVideo = recentVideos.length > 0 ? Math.round(totalVideoViews / recentVideos.length) : 0;

  const result: ChannelAnalysis = {
    channel,
    recentVideos,
    stats: {
      subscribers: parseInt(channel.statistics.subscriberCount, 10),
      totalViews: parseInt(channel.statistics.viewCount, 10),
      videoCount: parseInt(channel.statistics.videoCount, 10),
      avgViewsPerVideo,
    },
  };

  // Save with channel name as filename
  saveResult(result, 'channels', 'channel_analysis', channel.title);

  console.log('✅ Channel analysis complete\n');
  return result;
}

/**
 * Compare multiple YouTube channels
 *
 * @param channelIds - Array of channel IDs to compare
 * @returns Comparison data for all channels
 */
export async function compareChannels(channelIds: string[]) {
  console.log(`\n📊 Comparing ${channelIds.length} channels...`);

  const channels = await getMultipleChannels(channelIds, { save: false });

  const comparison = channels.map(ch => ({
    id: ch.id,
    title: ch.title,
    subscribers: parseInt(ch.statistics.subscriberCount, 10),
    views: parseInt(ch.statistics.viewCount, 10),
    videoCount: parseInt(ch.statistics.videoCount, 10),
    viewsPerVideo: parseInt(ch.statistics.videoCount, 10) > 0
      ? Math.round(parseInt(ch.statistics.viewCount, 10) / parseInt(ch.statistics.videoCount, 10))
      : 0,
  }));

  // Sort by subscribers descending
  comparison.sort((a, b) => b.subscribers - a.subscribers);

  const result = {
    channels: comparison,
    summary: {
      totalChannels: comparison.length,
      totalSubscribers: comparison.reduce((sum, c) => sum + c.subscribers, 0),
      totalViews: comparison.reduce((sum, c) => sum + c.views, 0),
      topBySubscribers: comparison[0]?.title || 'N/A',
    },
  };

  saveResult(result, 'channels', 'channel_comparison');

  console.log('✅ Channel comparison complete\n');
  return result;
}

/**
 * Video analysis result
 */
export interface VideoAnalysis {
  video: Awaited<ReturnType<typeof getVideo>>;
  engagement: {
    views: number;
    likes: number;
    comments: number;
    likeRate: number;
    commentRate: number;
  };
}

/**
 * Analyze a single video's performance
 *
 * @param videoId - YouTube video ID
 * @returns Video data with engagement metrics
 */
export async function analyzeVideo(videoId: string): Promise<VideoAnalysis> {
  console.log('\n🎬 Analyzing video...');

  const video = await getVideo(videoId, { save: false });

  const views = parseInt(video.statistics.viewCount, 10);
  const likes = parseInt(video.statistics.likeCount, 10);
  const comments = parseInt(video.statistics.commentCount, 10);

  const result: VideoAnalysis = {
    video,
    engagement: {
      views,
      likes,
      comments,
      likeRate: views > 0 ? parseFloat(((likes / views) * 100).toFixed(2)) : 0,
      commentRate: views > 0 ? parseFloat(((comments / views) * 100).toFixed(4)) : 0,
    },
  };

  // Save with video title as filename
  saveResult(result, 'videos', 'video_analysis', video.title);

  console.log('✅ Video analysis complete\n');
  return result;
}

/**
 * Search and analyze top videos for a keyword
 *
 * @param query - Search query
 * @param maxResults - Number of results (default 10)
 * @returns Search results with video stats
 */
export async function searchAndAnalyze(query: string, maxResults = 10) {
  console.log(`\n🔍 Searching for "${query}"...`);

  console.log('  → Searching videos...');
  const searchResults = await searchVideos(query, { maxResults, save: false });

  const videoIds = searchResults.items
    .filter(item => item.id.videoId)
    .map(item => item.id.videoId as string);

  if (videoIds.length === 0) {
    return { query, videos: [] };
  }

  console.log(`  → Getting stats for ${videoIds.length} videos...`);
  const videos = await getMultipleVideos(videoIds, { save: false });

  const result = {
    query,
    videos: videos.map(v => ({
      id: v.id,
      title: v.title,
      channelTitle: v.channelTitle,
      views: parseInt(v.statistics.viewCount, 10),
      likes: parseInt(v.statistics.likeCount, 10),
      comments: parseInt(v.statistics.commentCount, 10),
      publishedAt: v.publishedAt,
    })),
  };

  const sanitizedQuery = query.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 30);
  saveResult(result, 'search', 'search_analysis', sanitizedQuery);

  console.log('✅ Search analysis complete\n');
  return result;
}

// Print help when run directly
if (process.argv[1] === new URL(import.meta.url).pathname) {
  console.log(`
YouTube Analytics Toolkit
=========================

Channel functions:
  - getChannel(channelId)              Get channel details
  - getChannelStats(channelId)         Get simplified stats (subscribers, views, videoCount)
  - getMultipleChannels(channelIds)    Get multiple channels at once
  - analyzeChannel(channelId)          Full channel analysis with recent videos
  - compareChannels(channelIds)        Compare multiple channels

Video functions:
  - getVideo(videoId)                  Get video details
  - getVideoStats(videoId)             Get simplified stats (views, likes, comments)
  - getMultipleVideos(videoIds)        Get multiple videos at once
  - getChannelVideos(channelId)        Get videos from a channel
  - analyzeVideo(videoId)              Full video analysis with engagement metrics

Search functions:
  - searchVideos(query, options?)      Search for videos
  - searchChannels(query, options?)    Search for channels
  - searchAndAnalyze(query)            Search and get full stats

All results are automatically saved to /results directory.
`);
}
