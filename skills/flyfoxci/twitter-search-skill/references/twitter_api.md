# Twitter API Reference

This document provides detailed reference information for the Twitter Advanced Search API.

## API Endpoint

- **URL**: `https://api.twitterapi.io/twitter/tweet/advanced_search`
- **Method**: `GET`
- **Documentation**: https://docs.twitterapi.io/api-reference/endpoint/tweet_advanced_search

## Authentication

- **Header**: `X-API-Key`
- **Type**: Bearer token / API key
- **Required**: Yes

The API key should be obtained from https://twitterapi.io

## Request Parameters

### Query Parameter (`query`)

The search query supports Twitter's advanced search syntax:

#### Basic Keywords
- Single word: `AI`
- Multiple words: `"artificial intelligence"`
- OR logic: `AI OR "machine learning"`
- AND logic: `AI "machine learning"` (implicit AND)

#### User Filtering
- From specific user: `from:username`
- To specific user: `to:username`
- Mentioning user: `@username`

#### Date Filtering
- Since date: `since:2024-01-01`
- Until date: `until:2024-12-31`
- Combined: `since:2024-01-01 until:2024-12-31`

#### Language Filtering
- Specific language: `lang:en` (English)
- Language codes: en, es, fr, de, ja, zh, etc.

#### Content Type Filtering
- Hashtags: `#hashtag`
- Links: `filter:links`
- Replies: `filter:replies`
- Media: `filter:media`
- Verified users: `filter:verified`

#### Engagement Filtering
- Minimum retweets: `min_retweets:10`
- Minimum favorites: `min_faves:100`
- Minimum replies: `min_replies:5`

#### Complex Query Examples
```
# AI-related tweets from verified users in English
AI OR "machine learning" lang:en filter:verified

# Recent tweets about Bitcoin from influencers
Bitcoin from:elonmusk OR from:VitalikButerin since:2024-01-01

# Tweets with links about climate change
"climate change" filter:links lang:en

# Popular tweets about tech
tech min_retweets:100 min_faves:500
```

**Reference**: https://github.com/igorbrigadir/twitter-advanced-search

### Query Type (`queryType`)

- **Values**: `Latest` or `Top`
- **Default**: `Latest`
- **Description**:
  - `Latest`: Most recent tweets first
  - `Top`: Most relevant/popular tweets first (recommended for analysis)

### Cursor (`cursor`)

- **Type**: String
- **Default**: `""` (empty for first page)
- **Description**: Pagination token for fetching subsequent pages

## Response Format

### Top-Level Structure

```json
{
  "tweets": [...],      // Array of tweet objects
  "has_next_page": true, // Boolean: more results available
  "next_cursor": "..."   // String: cursor for next page
}
```

### Tweet Object Structure

#### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique tweet identifier |
| `url` | string | Tweet URL (e.g., https://x.com/user/status/123) |
| `text` | string | Tweet content |
| `createdAt` | string | Creation timestamp (e.g., "Tue Dec 10 07:00:30 +0000 2024") |
| `lang` | string | Language code (e.g., "en", "es") |
| `source` | string | Source app (e.g., "Twitter for iPhone") |

#### Engagement Metrics

| Field | Type | Description |
|-------|------|-------------|
| `retweetCount` | integer | Number of retweets |
| `replyCount` | integer | Number of replies |
| `likeCount` | integer | Number of likes |
| `quoteCount` | integer | Number of quote tweets |
| `viewCount` | integer | Number of views |
| `bookmarkCount` | integer | Number of bookmarks |

#### Reply/Thread Fields

| Field | Type | Description |
|-------|------|-------------|
| `isReply` | boolean | Whether this is a reply |
| `inReplyToId` | string | ID of the tweet being replied to |
| `inReplyToUserId` | string | ID of the user being replied to |
| `inReplyToUsername` | string | Username of the user being replied to |
| `conversationId` | string | Thread/conversation identifier |
| `displayTextRange` | array | Visible text range indices |

#### Author Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | User ID |
| `userName` | string | Username (handle) |
| `name` | string | Display name |
| `url` | string | Profile URL |
| `description` | string | Profile bio |
| `location` | string | User location |
| `followers` | integer | Follower count |
| `following` | integer | Following count |
| `statusesCount` | integer | Total tweets posted |
| `favouritesCount` | integer | Total likes given |
| `mediaCount` | integer | Total media posts |
| `isBlueVerified` | boolean | Twitter Blue verification status |
| `verifiedType` | string | Verification type (e.g., "government") |
| `createdAt` | string | Account creation date |
| `profilePicture` | string | Profile image URL |
| `coverPicture` | string | Cover image URL |

#### Entities Object

##### Hashtags (`entities.hashtags`)

```json
[{
  "text": "AI",
  "indices": [0, 3]
}]
```

##### URLs (`entities.urls`)

```json
[{
  "url": "https://t.co/...",
  "expanded_url": "https://example.com/full-url",
  "display_url": "example.com/full-url",
  "indices": [10, 33]
}]
```

##### Mentions (`entities.user_mentions`)

```json
[{
  "id_str": "123456",
  "screen_name": "username",
  "name": "Display Name"
}]
```

#### Nested Tweets

| Field | Type | Description |
|-------|------|-------------|
| `quoted_tweet` | object/null | If this is a quote tweet, the quoted tweet |
| `retweeted_tweet` | object/null | If this is a retweet, the original tweet |

## Pagination

Each page returns up to 20 tweets. To fetch more:

1. Check `has_next_page` in the response
2. If true, use `next_cursor` as the `cursor` parameter for the next request
3. Continue until `has_next_page` is false or desired count is reached

## Rate Limits

- The API may have rate limits (check twitterapi.io for current limits)
- Implement exponential backoff for retries if needed
- Consider caching results for repeated queries

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid query parameters) |
| 401 | Unauthorized (invalid API key) |
| 429 | Rate limit exceeded |
| 500 | Server error |

### Common Errors

- Invalid query syntax
- Missing or expired API key
- Network timeout
- Rate limiting

## Best Practices for Analysis

1. **Use `Top` query type** for analyzing trends and popular content
2. **Filter by language** when doing sentiment analysis
3. **Set date ranges** to get relevant, timely data
4. **Use `min_retweets` or `min_faves`** to filter for quality content
5. **Consider engagement metrics** when ranking tweets by importance
6. **Handle multiple languages** in text analysis
7. **Extract hashtags and mentions** for network analysis
8. **Track conversation threads** using `conversationId`

## Data Analysis Tips

### Key Metrics to Track

1. **Engagement rate**: (likes + retweets) / followers
2. **Virality**: retweets and quotes
3. **Discussion depth**: reply count
4. **Reach**: view count
5. **Sentiment**: Analyze text content
6. **Influencer identification**: High follower count + high engagement

### Common Analysis Patterns

1. **Trend detection**: Cluster by hashtags and keywords
2. **Influencer analysis**: Sort by follower count and engagement
3. **Sentiment analysis**: Use NLP on tweet text
4. **Temporal analysis**: Group by `createdAt` timestamps
5. **Network analysis**: Build graph from mentions and replies
6. **Content analysis**: Extract URLs, hashtags, and media
