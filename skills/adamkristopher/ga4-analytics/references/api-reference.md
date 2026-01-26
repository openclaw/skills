# API Reference

Complete function reference for all GA4 Analytics Toolkit modules.

## Table of Contents

- [Reports API](#reports-api) (7 functions)
- [Realtime API](#realtime-api) (4 functions)
- [Metadata API](#metadata-api) (3 functions)
- [Search Console API](#search-console-api) (6 functions)
- [Indexing API](#indexing-api) (4 functions)
- [Bulk Lookup API](#bulk-lookup-api) (3 functions)
- [Storage](#storage) (4 functions)

---

## Reports API

Import: `from './api/reports.js'`

### `parseDateRange(range?)`

Parse shorthand date range (e.g., "7d", "30d") to GA4 date range format.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `range` | `string \| DateRange \| undefined` | Settings default | Date range to parse |

**Returns:** `DateRange` — `{startDate: string, endDate: string}`

### `runReport(options)`

Run a custom GA4 report with arbitrary dimensions and metrics.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `options.dimensions` | `string[]` | required | GA4 dimension names |
| `options.metrics` | `string[]` | required | GA4 metric names |
| `options.dateRange` | `string \| DateRange` | `"30d"` | Date range |
| `options.filters` | `Record<string, string>` | `undefined` | Dimension filters |
| `options.orderBy` | `string[]` | `undefined` | Sort order |
| `options.limit` | `number` | `undefined` | Row limit |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<ReportResponse>` — Rows with dimension and metric values.

### `getPageViews(dateRange?)`

Get page view data with paths, titles, users, and session duration.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| DateRange` | `"30d"` | Date range |

**Dimensions:** `pagePath`, `pageTitle`
**Metrics:** `screenPageViews`, `activeUsers`, `averageSessionDuration`

### `getTrafficSources(dateRange?)`

Get traffic source data by source, medium, and campaign.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| DateRange` | `"30d"` | Date range |

**Dimensions:** `sessionSource`, `sessionMedium`, `sessionCampaignName`
**Metrics:** `sessions`, `activeUsers`, `newUsers`, `bounceRate`

### `getUserDemographics(dateRange?)`

Get user demographic data by country, device, and browser.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| DateRange` | `"30d"` | Date range |

**Dimensions:** `country`, `deviceCategory`, `browser`
**Metrics:** `activeUsers`, `sessions`, `newUsers`

### `getEventCounts(dateRange?)`

Get event count data by event name.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| DateRange` | `"30d"` | Date range |

**Dimensions:** `eventName`
**Metrics:** `eventCount`, `eventCountPerUser`, `activeUsers`

### `getConversions(dateRange?)`

Get conversion data by event name and source.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| DateRange` | `"30d"` | Date range |

**Dimensions:** `eventName`, `sessionSource`
**Metrics:** `conversions`, `totalRevenue`

### `getEcommerceRevenue(dateRange?)`

Get e-commerce revenue data by date and transaction.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| DateRange` | `"30d"` | Date range |

**Dimensions:** `date`, `transactionId`
**Metrics:** `totalRevenue`, `ecommercePurchases`, `averagePurchaseRevenue`

---

## Realtime API

Import: `from './api/realtime.js'`

### `getActiveUsers(save?)`

Get current active users by screen/page name.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<RealtimeResponse>` — Active users by `unifiedScreenName`.

### `getRealtimeEvents(save?)`

Get currently firing events.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<RealtimeResponse>` — Event counts by `eventName`.

### `getRealtimePages(save?)`

Get currently viewed pages.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<RealtimeResponse>` — Page views by `unifiedScreenName`.

### `getRealtimeSources(save?)`

Get current traffic sources.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<RealtimeResponse>` — Active users by `firstUserSource` and `firstUserMedium`.

---

## Metadata API

Import: `from './api/metadata.js'`

### `getAvailableDimensions(save?)`

Get all available dimensions for the GA4 property.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<MetadataResponse>` — Array of `{apiName, uiName, description}`.

### `getAvailableMetrics(save?)`

Get all available metrics for the GA4 property.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<MetadataResponse>` — Array of `{apiName, uiName, description}`.

### `getPropertyMetadata(save?)`

Get full property metadata (dimensions + metrics combined).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<MetadataResponse>` — Full metadata response.

---

## Search Console API

Import: `from './api/searchConsole.js'`

### `querySearchAnalytics(options)`

Run a custom Search Console analytics query.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `options.dimensions` | `string[]` | `["query"]` | Dimensions: `query`, `page`, `device`, `country`, `searchAppearance` |
| `options.dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |
| `options.rowLimit` | `number` | `1000` | Max rows |
| `options.startRow` | `number` | `0` | Pagination offset |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<SearchAnalyticsResponse>` — Rows with `{keys, clicks, impressions, ctr, position}`.

### `getTopQueries(dateRange?)`

Get top 100 search queries by clicks.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |

**Returns:** `Promise<SearchAnalyticsResponse>`

### `getTopPages(dateRange?)`

Get top 100 pages by search impressions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |

**Returns:** `Promise<SearchAnalyticsResponse>`

### `getDevicePerformance(dateRange?)`

Get search performance breakdown by device type (desktop, mobile, tablet).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |

**Returns:** `Promise<SearchAnalyticsResponse>`

### `getCountryPerformance(dateRange?)`

Get search performance by country (top 50).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |

**Returns:** `Promise<SearchAnalyticsResponse>`

### `getSearchAppearance(dateRange?)`

Get search appearance data (rich results, AMP, etc.).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |

**Returns:** `Promise<SearchAnalyticsResponse>`

---

## Indexing API

Import: `from './api/indexing.js'`

### `requestIndexing(url, options?)`

Request Google to re-crawl a single URL.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `string` | required | Full URL to request indexing for |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<UrlNotificationResult>` — `{url, type: 'URL_UPDATED', notifyTime}`.

### `requestIndexingBatch(urls, options?)`

Request re-crawling for multiple URLs (processed sequentially to avoid rate limits).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `urls` | `string[]` | required | Array of URLs |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<UrlNotificationResult[]>`

### `removeFromIndex(url, options?)`

Request URL removal from Google's index.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `string` | required | URL to remove |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<UrlNotificationResult>` — `{url, type: 'URL_DELETED', notifyTime}`.

### `inspectUrl(url, options?)`

Check a URL's index status, mobile usability, and rich results.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `string` | required | URL to inspect |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<UrlInspectionResult>` — Contains `indexStatus.verdict` ('PASS' | 'FAIL' | 'NEUTRAL'), `coverageState`, `lastCrawlTime`, `mobileUsability`, `richResults`.

---

## Bulk Lookup API

Import: `from './api/bulk-lookup.js'`

### `normalizeUrls(urls)`

Normalize page paths: trim whitespace, add leading slash.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `urls` | `string[]` | required | Array of page paths |

**Returns:** `string[]` — Normalized paths.

### `buildUrlFilter(urls)`

Build a GA4 dimension filter expression for a list of page paths.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `urls` | `string[]` | required | Normalized page paths |

**Returns:** `DimensionFilterExpression | null`

### `getMetricsForUrls(urls, options?)`

Get GA4 metrics for specific page paths (bulk lookup).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `urls` | `string[]` | required | Page paths (e.g., `["/pricing", "/about"]`) |
| `options.dateRange` | `string \| DateRange` | `"30d"` | Date range |
| `options.metrics` | `string[]` | `["screenPageViews", "activeUsers", "averageSessionDuration", "bounceRate", "engagementRate"]` | Metrics to retrieve |
| `options.save` | `boolean` | `true` | Save results to JSON |

**Returns:** `Promise<ReportResponse>` — Metrics for each URL.

---

## Storage

Import: `from './core/storage.js'`

### `saveResult<T>(data, category, operation, extraInfo?)`

Save result data to a timestamped JSON file with metadata wrapper.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `T` | required | Data to save |
| `category` | `string` | required | Category directory (e.g., `"reports"`, `"realtime"`) |
| `operation` | `string` | required | Operation name (e.g., `"page_views"`) |
| `extraInfo` | `string` | `undefined` | Optional extra info for filename |

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
