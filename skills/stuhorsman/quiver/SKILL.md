---
name: quiver
description: Query alternative financial data from Quiver Quantitative (Congress trading, Lobbying, Government Contracts, Insider transactions). Use this to track politician stock trades or unconventional market signals.
---

# Quiver Quantitative Skill

Access alternative data sets from Quiver Quantitative to track non-traditional market signals.

## Prerequisites

- **API Token:** You need a Quiver Quantitative API token.
- **Environment:** Set `QUIVER_API_KEY` in your environment or `TOOLS.md`.

## Usage

This skill uses a Python script to fetch data and return it as JSON.

### Congress Trading
Track stock trades by US Senators and Representatives.

```bash
# Recent trades by all members
skills/quiver/scripts/query_quiver.py congress

# Specific Ticker
skills/quiver/scripts/query_quiver.py congress --ticker NVDA

# Specific Politician
skills/quiver/scripts/query_quiver.py congress --politician "Nancy Pelosi"
```

### Corporate Lobbying
Track lobbying spend by companies.

```bash
skills/quiver/scripts/query_quiver.py lobbying AAPL
```

### Government Contracts
Track government contracts awarded to companies.

```bash
skills/quiver/scripts/query_quiver.py contracts LMT
```

### Insider Trading
Track corporate insider transactions.

```bash
skills/quiver/scripts/query_quiver.py insiders TSLA
```

## Output

All commands output a JSON array of records. You can pipe this to `jq` to filter or format it.

```bash
# Get Pelosi's recent NVDA trades
skills/quiver/scripts/query_quiver.py congress --politician "Nancy Pelosi" | jq '.[] | select(.Ticker == "NVDA")'
```
