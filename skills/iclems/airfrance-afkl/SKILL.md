---
name: airfrance-afkl
description: Track Air France flights using the Air France–KLM Open Data APIs (Flight Status). Use when the user gives a flight number/date (e.g., AF007 on 2026-01-29) and wants monitoring, alerts (delay/gate/aircraft changes), or analysis (previous-flight chain, aircraft tail number → cabin recency / Wi‑Fi). Also use when setting up or tuning polling schedules within API rate limits.
---

# Air France (AFKL Open Data) flight tracker

## Quick start (one-off status)

1) Create an API key (and optional secret)
- Register on: https://developer.airfranceklm.com
- Subscribe to the Open Data product(s) you need (at least **Flight Status API**)
- Generate credentials (API key; some accounts also provide an API secret)

2) Provide API credentials (do not print them):
- Preferred: env vars `AFKL_API_KEY` (and optional `AFKL_API_SECRET`)
- Or files in your state dir (`CLAWDBOT_STATE_DIR` or `./state`):
  - `afkl_api_key.txt` (chmod 600)
  - `afkl_api_secret.txt` (chmod 600, optional)

2) Query flight status:
- Run: `node skills/airfrance-afkl/scripts/afkl_flightstatus_query.mjs --carrier AF --flight 7 --origin JFK --dep-date 2026-01-29`

Notes:
- Send `Accept: */*` (API returns `application/hal+json`).
- Keep within limits: **<= 1 request/sec**. When making multiple calls, sleep ~1100ms between them.

## Start monitoring (watcher)

Use when the user wants proactive updates.

- Run: `node skills/airfrance-afkl/scripts/afkl_watch_flight.mjs --carrier AF --flight 7 --origin JFK --dep-date 2026-01-29`

What it does:
- Fetches the operational flight(s) for the date window.
- Emits a single message only when something meaningful changes.
- Also follows the **previous-flight chain** (`flightRelations.previousFlightData.id`) up to a configurable depth and alerts if a previous segment is delayed/cancelled.

Polling strategy (default):
- >36h before departure: at most every **60 min**
- 36h→12h: every **30 min**
- 12h→3h: every **15 min**
- 3h→departure: every **5–10 min** (stay under daily quota)
- After departure: every **30 min** until arrival

Implementation detail: run cron every 5–15 min, but the script self-throttles using a state file so it won’t hit the API when it’s not time. The watcher prints **no output** when nothing changed (so cron jobs can send only when stdout is non-empty).

## Input shorthand

Preferred user-facing format:
- `AF7 demain` / `AF7 jeudi`

Interpretation rule:
- The day always refers to the **departure date** (not arrival).

Implementation notes:
- Convert relative day words to a departure date in the user’s timezone unless the origin timezone is explicitly known.
- When ambiguous (long-haul crossing midnight), prefer the departure local date at the origin if origin is known.

(For scripts, still pass `--origin` + `--dep-date YYYY-MM-DD`.)

## Interpret “interesting” fields

See `references/fields.md` for:
- `flightRelations` (prev/next)
- `places.*` (terminal/gate/check-in zone)
- `times.*` (scheduled/estimated/latest/actual)
- `aircraft` (type, registration)
- “parking position” / stand-type hints (when present)
- Wi‑Fi hints and how to reason about cabin recency

## Cabin recency / upgrade heuristics

When aircraft registration is available:
- Use tail number to infer **sub-fleet** and likely cabin generation.
- If data suggests older config (or no Wi‑Fi), upgrading can be more/less worth it.

Be conservative:
- Open Data often doesn’t expose exact seat model; treat this as **best-effort**.
