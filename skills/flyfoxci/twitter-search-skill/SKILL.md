---
name: twitter-search
description: Advanced Twitter search and social media data analysis. Fetches tweets by keywords using Twitter API, processes up to 1000 results, and generates professional data analysis reports with insights and actionable recommendations. Use when user requests Twitter/X social media search, social media trend analysis, tweet data mining, social listening, influencer identification, topic sentiment analysis from tweets, or any task involving gathering and analyzing Twitter data for insights.
---

# Twitter Search and Analysis

## Overview

Search Twitter for keywords using advanced search syntax, fetch up to 1000 relevant tweets, and analyze the data to produce professional reports with insights, statistics, and actionable recommendations.

## Prerequisites

**API Key Required**: Users must configure their Twitter API key from https://twitterapi.io

The API key can be provided in three ways:
1. **Environment variable** (recommended): Set `TWITTER_API_KEY` in your `~/.bashrc` or `~/.zshrc`
   ```bash
   echo 'export TWITTER_API_KEY="your_key_here"' >> ~/.bashrc
   source ~/.bashrc
   ```
2. **As an argument**: Use `--api-key YOUR_KEY` with the wrapper script
3. **Passed directly**: As first argument to the Python script

## Quick Start

### Using the Wrapper Script (Recommended)

The wrapper script automatically handles environment variable loading and dependency checks:

```bash
# Basic search (uses TWITTER_API_KEY from shell config)
./scripts/run_search.sh "AI"

# With custom API key
./scripts/run_search.sh "AI" --api-key YOUR_KEY

# With options
./scripts/run_search.sh "\"Claude AI\"" --max-results 100 --format summary

# Advanced query
./scripts/run_search.sh "from:elonmusk since:2024-01-01" --query-type Latest
```

### Direct Python Script Usage

```bash
# Search for a keyword
scripts/twitter_search.py "$API_KEY" "AI"

# Search with multiple keywords
scripts/twitter_search.py "$API_KEY" "\"ChatGPT\" OR \"Claude AI\""

# Search from specific user
scripts/twitter_search.py "$API_KEY" "from:elonmusk"

# Search with date range
scripts/twitter_search.py "$API_KEY" "Bitcoin since:2024-01-01"
```

### Advanced Queries

```bash
# Complex query: AI tweets from verified users, English only
scripts/twitter_search.py "$API_KEY" "AI OR \"machine learning\" lang:en filter:verified"

# Recent crypto tweets with minimum engagement
scripts/twitter_search.py "$API_KEY" "Bitcoin min_retweets:10 lang:en"

# From specific influencers
scripts/twitter_search.py "$API_KEY" "from:elonmusk OR from:VitalikButerin since:2024-01-01"
```

### Output Format

```bash
# Full JSON with all tweets
scripts/twitter_search.py "$API_KEY" "AI" --format json

# Summary with statistics (default)
scripts/twitter_search.py "$API_KEY" "AI" --format summary
```

### Options

- `--max-results N`: Maximum tweets to fetch (default: 1000)
- `--query-type Latest|Top`: Sort order (default: Top for relevance)
- `--format json|summary`: Output format (default: summary)

## Workflow

### 1. Understand User Requirements

Clarify the analysis goal:
- What topic/keyword to search?
- Date range preference?
- Specific users to include/exclude?
- Language preference?
- Type of insights needed (trends, sentiment, influencers)?

### 2. Build the Search Query

Use [Twitter Advanced Search](https://github.com/igorbrigadir/twitter-advanced-search) syntax:

| Syntax | Example | Description |
|--------|---------|-------------|
| `keyword` | `AI` | Single keyword |
| `"phrase"` | `"machine learning"` | Exact phrase |
| `OR` | `AI OR ChatGPT` | Either term |
| `from:user` | `from:elonmusk` | From specific user |
| `to:user` | `to:elonmusk` | Reply to user |
| `since:DATE` | `since:2024-01-01` | After date |
| `until:DATE` | `until:2024-12-31` | Before date |
| `lang:xx` | `lang:en` | Language code |
| `#hashtag` | `#AI` | Hashtag |
| `filter:links` | `filter:links` | Tweets with links |
| `min_retweets:N` | `min_retweets:100` | Minimum retweets |

### 3. Fetch Data

Execute the search script:

```bash
scripts/twitter_search.py "$API_KEY" "YOUR_QUERY" --max-results 1000 --query-type Top
```

**Important**: Default is 1000 tweets maximum. The script automatically:
- Paginates through all available results
- Stops at 1000 tweets (API limit consideration)
- Handles errors gracefully

### 4. Analyze and Generate Report

After fetching data, produce a comprehensive professional report with:

#### Report Structure

1. **Executive Summary** (2-3 sentences)
   - What was searched
   - Key findings overview

2. **Data Overview**
   - Total tweets analyzed
   - Date range of data
   - Query parameters used

3. **Key Metrics**
   - Total engagement (likes, retweets, replies, quotes, views)
   - Average engagement per tweet
   - Language distribution
   - Reply vs. original tweet ratio

4. **Top Content Analysis**
   - Most retweeted tweets (with **URL links** to original tweets)
   - Most liked tweets (with **URL links** to original tweets)
   - Top hashtags with frequency
   - Most mentioned users
   - Selected tweet examples with full URL references

5. **Influencer Analysis**
   - Top users by follower count
   - Most active users
   - Verified user percentage

6. **Trend Insights** (based on data patterns)
   - Emerging themes
   - Sentiment indicators
   - Temporal patterns
   - Conversation drivers

7. **Key Takeaways**
   - 3-5 bullet points of core insights
   - Data-backed conclusions

8. **Actionable Recommendations**
   - Specific, implementable suggestions
   - Based on the data findings
   - Prioritized by impact

#### Analysis Guidelines

- **Be data-driven**: Every claim should reference actual metrics
- **Provide context**: Explain why metrics matter
- **Identify patterns**: Look for trends across the dataset
- **Stay objective**: Present facts, avoid speculation
- **Be specific**: Recommendations should be concrete and actionable
- **Consider external context**: Use web search for background when relevant

### 5. Output Format

Present the report in clear markdown with:
- Headers for each section
- Tables for structured data
- Bullet points for lists
- Bold for key metrics
- Code blocks for tweet examples
- **Clickable URLs** for all referenced tweets (format: `[@username](https://x.com/username/status/tweet_id)`)

#### Tweet URL Format

Always include clickable links to tweets:
```markdown
| Author | Tweet | URL |
|--------|-------|-----|
| @user | Summary of tweet content | [View](https://x.com/user/status/123456) |
```

Or inline format:
```markdown
- **@username**: Tweet summary - [View Tweet](https://x.com/username/status/123456)
```

## Query Examples by Use Case

### Trend Analysis
```
"AI" OR "artificial intelligence" lang:en min_retweets:50
```

### Competitor Monitoring
```
from:competitor1 OR from:competitor2 since:2024-01-01
```

### Product Launch Tracking
```
#ProductName OR "Product Name" lang:en filter:verified
```

### Crisis Monitoring
```
#BrandName OR "Brand Name" lang:en --query-type Latest
```

### Influencer Discovery
```
#Topic lang:en min_retweets:100 min_faves:500
```

### Sentiment Analysis
```
"brand name" OR #BrandName lang:en --max-results 1000
```

## Resources

### scripts/run_search.sh (Wrapper Script)

Convenience wrapper that handles environment variable loading and dependency checks:
- Automatically loads `TWITTER_API_KEY` from `~/.bashrc` or `~/.zshrc`
- Checks Python availability and installs missing dependencies
- Provides user-friendly error messages
- Supports all command-line options from the Python script

**Usage**:
```bash
./scripts/run_search.sh <query> [options]
```

**Options**:
- `--api-key KEY`: Override environment variable API key
- `--max-results N`: Maximum tweets to fetch (default: 1000)
- `--query-type Latest|Top`: Sort order (default: Top)
- `--format json|summary`: Output format (default: json)

### scripts/twitter_search.py

Executable Python script that:
- Fetches tweets from Twitter API
- Handles pagination automatically
- Extracts key tweet metrics
- Calculates aggregate statistics
- Outputs structured JSON data

**Usage**:
```bash
scripts/twitter_search.py <api_key> <query> [options]
```

### references/twitter_api.md

Comprehensive API documentation including:
- Complete parameter reference
- Query syntax guide
- Response structure details
- Pagination instructions
- Best practices for analysis
- Error handling guide

**Read this when**: Building complex queries or understanding data structure.

## Tips for Better Analysis

1. **Use Top query type** for trend analysis (more relevant results)
2. **Set date filters** for timely insights
3. **Filter by language** for accurate text analysis
4. **Include minimum engagement** to filter noise
5. **Combine with web search** to validate trends
6. **Look beyond metrics** - analyze content themes
7. **Track hashtags** to identify sub-conversations
8. **Identify influencers** by combining followers + engagement

## Error Handling

If the script fails:
- Check API key validity
- Verify query syntax
- Ensure network connectivity
- Check rate limits (if applicable)
- Review error messages for specific issues
