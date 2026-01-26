"""LLM help documentation for OuraCLI."""

import json
from typing import Any, Literal


def _get_spec_dict() -> dict[str, Any]:
    """Return dashdash-spec v0.2.0 compliant metadata."""
    return {
        "specVersion": "0.2.0",
        "name": "ouracli",
        "version": "0.1.0",
        "description": "CLI tool for accessing Oura Ring health and wellness data from your Oura Ring device.",  # noqa: E501
        "usageContext": (
            "Use when the user needs to retrieve health metrics (sleep, activity, readiness, "
            "heart rate, SpO2, stress, workouts, etc.) from their Oura Ring. "
            "Requires an Oura Personal Access Token."
        ),
        "webUI": "https://cloud.ouraring.com",
        "apiDocs": "https://cloud.ouraring.com/v2/docs",
        "installation": {
            "method": "pip",
            "command": "pip install -e .[dev]",
            "notes": "Clone the repository first, then run `task py:install` or use pip install directly.",  # noqa: E501
        },
        "authentication": {
            "required": True,
            "type": "bearer_token",
            "envVar": "PERSONAL_ACCESS_TOKEN",
            "instructions": (
                "Obtain a token at https://cloud.ouraring.com/personal-access-tokens. "
                "Set via environment variable, secrets/oura.env, or ~/.secrets/oura.env."  # noqa: E501
            ),
        },
        "commands": [
            {
                "name": "activity",
                "description": "Get daily activity data (steps, MET values, calories).",
                "examples": [
                    {
                        "command": "ouracli activity today --json",
                        "description": "Today's activity as JSON",
                    },
                    {"command": 'ouracli activity "7 days" --json', "description": "Last 7 days"},
                    {
                        "command": 'ouracli activity "2025-12-01 28 days" --html > dec.html',
                        "description": "December with charts",
                    },
                ],
                "notes": "Supports --tree, --json, --markdown, --html, --dataframe formats.",  # noqa: E501
            },
            {
                "name": "sleep",
                "description": "Get daily sleep data (stages, efficiency, heart rate during sleep).",  # noqa: E501
                "examples": [
                    {"command": "ouracli sleep today --json", "description": "Today's sleep"},
                    {"command": 'ouracli sleep "30 days" --json', "description": "Last 30 days"},
                ],
            },
            {
                "name": "readiness",
                "description": "Get daily readiness scores and contributors.",
                "examples": [
                    {"command": 'ouracli readiness "7 days" --json', "description": "Last week"}
                ],
                "notes": "contributors.resting_heart_rate is a SCORE (0-100), not BPM.",
            },
            {
                "name": "heartrate",
                "description": "Get time-series heart rate data at 5-minute resolution.",
                "examples": [
                    {
                        "command": "ouracli heartrate today --json",
                        "description": "Today's HR timeseries",
                    },
                    {
                        "command": 'ouracli heartrate "2025-12-15 1 days" --html > hr.html',
                        "description": "Dec 15 chart",
                    },
                ],
            },
            {
                "name": "spo2",
                "description": "Get daily SpO2 (blood oxygen) data.",
                "examples": [
                    {"command": 'ouracli spo2 "7 days" --json', "description": "Last week SpO2"}
                ],
            },
            {
                "name": "stress",
                "description": "Get daily stress data.",
                "examples": [
                    {"command": 'ouracli stress "7 days" --json', "description": "Last week stress"}
                ],
            },
            {
                "name": "workout",
                "description": "Get workout sessions.",
                "examples": [
                    {
                        "command": 'ouracli workout "7 days" --json',
                        "description": "Last week workouts",
                    }
                ],
            },
            {
                "name": "session",
                "description": "Get activity sessions.",
                "examples": [
                    {
                        "command": 'ouracli session "7 days" --json',
                        "description": "Last week sessions",
                    }
                ],
            },
            {
                "name": "tag",
                "description": "Get user-added tags.",
                "examples": [
                    {"command": 'ouracli tag "7 days" --json', "description": "Last week tags"}
                ],
            },
            {
                "name": "rest_mode",
                "description": "Get rest mode periods.",
                "examples": [
                    {
                        "command": 'ouracli rest_mode "7 days" --json',
                        "description": "Last week rest mode",
                    }
                ],
            },
            {
                "name": "personal_info",
                "description": "Get user profile information.",
                "examples": [
                    {"command": "ouracli personal_info --json", "description": "User profile"}
                ],
                "notes": "Does not accept a date range.",
            },
            {
                "name": "all",
                "description": "Get all available data types.",
                "examples": [
                    {
                        "command": 'ouracli all "7 days" --json',
                        "description": "All data, last 7 days",
                    },
                    {
                        "command": 'ouracli all "30 days" --by-day --html > report.html',
                        "description": "Monthly report",
                    },
                ],
                "notes": "Supports --by-day (default) or --by-method grouping.",
            },
        ],
        "dateRanges": {
            "description": "All commands (except personal_info) accept flexible date range arguments.",  # noqa: E501
            "supportedFormats": [
                "today",
                "yesterday",
                "YYYY-MM-DD",
                '"N days"',
                '"N weeks"',
                '"N months"',
                '"YYYY-MM-DD N days"',
            ],
            "unsupportedFormats": [
                "YYYY-MM-DD YYYY-MM-DD (two separate args)",
                '"YYYY-MM-DD to YYYY-MM-DD"',
                '"YYYY-MM-DD..YYYY-MM-DD"',
                "--start-date / --end-date flags",
                '"N months ago"',
            ],
            "notes": (
                "Use quotes when the date range contains spaces. "
                "To query a date range between two specific dates, calculate the number of days and use 'YYYY-MM-DD N days'."  # noqa: E501
            ),
        },
        "outputFormats": {
            "description": "All commands support multiple output formats via flags (only one at a time).",  # noqa: E501
            "formats": [
                {"flag": "--tree", "default": True, "description": "Human-readable tree structure"},
                {
                    "flag": "--json",
                    "default": False,
                    "description": "Raw JSON (recommended for LLMs)",
                },
                {"flag": "--markdown", "default": False, "description": "Markdown formatted"},
                {
                    "flag": "--html",
                    "default": False,
                    "description": "Interactive HTML with Chart.js",
                },
                {"flag": "--dataframe", "default": False, "description": "Pandas DataFrame"},
            ],
            "recommendation": "Always use --json for programmatic analysis and LLM processing.",
        },
        "bestPractices": [
            "Always use --json format for reliable parsing in automated workflows.",
            "Use date ranges (e.g., 'YYYY-MM-DD 2 days') instead of single dates to avoid timezone quirks.",  # noqa: E501
            "In readiness data, contributors.resting_heart_rate is a score (0-100), NOT actual BPM.",  # noqa: E501
            "Redirect HTML/Markdown output to files for viewing: ouracli activity today --html > output.html",  # noqa: E501
            "Check that PERSONAL_ACCESS_TOKEN is set before running commands.",
        ],
        "troubleshooting": [
            {
                "error": "Got unexpected extra argument",
                "cause": "Two separate date arguments instead of one quoted range.",
                "solution": "Use 'YYYY-MM-DD N days' format instead of two dates.",
            },
            {
                "error": "Invalid date specification",
                "cause": "Unsupported syntax like 'to', '..', or relative expressions.",
                "solution": "Use supported formats: 'N days', 'YYYY-MM-DD N days'.",
            },
            {
                "error": "No such option: --start-date",
                "cause": "Flag-based date specification not supported.",
                "solution": "Use positional date range argument.",
            },
            {
                "error": "No data returned",
                "cause": "Ring hasn't synced, date outside range, or timezone issue.",
                "solution": "Try broader date range or add buffer day.",
            },
        ],
        "relatedTools": [
            {
                "name": "Oura Web UI",
                "url": "https://cloud.ouraring.com",
                "description": "Official web interface",
            },
            {
                "name": "Oura API",
                "url": "https://cloud.ouraring.com/v2/docs",
                "description": "REST API docs",
            },
        ],
    }


def _render_markdown(spec: dict[str, Any]) -> str:
    """Render dashdash-spec as markdown with YAML front matter."""
    # YAML front matter
    front_matter = f"""---
name: {spec['name']}
version: {spec['version']}
specVersion: {spec['specVersion']}
usageContext: {spec['usageContext']}
webUI: {spec.get('webUI', '')}
apiDocs: {spec.get('apiDocs', '')}
---
"""
    body = [
        "# OuraCLI Usage Guide for LLMs",
        "",
        "## Overview",
        spec["description"],
        "",
        "## When To Use",
        spec["usageContext"],
        "",
        "## Alternative Access Methods",
        f"- Web UI: {spec.get('webUI', '')}",
        f"- API Docs: {spec.get('apiDocs', '')}",
        "",
        "## Installation",
        f"Method: {spec['installation']['method']}",
        f"Command: `{spec['installation']['command']}`",
        f"Notes: {spec['installation'].get('notes', '')}",
        "",
        "## Authentication",
        f"Required: {spec['authentication']['required']}",
        f"Type: {spec['authentication']['type']}",
        f"Environment Variable: `{spec['authentication']['envVar']}`",
        spec["authentication"]["instructions"],
        "",
        "## Date Range Specification",
        "### Supported",
        "- " + "\n- ".join(spec["dateRanges"]["supportedFormats"]),
        "",
        "### Unsupported (Common LLM Mistakes)",
        "- " + "\n- ".join(spec["dateRanges"]["unsupportedFormats"]),
        "",
        f"Notes: {spec['dateRanges']['notes']}",
        "",
        "## Output Formats",
        "- "
        + "\n- ".join(
            [
                f"{fmt['flag']}{' (default)' if fmt.get('default') else ''} - {fmt['description']}"
                for fmt in spec["outputFormats"]["formats"]
            ]
        ),
        "",
        f"Recommendation: {spec['outputFormats']['recommendation']}",
        "",
        "## Commands",
    ]

    for cmd in spec["commands"]:
        body.extend(
            [
                f"### {cmd['name']}",
                cmd["description"],
            ]
        )
        if cmd.get("notes"):
            body.append(f"Notes: {cmd['notes']}")
        if examples := cmd.get("examples"):
            body.append("Examples")
            body.append("```bash")
            for ex in examples:
                body.append(ex["command"])
            body.append("```")
        body.append("")

    body.extend(
        [
            "## Best Practices",
            "- " + "\n- ".join(spec["bestPractices"]),
            "",
            "## Troubleshooting",
            "- " + "\n- ".join([f"{t['error']}: {t['solution']}" for t in spec["troubleshooting"]]),
            "",
            "## Related Tools",
            "- " + "\n- ".join([f"{t['name']}: {t['url']}" for t in spec["relatedTools"]]),
        ]
    )

    return front_matter + "\n".join(body)


def _render_json(spec: dict[str, Any]) -> str:
    """Render a compact JSON representation for programmatic consumption."""
    return json.dumps(spec, indent=2)


def show_llm_help(format_type: Literal["markdown", "json"] = "markdown") -> str:
    """Return usage guide per dashdash-spec v0.2.0 in the requested format."""
    spec = _get_spec_dict()
    if format_type.lower() == "json":
        return _render_json(spec)
    return _render_markdown(spec)
