---
name: microsoft-ads-mcp
description: Create and manage Microsoft Advertising campaigns (Bing Ads / DuckDuckGo Ads) via MCP server - campaigns, ad groups, keywords, ads, and reporting
metadata: {"clawdbot":{"emoji":"📢","requires":{"commands":["mcporter"]},"homepage":"https://github.com/Duartemartins/microsoft-ads-mcp-server"}}
---

# Microsoft Ads MCP Server

Create and manage Microsoft Advertising campaigns programmatically. This MCP server enables full campaign management for Bing and DuckDuckGo search ads.

## Why Microsoft Advertising?

- **DuckDuckGo Integration** - Microsoft Advertising powers DDG search ads, reaching privacy-conscious users
- **Lower CPCs** - Often 30-50% cheaper than Google Ads
- **Bing + Yahoo + AOL** - Access to the full Microsoft Search Network
- **Import from Google** - Easy migration of existing campaigns

## Setup

### 1. Install the MCP server

```bash
git clone https://github.com/Duartemartins/microsoft-ads-mcp-server.git
cd microsoft-ads-mcp-server
pip install -r requirements.txt
```

### 2. Get credentials

1. **Microsoft Ads Account**: Sign up at [ads.microsoft.com](https://ads.microsoft.com)
2. **Developer Token**: Apply at [developers.ads.microsoft.com](https://developers.ads.microsoft.com)
3. **Azure AD App**: Create at [portal.azure.com](https://portal.azure.com) with redirect URI `https://login.microsoftonline.com/common/oauth2/nativeclient`

### 3. Configure mcporter

Add to `~/.mcporter/mcporter.json`:

```json
{
  "mcpServers": {
    "microsoft-ads": {
      "command": "python3",
      "args": ["/path/to/microsoft-ads-mcp-server/server.py"],
      "type": "stdio",
      "env": {
        "MICROSOFT_ADS_DEVELOPER_TOKEN": "your_token",
        "MICROSOFT_ADS_CLIENT_ID": "your_azure_app_client_id"
      }
    }
  }
}
```

### 4. Authenticate

```bash
mcporter call microsoft-ads.get_auth_url
# Open URL in browser, sign in, copy redirect URL
mcporter call microsoft-ads.complete_auth '{"redirect_url": "https://login.microsoftonline.com/common/oauth2/nativeclient?code=..."}'
```

## Available Tools

### Account Management
```bash
mcporter call microsoft-ads.search_accounts
```

### Campaign Operations
```bash
# List campaigns
mcporter call microsoft-ads.get_campaigns

# Create campaign (starts paused for safety)
mcporter call microsoft-ads.create_campaign '{"name": "My Campaign", "daily_budget": 20}'

# Activate or pause
mcporter call microsoft-ads.update_campaign_status '{"campaign_id": 123456, "status": "Active"}'
```

### Ad Groups
```bash
# List ad groups
mcporter call microsoft-ads.get_ad_groups '{"campaign_id": 123456}'

# Create ad group
mcporter call microsoft-ads.create_ad_group '{"campaign_id": 123456, "name": "Product Keywords", "cpc_bid": 1.50}'
```

### Keywords
```bash
# List keywords
mcporter call microsoft-ads.get_keywords '{"ad_group_id": 789012}'

# Add keywords (Broad, Phrase, or Exact match)
mcporter call microsoft-ads.add_keywords '{"ad_group_id": 789012, "keywords": "buy widgets, widget store", "match_type": "Phrase", "default_bid": 1.25}'
```

### Ads
```bash
# List ads
mcporter call microsoft-ads.get_ads '{"ad_group_id": 789012}'

# Create Responsive Search Ad
mcporter call microsoft-ads.create_responsive_search_ad '{
  "ad_group_id": 789012,
  "final_url": "https://example.com/widgets",
  "headlines": "Buy Widgets Online|Best Widget Store|Free Shipping",
  "descriptions": "Shop our selection. Free shipping over $50.|Quality widgets at great prices."
}'
```

### Reporting
```bash
# Submit report request
mcporter call microsoft-ads.submit_campaign_performance_report '{"date_range": "LastWeek"}'
mcporter call microsoft-ads.submit_keyword_performance_report '{"date_range": "LastMonth"}'
mcporter call microsoft-ads.submit_search_query_report '{"date_range": "LastWeek"}'
mcporter call microsoft-ads.submit_geographic_report '{"date_range": "LastMonth"}'

# Check status and get download URL
mcporter call microsoft-ads.poll_report_status
```

### Other
```bash
mcporter call microsoft-ads.get_budgets
mcporter call microsoft-ads.get_labels
```

## Complete Workflow Example

```bash
# 1. Check account
mcporter call microsoft-ads.search_accounts

# 2. Create campaign
mcporter call microsoft-ads.create_campaign '{"name": "PopaDex - DDG Search", "daily_budget": 15}'
# Returns: Campaign ID 123456

# 3. Create ad group
mcporter call microsoft-ads.create_ad_group '{"campaign_id": 123456, "name": "Privacy Keywords", "cpc_bid": 0.75}'
# Returns: Ad Group ID 789012

# 4. Add keywords
mcporter call microsoft-ads.add_keywords '{
  "ad_group_id": 789012,
  "keywords": "privacy search engine, private browsing, anonymous search",
  "match_type": "Phrase",
  "default_bid": 0.60
}'

# 5. Create ad
mcporter call microsoft-ads.create_responsive_search_ad '{
  "ad_group_id": 789012,
  "final_url": "https://popadex.com",
  "headlines": "PopaDex Private Search|Search Without Tracking|Privacy-First Search Engine",
  "descriptions": "Search the web without being tracked. No ads, no profiling.|Your searches stay private. Try PopaDex today."
}'

# 6. Activate campaign
mcporter call microsoft-ads.update_campaign_status '{"campaign_id": 123456, "status": "Active"}'

# 7. Check performance after a few days
mcporter call microsoft-ads.submit_campaign_performance_report '{"date_range": "LastWeek"}'
mcporter call microsoft-ads.poll_report_status
```

## Match Types

| Type | Syntax | Triggers |
|------|--------|----------|
| Broad | `keyword` | Related searches, synonyms |
| Phrase | `"keyword"` | Contains phrase in order |
| Exact | `[keyword]` | Exact match only |

## Report Columns

**Campaign Reports**: CampaignName, Impressions, Clicks, Ctr, AverageCpc, Spend, Conversions, Revenue

**Keyword Reports**: Keyword, AdGroupName, CampaignName, Impressions, Clicks, Ctr, AverageCpc, Spend, Conversions, QualityScore

**Search Query Reports**: SearchQuery, Keyword, CampaignName, Impressions, Clicks, Spend, Conversions

**Geographic Reports**: Country, State, City, CampaignName, Impressions, Clicks, Spend, Conversions

## Tips

1. **Start paused** - Campaigns are created paused by default. Review before activating.
2. **Use Phrase match** - Good balance between reach and relevance for most keywords.
3. **Multiple headlines** - RSAs need 3-15 headlines (30 chars each) and 2-4 descriptions (90 chars each).
4. **Check search queries** - Review actual search terms to find negative keywords.
5. **Geographic targeting** - Use geo reports to optimize by location.

## Credits

MCP Server: [github.com/Duartemartins/microsoft-ads-mcp-server](https://github.com/Duartemartins/microsoft-ads-mcp-server)

Built with [FastMCP](https://github.com/jlowin/fastmcp) and the [Bing Ads Python SDK](https://github.com/BingAds/BingAds-Python-SDK)
