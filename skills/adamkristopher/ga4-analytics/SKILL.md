---
name: ga4-analytics
description: "Google Analytics 4, Search Console, and Indexing API toolkit. Analyze website traffic, page performance, user demographics, real-time visitors, search queries, and SEO metrics. Use when the user asks to: check site traffic, analyze page views, see traffic sources, view user demographics, get real-time visitor data, check search console queries, analyze SEO performance, request URL re-indexing, inspect index status, compare date ranges, check bounce rates, view conversion data, or get e-commerce revenue. Requires a Google Cloud service account with GA4 and Search Console access."
---

# GA4 Analytics Toolkit

## Setup

Install dependencies:

```bash
cd scripts && npm install
```

Configure credentials by creating a `.env` file in the project root:

```
GA4_PROPERTY_ID=123456789
GA4_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
GA4_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
SEARCH_CONSOLE_SITE_URL=https://your-domain.com
GA4_DEFAULT_DATE_RANGE=30d
```

**Prerequisites**: A Google Cloud project with the Analytics Data API, Search Console API, and Indexing API enabled. A service account with access to your GA4 property and Search Console.

## Quick Start

| User says | Function to call |
|-----------|-----------------|
| "Show me site traffic for the last 30 days" | `siteOverview("30d")` |
| "What are my top search queries?" | `searchConsoleOverview("30d")` |
| "Who's on the site right now?" | `liveSnapshot()` |
| "Reindex these URLs" | `reindexUrls(["https://example.com/page1", ...])` |
| "Compare this month vs last month" | `compareDateRanges({startDate: "30daysAgo", endDate: "today"}, {startDate: "60daysAgo", endDate: "31daysAgo"})` |
| "What pages get the most traffic?" | `contentPerformance("30d")` |

Execute functions by importing from `scripts/src/index.ts`:

```typescript
import { siteOverview, searchConsoleOverview } from './scripts/src/index.js';

const overview = await siteOverview('30d');
```

Or run directly with tsx:

```bash
npx tsx scripts/src/index.ts
```

## Workflow Pattern

Every analysis follows three phases:

### 1. Analyze
Run API functions. Each call hits the Google APIs and returns structured data.

### 2. Auto-Save
All results automatically save as timestamped JSON files to `results/{category}/`. File naming pattern: `YYYYMMDD_HHMMSS__operation__extra_info.json`

### 3. Summarize
After analysis, read the saved JSON files and create a markdown summary in `results/summaries/` with data tables, trends, and recommendations.

## High-Level Functions

### GA4 Analytics

| Function | Purpose | What it gathers |
|----------|---------|----------------|
| `siteOverview(dateRange?)` | Comprehensive site snapshot | Page views, traffic sources, demographics, events |
| `trafficAnalysis(dateRange?)` | Traffic deep-dive | Sources, sessions by source/medium, new vs returning |
| `contentPerformance(dateRange?)` | Top pages analysis | Page views, landing pages, exit pages |
| `userBehavior(dateRange?)` | Engagement patterns | Demographics, events, daily engagement metrics |
| `compareDateRanges(range1, range2)` | Period comparison | Side-by-side metrics for two date ranges |
| `liveSnapshot()` | Real-time data | Active users, current pages, current events |

### Search Console

| Function | Purpose | What it gathers |
|----------|---------|----------------|
| `searchConsoleOverview(dateRange?)` | SEO snapshot | Top queries, pages, device, country breakdown |
| `keywordAnalysis(dateRange?)` | Keyword deep-dive | Queries with device breakdown |
| `seoPagePerformance(dateRange?)` | Page SEO metrics | Top pages by clicks, country breakdown |

### Indexing

| Function | Purpose |
|----------|---------|
| `reindexUrls(urls)` | Request re-indexing for multiple URLs |
| `checkIndexStatus(urls)` | Check if URLs are indexed |

### Utility

| Function | Purpose |
|----------|---------|
| `getAvailableFields()` | List all available GA4 dimensions and metrics |

### Individual API Functions

For granular control, import specific functions from the API modules. See [references/api-reference.md](references/api-reference.md) for the complete list of 30+ API functions with parameters, types, and examples.

## Date Ranges

All functions accept flexible date range formats:

| Format | Example | Description |
|--------|---------|-------------|
| Shorthand | `"7d"`, `"30d"`, `"90d"` | Days ago to today |
| Explicit | `{startDate: "2024-01-01", endDate: "2024-01-31"}` | Specific dates |
| GA4 relative | `{startDate: "30daysAgo", endDate: "today"}` | GA4 relative format |

Default is `"30d"` (configurable via `GA4_DEFAULT_DATE_RANGE` in `.env`).

## Results Storage

Results auto-save to `results/` with this structure:

```
results/
├── reports/          # GA4 standard reports
├── realtime/         # Real-time snapshots
├── searchconsole/    # Search Console data
├── indexing/         # Indexing API results
└── summaries/        # Human-readable markdown summaries
```

### Managing Results

```typescript
import { listResults, loadResult, getLatestResult } from './scripts/src/index.js';

// List recent results
const files = listResults('reports', 10);

// Load a specific result
const data = loadResult(files[0]);

// Get most recent result for an operation
const latest = getLatestResult('reports', 'site_overview');
```

## Common Dimensions and Metrics

### Dimensions
`pagePath`, `pageTitle`, `sessionSource`, `sessionMedium`, `country`, `deviceCategory`, `browser`, `date`, `eventName`, `landingPage`, `newVsReturning`

### Metrics
`screenPageViews`, `activeUsers`, `sessions`, `newUsers`, `bounceRate`, `averageSessionDuration`, `engagementRate`, `conversions`, `totalRevenue`, `eventCount`

## Tips

1. **Specify date ranges** — "last 7 days" or "last 90 days" gives different insights than the default 30 days
2. **Request summaries** — After pulling data, ask for a markdown summary with tables and insights
3. **Compare periods** — Use `compareDateRanges()` to spot trends (this month vs last month)
4. **Check real-time data** — `liveSnapshot()` shows who's on the site right now
5. **Combine GA4 + Search Console** — Traffic data plus search query data gives the full picture
