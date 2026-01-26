# API Reference

Complete function reference for all YouTube Analytics Toolkit modules.

## Table of Contents

- [Channel API](#channel-api) (3 functions)
- [Video API](#video-api) (4 functions)
- [Search API](#search-api) (2 functions)
- [Orchestration](#orchestration) (4 functions)
- [Storage](#storage) (4 functions)

---

## Channel API

Import: `from './api/channels.js'`

### `getChannel(channelId, options?)`

Get full channel details by ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channelId` | `string` | required | YouTube channel ID (starts with UC) |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<ChannelResponse>` — `{id, title, description, customUrl?, publishedAt, country?, thumbnails?, statistics: {viewCount, subscriberCount, videoCount}, uploadsPlaylistId?}`

### `getChannelStats(channelId)`

Get simplified channel statistics as numbers.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channelId` | `string` | required | YouTube channel ID |

**Returns:** `Promise<ChannelStats>` — `{subscribers: number, views: number, videoCount: number}`

### `getMultipleChannels(channelIds, options?)`

Get multiple channels in a single API call.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channelIds` | `string[]` | required | Array of channel IDs |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<ChannelResponse[]>`

---

## Video API

Import: `from './api/videos.js'`

### `getVideo(videoId, options?)`

Get full video details by ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `videoId` | `string` | required | YouTube video ID |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<VideoResponse>` — `{id, title, description, publishedAt, channelId, channelTitle, tags?, thumbnails?, statistics: {viewCount, likeCount, commentCount}, duration?}`

### `getVideoStats(videoId)`

Get simplified video statistics as numbers.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `videoId` | `string` | required | YouTube video ID |

**Returns:** `Promise<VideoStats>` — `{views: number, likes: number, comments: number}`

### `getMultipleVideos(videoIds, options?)`

Get multiple videos in a single API call.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `videoIds` | `string[]` | required | Array of video IDs |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<VideoResponse[]>`

### `getChannelVideos(channelId, options?)`

Get videos from a channel's uploads playlist.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channelId` | `string` | required | YouTube channel ID |
| `options.maxResults` | `number` | `50` | Maximum videos to return |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<VideoResponse[]>` — Array of full video details from the channel's recent uploads.

---

## Search API

Import: `from './api/search.js'`

### `searchVideos(query, options?)`

Search YouTube for videos.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `string` | required | Search query string |
| `options.maxResults` | `number` | `50` | Maximum results |
| `options.publishedAfter` | `string` | `undefined` | ISO date filter (e.g., `"2024-01-01T00:00:00Z"`) |
| `options.publishedBefore` | `string` | `undefined` | ISO date filter |
| `options.order` | `string` | `"relevance"` | Sort order: `date`, `rating`, `relevance`, `title`, `videoCount`, `viewCount` |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<SearchResponse>` — `{items: [{id: {kind, videoId?, channelId?}, snippet: {title, description, publishedAt, channelId, channelTitle, thumbnails?}}], pageInfo?, nextPageToken?, prevPageToken?}`

### `searchChannels(query, options?)`

Search YouTube for channels.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `string` | required | Search query string |
| `options.maxResults` | `number` | `50` | Maximum results |
| `options.order` | `string` | `"relevance"` | Sort order: `date`, `rating`, `relevance`, `title`, `videoCount`, `viewCount` |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<SearchResponse>`

---

## Orchestration

Import: `from './index.js'`

### `analyzeChannel(channelId)`

Comprehensive channel analysis — fetches channel info, recent videos, and calculates average views per video.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channelId` | `string` | required | YouTube channel ID |

**Returns:** `Promise<ChannelAnalysis>` — `{channel: ChannelResponse, recentVideos: VideoResponse[], stats: {subscribers, totalViews, videoCount, avgViewsPerVideo}}`

### `compareChannels(channelIds)`

Compare multiple YouTube channels side by side. Returns channels sorted by subscriber count.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channelIds` | `string[]` | required | Array of channel IDs to compare |

**Returns:** `Promise<{channels: [{id, title, subscribers, views, videoCount, viewsPerVideo}], summary: {totalChannels, totalSubscribers, totalViews, topBySubscribers}}>`

### `analyzeVideo(videoId)`

Analyze a single video's performance with engagement metrics.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `videoId` | `string` | required | YouTube video ID |

**Returns:** `Promise<VideoAnalysis>` — `{video: VideoResponse, engagement: {views, likes, comments, likeRate, commentRate}}`

### `searchAndAnalyze(query, maxResults?)`

Search for videos and get full statistics for each result.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `string` | required | Search query |
| `maxResults` | `number` | `10` | Number of results |

**Returns:** `Promise<{query, videos: [{id, title, channelTitle, views, likes, comments, publishedAt}]}>`

---

## Storage

Import: `from './core/storage.js'`

### `saveResult<T>(data, category, operation, name?)`

Save result data to a JSON file with metadata wrapper.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `T` | required | Data to save |
| `category` | `string` | required | Category directory (e.g., `"channels"`, `"videos"`) |
| `operation` | `string` | required | Operation name (e.g., `"channel_analysis"`) |
| `name` | `string` | `undefined` | Optional name for filename |

**Returns:** `string` — Full path to the saved file.

### `loadResult<T>(filepath)`

Load a previously saved result from a JSON file.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filepath` | `string` | required | Path to the JSON file |

**Returns:** `SavedResult<T> | null`

### `listResults(category, limit?)`

List saved result files for a category, sorted newest first.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | `string` | required | Category to list |
| `limit` | `number` | `undefined` | Max results to return |

**Returns:** `string[]` — Array of file paths.

### `getLatestResult<T>(category, operation?)`

Get the most recent result for a category, optionally filtered by operation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | `string` | required | Category to search |
| `operation` | `string` | `undefined` | Filter by operation name |

**Returns:** `SavedResult<T> | null`
