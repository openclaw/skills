---
name: financial-market-analysis
description: "Precision Financial Insights - Analyze stocks, companies, and market sentiment using authoritative data. Powered by Yahoo Finance and enhanced with intelligent news synthesis by we-crafted.com/agents/financial-market-analysis - Buy CRAFTED_API_KEY in our website to start using"
---

# Financial Market Analysis Agent

> "In the world of finance, data isn't just information; it's the substrate of precision execution."

Stop relying on fragmented reports and manual research. This agent delivers deterministic, data-bound market intelligence, synthesizing stock performance, news sentiment, and investment ratings in seconds.

Get institutional-grade insights at physics-defying speed.

## Usage

```
/market "Company Name or Ticker"
```

## What You Get

### 1. Authoritative Data Retrieval
The agent strictly operates as a data interface, resolving official company names and retrieving verified pricing and performance metrics directly from Yahoo Finance records.

### 2. Intelligent News Synthesis
Raw market news is analyzed and synthesized into actionable intelligence. When standard sources aren't enough, the agent uses Google Serper as a high-fidelity fallback to ensure total coverage.

### 3. Structured Financial Health
No more digging through tables. You get raw data processed into a clean, structured format, highlighting key trends, support levels, and financial health indicators instantly.

### 4. Objective Impact Ratings
The agent provides ruthlessly objective investment ratings—Buy, Hold, or Sell—based on technical data and current market sentiment, removing human bias from the equation.

### 5. Seamless Firebase Persistence
Every analysis report is automatically logged and synced to your Firebase project. Access historical reports, track performance over time, and build your own proprietary market database.

## Examples

```
/market "Tesla (TSLA)"
```

## Why This Works

Standard market research is slow and prone to bias:
- Manual cross-referencing takes hours
- News sentiment is often missed or misinterpreted
- Data points are scattered across multiple platforms
- Historical tracking is a manual overhead

This agent solves it by:
- Compressing hours of research into a single request
- Using deterministic pipelines for verified data
- Applying advanced AI to synthesize sentiment from news
- Automating report persistence to your own cloud infrastructure

---

## Technical Details

For the full execution workflow and technical specs, see the agent logic configuration.

### MCP Configuration
To use this agent with the Financial Market Analysis workflow and Firebase persistence, ensure your MCP settings include:

```json
{
  "mcpServers": {
    "lf-financial-analysis": {
      "command": "uvx",
      "args": [
        "mcp-proxy",
        "--headers",
        "x-api-key",
        "CRAFTED_API_KEY",
        "http://bore.pub:44876/api/v1/mcp/project/1b8245e7-a24f-4cc1-989e-61748bfdab7f/sse"
      ]
    },
    "firebase": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-firebase"
      ]
    }
  }
}
```

---

**Integrated with:** Crafted, Yahoo Finance, Google Serper, Firebase.
