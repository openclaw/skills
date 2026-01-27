# Value Tracker Skill

Track and quantify the value your AI assistant generates. Measure hours saved, calculate ROI with differentiated rates by category, and prove the impact.

## Why This Matters

AI assistants save time, but how much? This skill tracks:
- **Hours saved** per task
- **Value generated** with category-specific rates (strategy work ≠ ops work)
- **ROI over time** with daily/weekly/monthly summaries

## Quick Start

```bash
# Log a task manually
./tracker.py log tech "Set up Toast API integration" -H 2

# Auto-detect category from description
./tracker.py log auto "Researched competitor pricing strategies" -H 1.5

# View summaries
./tracker.py summary today
./tracker.py summary week
./tracker.py summary month

# Generate markdown report
./tracker.py report week > weekly-value-report.md

# Export JSON for dashboards
./tracker.py export --format json
```

## Categories & Default Rates

| Category | Default Rate | Use For |
|----------|--------------|---------|
| strategy | $150/hr | Planning, decisions, high-level thinking |
| research | $100/hr | Market research, analysis, deep dives |
| finance | $100/hr | Financial analysis, reporting, forecasting |
| tech | $85/hr | Integrations, automations, scripts |
| sales | $75/hr | CRM, pipeline, outreach |
| marketing | $65/hr | Content, social, campaigns |
| ops | $50/hr | Email triage, scheduling, routine tasks |

Edit `config.json` to customize rates for your context.

## Auto-Detection Keywords

When using `log auto`, the skill detects category from keywords:

- **strategy**: plan, strategy, decision, roadmap, vision
- **research**: research, analyze, competitor, market, study
- **finance**: financial, budget, forecast, revenue, cost
- **tech**: api, integration, script, automation, code, setup
- **sales**: crm, pipeline, deal, lead, prospect, outreach
- **marketing**: content, social, campaign, post, newsletter
- **ops**: email, calendar, schedule, meeting, triage

## Configuration

Edit `config.json`:

```json
{
  "currency": "$",
  "default_rate": 75,
  "rates_by_category": {
    "strategy": 150,
    "research": 100,
    "finance": 100,
    "tech": 85,
    "sales": 75,
    "marketing": 65,
    "ops": 50
  }
}
```

## Data Storage

Tasks are stored in `data.json` in the skill directory. Back it up periodically.

## Integration with Dashboards

Use `tracker.py export` to get JSON output suitable for web dashboards or other tools.

## Tips

1. **Be consistent** — Log tasks as you complete them
2. **Use auto-detect** — Faster than picking categories manually
3. **Review weekly** — The value adds up faster than you think
4. **Customize rates** — Match your actual hourly cost/value

## Example Output

```
📊 Value Summary (This Week)
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hours:  12.5h
Total Value:  $1,087
Avg Rate:     $87/hr

By Category:
  🎯 strategy    2.0h    $300
  🔍 research    3.5h    $350
  ⚙️ tech        4.0h    $340
  🔧 ops         3.0h    $150

Top Tasks:
  • Competitor analysis deep dive (3.5h)
  • Toast API integration (2.0h)
  • Q2 planning session (2.0h)
```

---

*Ship value, track value, prove value.*
