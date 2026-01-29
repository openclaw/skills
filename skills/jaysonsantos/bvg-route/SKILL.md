---
name: bvg-route
description: "Route planning for Berlin public transport (BVG) using the v6.bvg.transport.rest API. Use when the user asks for: (1) route suggestions between two addresses or stops, (2) live next-departure info for a stop, (3) arrival-time–based journey planning (arrive-by or depart-at). Supports outputting 2–3 options ranked by travel time, transfers, and walking, and returning step-by-step directions and refresh tokens for live updates."
---

# BVG Route Planner Skill

Purpose
- Provide concise, actionable public-transport directions in Berlin using the v6.bvg.transport.rest API.

When to use
- User asks for directions between two places in Berlin (addresses, stop names, or coordinates).
- User asks for next departures from a stop/station.
- User requests to arrive by a specific time (arrive-by) or depart at a specific time.

Core behavior
1. Resolve `from` and `to` into either stop IDs (preferred) or address/POI objects using GET /locations or /locations/nearby.
2. Call GET /journeys with arrival or departure parameter as requested, request results=3 and stopovers=true to construct step-by-step legs.
3. Format 2–3 options: show total travel time, number of transfers, walking time, and estimated departure/arrival times.
4. Provide step-by-step instructions for the selected journey: walk to stop A (distance/time), take line X toward Y, get off at stop B (platform if available), final walk to destination.
5. When appropriate, include the journey refreshToken and a GET /journeys/:ref refresh step to update realtime delays.
6. For simple next-departure queries, use GET /stops/:id/departures with duration=20 (or configurable) and return the nearest 3 departures.

Outputs
- Human-readable routes with departure times, transfers, walking distances, estimated arrival, and concise step list.
- Machine-friendly JSON (optional) containing journey id, refreshToken, legs, and stop IDs for programmatic refreshes.

References
- The skill expects to use the v6.bvg.transport.rest API (https://v6.bvg.transport.rest/api.html). See references/API.md for summary and examples.

Examples (triggers)
- "How do I get from Invalidenstraße 43 10115 to Leibnizstraße 62 by public transport?"
- "When is the next U-Bahn from U Rosenthaler Platz?"
- "Find journeys that arrive at Deutsche Oper by 17:50 tonight, fastest option first."

Notes for implementers
- **IBNR format (CRITICAL):** The `/journeys` endpoint requires **base IBNR codes only** (6 digits), not the full ID with `::` suffixes.
  - ❌ Wrong: `de:11000:900110001::3` or `de:11000:900110001`
  - ✅ Correct: `900110001` (extract base 6-digit code from `/stops` results)
  - Process: Call `/stops?query=...` first, extract the 6-digit `id` from results, use that for `/journeys`.
- **URL encoding (CRITICAL):** All query string parameters must be properly URL-encoded using `urllib.parse.quote()` or equivalent. Examples:
  - Space → `%20`
  - `ö` → `%C3%B6`
  - `ü` → `%C3%BC`
  - `Ä` → `%C3%84`
  - Special chars like `&`, `?`, `#` → their percent-encoded equivalents
  - Example: `Schönhauser Allee` → `Sch%C3%B6nhauser%20Allee`
  - Every API call with address/stop name strings in query params must encode before building the URL.
- Prefer stop/station IDs when calling /journeys (more reliable than fuzzy names): Use `/stops?query=...` to resolve names → base IBNR.
- Use `stopovers=true` to build readable step lists; include `entrances=true` when walking-to-entrance accuracy is important.
- Request `results=3` then offer the top 2–3 to the user.
- Handle timezone-aware ISO datetimes; default to Europe/Berlin if none provided.
