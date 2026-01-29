v6.bvg.transport.rest API — condensed reference

Base: https://v6.bvg.transport.rest/

Useful endpoints
- GET /locations?query=<q>&results=5 — find stops, addresses, POIs
- GET /locations/nearby?latitude=<lat>&longitude=<lon>&results=5&distance=<m> — find nearby stops
- GET /journeys?from=<id or address>&to=<id or address>&arrival=<iso>|&departure=<iso>&results=3&stopovers=true — plan journeys
- GET /journeys/:ref — refresh journey realtime info (useful for delay updates)
- GET /stops/:id/departures?duration=20 — next departures from a stop

Date/time params: accept ISO 8601, human-relative strings, or UNIX timestamps. Prefer Europe/Berlin timezone for parsing.

Examples (with URL encoding)
- Locations (unencoded): `/locations?query=Schönhauser Allee`
  → (encoded): `/locations?query=Sch%C3%B6nhauser%20Allee`
- Journeys: `/journeys?from=900101001&to=900980720&arrival=2026-01-29T17:50:00+01:00&results=3&stopovers=true`
- Refresh: `/journeys/<refreshToken>`

**IMPORTANT: URL Encoding**
All query string values must be URL-encoded before building the request URL:
- Use `urllib.parse.quote()` (Python) or equivalent in your language
- Space → `%20`, `ö` → `%C3%B6`, `ü` → `%C3%BC`, `Ä` → `%C3%84`
- Example: `Sch%C3%B6nhauser Allee` becomes `Sch%C3%B6nhauser%20Allee`

Notes
- No auth required. Rate limit ~100 req/min.
- Use stop IDs when possible for deterministic results.
