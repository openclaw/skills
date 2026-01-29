# airfrance-afkl-skill

Clawdbot skill to track **Air France flights** using the **Air France–KLM Open Data APIs** (Flight Status).

It’s designed for day-to-day travel monitoring:
- Flight status + schedule vs latest published times
- Terminal / gate (when published)
- Boarding close time (when available)
- Aircraft tail number + cabin configuration summary (best-effort)
- Previous-flight chain (useful to estimate delay risk)
- Compact alerts: you only get pinged when displayed fields change

## Prerequisites

1) Register and create an API key on the AFKL developer portal:
- https://developer.airfranceklm.com

2) Subscribe to Open Data products (at least **Flight Status API**).

## Configuration

Provide credentials **via environment variables** (recommended):

```bash
export AFKL_API_KEY="..."
# optional
export AFKL_API_SECRET="..."
```

Or via files in your state dir:

- Set `CLAWDBOT_STATE_DIR` to your state directory (or it falls back to `./state`)
- Create:
  - `afkl_api_key.txt`
  - `afkl_api_secret.txt` (optional)

## Usage

### One-off query

```bash
node skills/airfrance-afkl/scripts/afkl_flightstatus_query.mjs \
  --carrier AF --flight 7 --origin JFK --dep-date 2026-01-29
```

### Watcher (poll + change-only output)

```bash
node skills/airfrance-afkl/scripts/afkl_watch_flight.mjs \
  --carrier AF --flight 7 --origin JFK --dep-date 2026-01-29 --prev-depth 2
```

Output behavior:
- **Prints nothing** when nothing changed
- Prints a **ready-to-send multi-line message** when something changed

The message is designed to be compact and human-readable:
- Emojis for 🛫/🕤/🛬/✈️/📶
- Weekday + date + time (to avoid timezone ambiguity)
- Tail + aircraft type + cabin config summary
- Wi‑Fi line (fast/slow) when available
- Previous-flight chain summary (e.g. `↩️ Dubai → Paris → New York (on time)`)
- Optional headline line highlighting what changed (new time, inbound delay, new aircraft, boarding started)


## Rate limits

AFKL Open Data is rate-limited (commonly **1 request/second** and a daily quota).
The watcher is designed to be schedule-aware and to avoid unnecessary calls.

## Notes / disclaimers

- Aircraft “intel” (age, first flight, etc.) is **best-effort** and relies on public sources.
- Cabin configuration identifiers can vary by fleet and may not guarantee the exact seat product.

## License

MIT (recommended) — add a LICENSE file if you want.
