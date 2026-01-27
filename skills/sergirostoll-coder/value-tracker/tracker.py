#!/usr/bin/env python3
"""
Value Tracker - Quantify the value your AI assistant generates.
Track hours saved with differentiated rates by category.
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

SKILL_DIR = Path(__file__).parent
DATA_FILE = SKILL_DIR / "data.json"
CONFIG_FILE = SKILL_DIR / "config.json"

# Auto-detection keywords
CATEGORY_KEYWORDS = {
    "strategy": ["plan", "strategy", "decision", "roadmap", "vision", "strategic", "priority", "goal"],
    "research": ["research", "analyze", "analysis", "competitor", "market", "study", "investigate", "deep dive"],
    "finance": ["financial", "budget", "forecast", "revenue", "cost", "profit", "expense", "accounting"],
    "tech": ["api", "integration", "script", "automation", "code", "setup", "deploy", "technical", "debug", "install"],
    "sales": ["crm", "pipeline", "deal", "lead", "prospect", "outreach", "sales", "client", "customer"],
    "marketing": ["content", "social", "campaign", "post", "newsletter", "brand", "marketing", "seo", "ads"],
    "ops": ["email", "calendar", "schedule", "meeting", "triage", "organize", "admin", "routine", "check"]
}

CATEGORY_ICONS = {
    "strategy": "🎯", "research": "🔍", "finance": "💹",
    "tech": "⚙️", "sales": "📈", "marketing": "📣",
    "ops": "🔧", "other": "📦"
}

def load_config():
    """Load configuration with defaults."""
    defaults = {
        "currency": "$",
        "default_rate": 75,
        "rates_by_category": {
            "strategy": 150, "research": 100, "finance": 100,
            "tech": 85, "sales": 75, "marketing": 65, "ops": 50
        }
    }
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            user_config = json.load(f)
            defaults.update(user_config)
    else:
        # Create default config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(defaults, f, indent=2)
    
    return defaults

def load_data():
    """Load existing data."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"entries": []}

def save_data(data):
    """Save data to file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def detect_category(description):
    """Auto-detect category from description keywords."""
    desc_lower = description.lower()
    
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > 0:
            scores[category] = score
    
    if scores:
        return max(scores, key=scores.get)
    return "other"

def get_rate(category, config):
    """Get hourly rate for category."""
    return config.get("rates_by_category", {}).get(category, config.get("default_rate", 75))

def log_task(args, config):
    """Log a new task."""
    data = load_data()
    
    category = args.category
    if category == "auto":
        category = detect_category(args.description)
        print(f"📌 Auto-detected category: {category}")
    
    rate = get_rate(category, config)
    value = args.hours * rate
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": category,
        "description": args.description,
        "hours": args.hours,
        "rate": rate,
        "value": value
    }
    
    if args.notes:
        entry["notes"] = args.notes
    
    data["entries"].append(entry)
    save_data(data)
    
    currency = config.get("currency", "$")
    print(f"✅ Logged: {args.description}")
    print(f"   {CATEGORY_ICONS.get(category, '📦')} {category} | {args.hours}h | {currency}{value:.0f}")

def get_date_range(period):
    """Get date range for period."""
    today = datetime.now().date()
    
    if period == "today":
        return today, today
    elif period == "week":
        start = today - timedelta(days=today.weekday())
        return start, today
    elif period == "month":
        start = today.replace(day=1)
        return start, today
    else:  # all
        return None, None

def filter_entries(entries, period):
    """Filter entries by period."""
    start, end = get_date_range(period)
    
    if start is None:
        return entries
    
    filtered = []
    for e in entries:
        entry_date = datetime.fromisoformat(e["timestamp"]).date()
        if start <= entry_date <= end:
            filtered.append(e)
    
    return filtered

def summary(args, config):
    """Show summary for period."""
    data = load_data()
    entries = filter_entries(data.get("entries", []), args.period)
    
    if not entries:
        print(f"📊 No entries for {args.period}")
        return
    
    currency = config.get("currency", "$")
    
    # Calculate totals
    total_hours = sum(e.get("hours", 0) for e in entries)
    total_value = sum(e.get("value", e.get("hours", 0) * get_rate(e.get("category", "other"), config)) for e in entries)
    avg_rate = total_value / total_hours if total_hours > 0 else 0
    
    # By category
    by_cat = {}
    for e in entries:
        cat = e.get("category", "other")
        if cat not in by_cat:
            by_cat[cat] = {"hours": 0, "value": 0}
        by_cat[cat]["hours"] += e.get("hours", 0)
        by_cat[cat]["value"] += e.get("value", e.get("hours", 0) * get_rate(cat, config))
    
    # Sort by value
    sorted_cats = sorted(by_cat.items(), key=lambda x: x[1]["value"], reverse=True)
    
    # Top tasks
    sorted_entries = sorted(entries, key=lambda x: x.get("hours", 0), reverse=True)[:5]
    
    # Print summary
    period_label = {"today": "Today", "week": "This Week", "month": "This Month", "all": "All Time"}
    
    print(f"\n📊 Value Summary ({period_label.get(args.period, args.period)})")
    print("━" * 40)
    print(f"\nTotal Hours:  {total_hours:.1f}h")
    print(f"Total Value:  {currency}{total_value:,.0f}")
    print(f"Avg Rate:     {currency}{avg_rate:.0f}/hr")
    
    print(f"\nBy Category:")
    for cat, data in sorted_cats:
        icon = CATEGORY_ICONS.get(cat, "📦")
        print(f"  {icon} {cat:<12} {data['hours']:>5.1f}h    {currency}{data['value']:>6,.0f}")
    
    if sorted_entries:
        print(f"\nTop Tasks:")
        for e in sorted_entries:
            desc = e.get("description", e.get("notes", ""))[:40]
            print(f"  • {desc} ({e.get('hours', 0):.1f}h)")
    
    print()

def report(args, config):
    """Generate markdown report."""
    data = load_data()
    entries = filter_entries(data.get("entries", []), args.period)
    
    if not entries:
        print(f"# Value Report\n\nNo entries for {args.period}")
        return
    
    currency = config.get("currency", "$")
    
    # Calculate totals
    total_hours = sum(e.get("hours", 0) for e in entries)
    total_value = sum(e.get("value", e.get("hours", 0) * get_rate(e.get("category", "other"), config)) for e in entries)
    avg_rate = total_value / total_hours if total_hours > 0 else 0
    
    # By category
    by_cat = {}
    for e in entries:
        cat = e.get("category", "other")
        if cat not in by_cat:
            by_cat[cat] = {"hours": 0, "value": 0, "tasks": []}
        by_cat[cat]["hours"] += e.get("hours", 0)
        by_cat[cat]["value"] += e.get("value", e.get("hours", 0) * get_rate(cat, config))
        by_cat[cat]["tasks"].append(e)
    
    sorted_cats = sorted(by_cat.items(), key=lambda x: x[1]["value"], reverse=True)
    
    period_label = {"today": "Today", "week": "This Week", "month": "This Month", "all": "All Time"}
    
    print(f"# 💰 Value Report — {period_label.get(args.period, args.period)}")
    print(f"\n*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    
    print("## Summary\n")
    print(f"| Metric | Value |")
    print(f"|--------|-------|")
    print(f"| **Total Hours** | {total_hours:.1f}h |")
    print(f"| **Total Value** | {currency}{total_value:,.0f} |")
    print(f"| **Avg Rate** | {currency}{avg_rate:.0f}/hr |")
    print(f"| **Tasks Completed** | {len(entries)} |")
    
    print("\n## By Category\n")
    print("| Category | Hours | Value | % |")
    print("|----------|-------|-------|---|")
    for cat, cdata in sorted_cats:
        icon = CATEGORY_ICONS.get(cat, "📦")
        pct = (cdata["value"] / total_value * 100) if total_value > 0 else 0
        print(f"| {icon} {cat.title()} | {cdata['hours']:.1f}h | {currency}{cdata['value']:,.0f} | {pct:.0f}% |")
    
    print("\n## Task Log\n")
    for e in sorted(entries, key=lambda x: x.get("timestamp", ""), reverse=True)[:20]:
        icon = CATEGORY_ICONS.get(e.get("category", "other"), "📦")
        desc = e.get("description", e.get("notes", ""))
        print(f"- {icon} **{desc}** — {e.get('hours', 0):.1f}h ({currency}{e.get('value', 0):.0f})")
    
    print("\n---\n*Tracked with Value Tracker*")

def export_data(args, config):
    """Export data as JSON."""
    data = load_data()
    entries = filter_entries(data.get("entries", []), args.period) if args.period else data.get("entries", [])
    
    currency = config.get("currency", "$")
    total_hours = sum(e.get("hours", 0) for e in entries)
    total_value = sum(e.get("value", e.get("hours", 0) * get_rate(e.get("category", "other"), config)) for e in entries)
    
    # By category
    by_cat = {}
    for e in entries:
        cat = e.get("category", "other")
        if cat not in by_cat:
            by_cat[cat] = {"hours": 0, "value": 0, "count": 0}
        by_cat[cat]["hours"] += e.get("hours", 0)
        by_cat[cat]["value"] += e.get("value", e.get("hours", 0) * get_rate(cat, config))
        by_cat[cat]["count"] += 1
    
    output = {
        "summary": {
            "total_hours": round(total_hours, 1),
            "total_value": round(total_value, 0),
            "avg_rate": round(total_value / total_hours, 0) if total_hours > 0 else 0,
            "task_count": len(entries),
            "currency": currency
        },
        "by_category": by_cat,
        "entries": entries if args.include_entries else None
    }
    
    if not args.include_entries:
        del output["entries"]
    
    print(json.dumps(output, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Track value generated by AI assistant")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log a task")
    log_parser.add_argument("category", help="Category (strategy/research/finance/tech/sales/marketing/ops/auto)")
    log_parser.add_argument("description", help="Task description")
    log_parser.add_argument("--hours", "-H", type=float, required=True, help="Hours spent")
    log_parser.add_argument("--notes", "-n", help="Additional notes")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show summary")
    summary_parser.add_argument("period", nargs="?", default="week", help="Period: today/week/month/all")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate markdown report")
    report_parser.add_argument("period", nargs="?", default="week", help="Period: today/week/month/all")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export JSON data")
    export_parser.add_argument("--period", "-p", help="Period filter: today/week/month")
    export_parser.add_argument("--include-entries", "-e", action="store_true", help="Include individual entries")
    
    args = parser.parse_args()
    config = load_config()
    
    if args.command == "log":
        log_task(args, config)
    elif args.command == "summary":
        summary(args, config)
    elif args.command == "report":
        report(args, config)
    elif args.command == "export":
        export_data(args, config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
