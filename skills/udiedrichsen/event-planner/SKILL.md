---
name: event-planner
description: Plan events (night out, weekend, date night, team outing, meals, trips) by searching venues via Google Places API. Auto-selects best restaurants, bars, activities based on location, budget, party size, and preferences. Generates detailed itinerary with timing and Google Maps link. Use when asked to plan an outing, create an itinerary, find places for events, or organize activities.
homepage: https://github.com/clawdbot/clawdbot
metadata: {"clawdbot":{"emoji":"🎉","requires":{"bins":["uv"],"env":["GOOGLE_PLACES_API_KEY"]},"primaryEnv":"GOOGLE_PLACES_API_KEY","install":[{"id":"uv-brew","kind":"brew","formula":"uv","bins":["uv"],"label":"Install uv (brew)"}]}}
---

# Event Planner

Plan events by searching venues and generating itineraries with Google Maps links.

## Quick Start

Plan a night out:

```bash
uv run {baseDir}/scripts/plan_event.py "night out" \
  --location "Times Square, NYC" \
  --party-size 4 \
  --budget medium \
  --duration 4h
```

Plan a weekend day:

```bash
uv run {baseDir}/scripts/plan_event.py "weekend day" \
  --location "Central Park, NYC" \
  --party-size 2 \
  --budget "$100 per person" \
  --preferences "outdoors, casual dining"
```

Plan a date night:

```bash
uv run {baseDir}/scripts/plan_event.py "date night" \
  --location "SoHo, NYC" \
  --budget high \
  --duration 3h
```

## Event Types

- **night-out**: Dinner + 1-2 bars/lounges (3-4 hours)
- **weekend-day**: Brunch/lunch + activity + dinner (6-8 hours)
- **date-night**: Romantic restaurant + dessert/drinks spot (2-3 hours)
- **team-event**: Group activity + dinner venue (3-5 hours)
- **lunch**: Single restaurant recommendation
- **dinner**: Single restaurant recommendation
- **trip**: Multi-day itinerary with daily plans

## Parameters

- `--location`: City, address, or landmark (required)
- `--party-size`: Number of people (default: 2)
- `--budget`: "low/medium/high" or "$X per person" (default: medium)
- `--duration`: Hours available (e.g., "3h", "full day")
- `--preferences`: Comma-separated (e.g., "vegetarian, outdoor seating, live music")
- `--start-time`: When to start (default: inferred from event type)
- `--output`: text|json (default: text)
- `--date`: Target date in YYYY-MM-DD format for day-specific checks (default: today)

## Output Format

**Default (text)**: Markdown itinerary with timeline, venue details, travel info, and Google Maps link

**JSON**: Structured data with all venue details, coordinates, and parsed metadata

## Limitations

- **API limits**: Google Places API has usage quotas (check your billing)
- **Real-time data**: Venue hours may change; always confirm before going
- **Budget estimates**: Based on Google's price level (0-4), not exact costs
- **Travel times**: Uses Google Directions API when available; falls back to distance-based estimates with 30% buffer
- **Opening hours**: Places without verified hours will show warnings; do not assume availability
- **Event venues**: Cultural centers, theaters, and event spaces may have variable hours depending on scheduled events

## API Requirements

The event planner uses:
- **Google Places API (New)**: Required for venue search
- **Google Directions API**: Optional but recommended for accurate travel times

Both APIs can use the same `GOOGLE_PLACES_API_KEY` if enabled in Google Cloud Console.

## Error Handling

- Invalid location → Returns error with suggestions
- No venues found → Relaxes filters and retries
- API failures → Retry with exponential backoff (3 attempts)
