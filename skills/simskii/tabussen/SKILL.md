---
name: tabussen
description: Västerbotten & Umeå public transport trip planner (Tabussen/Ultra). Plans bus journeys using ResRobot API. Supports stops, addresses, coordinates, regional and local routes throughout Västerbotten county.
license: MIT
compatibility: Requires curl, jq. Works with Claude Code and compatible agents.
metadata:
  author: simskii
  version: "1.0.0"
  region: sweden-vasterbotten
---

# Tabussen Trip Planner

Plan public transport journeys in Västerbotten, Sweden - including Umeå local traffic (Ultra) and regional routes (Länstrafiken Västerbotten).

## Overview

This skill uses the **ResRobot API** (Trafiklab) to provide journey planning for Tabussen/Ultra. ResRobot is Sweden's national public transport API covering all operators including Länstrafiken Västerbotten.

**Coverage:**
- Ultra (Umeå local bus traffic)
- Länstrafiken Västerbotten (regional buses)
- Connections to/from other Swedish regions
- Train connections where applicable

## Commands

### 1. Search Location

Search for stops, stations, or points of interest.

```bash
./search-location.sh <query> [limit]
```

| Argument | Description |
|----------|-------------|
| `query` | Location name to search for (append `?` for fuzzy search) |
| `limit` | Number of results to show (default: 5, max: 10) |

**Output includes:**
- `ID` - The stop identifier (use this in journey search)
- `Name` - Official name of the stop
- `Coordinates` - Latitude, longitude
- `Weight` - Traffic volume indicator (higher = more traffic)

**Search tips:**
- Use `?` suffix for fuzzy/partial matching: `"Vasaplan?"` 
- Exact search without `?`: `"Vasaplan"`
- Include municipality for precision: `"Umeå Vasaplan"`

### 2. Journey Search

Plan a journey between two locations using their IDs.

```bash
./journey.sh <from-id> <to-id> [datetime] [mode]
```

| Argument | Description |
|----------|-------------|
| `from-id` | Origin stop ID (from search) |
| `to-id` | Destination stop ID |
| `datetime` | Optional: `"18:30"`, `"tomorrow 09:00"`, `"2026-01-28 14:00"` |
| `mode` | Optional: `"depart"` (default) or `"arrive"` |

**Coordinate-based search:**
```bash
./journey.sh "63.825#20.263" <to-id> [datetime] [mode]
```
Use `lat#lon` format for coordinates (WGS84 decimal degrees).

---

## Understanding User Time Intent

Before searching, understand what the user wants:

### Intent Types

| User Says | Intent | How to Query |
|-----------|--------|--------------|
| "now", "next bus", "how do I get to" | **Travel Now** | No datetime parameter |
| "in 30 minutes", "in 1 hour" | **Depart Later** | Calculate time, use `depart` mode |
| "around 15:00", "sometime afternoon" | **Around Time** | Query with offset (see below) |
| "arrive by 18:00", "need to be there at 9" | **Arrive By** | Use `arrive` mode |
| "tomorrow morning", "on Friday at 10" | **Future Time** | Use specific datetime |

### Handling "Around Time" Queries

When user wants options "around" a time, query 15-30 minutes earlier to show options before and after:

```bash
# User: "I want to travel around 15:00"
# Query at 14:30 to get options spanning 14:30-16:00+
./journey.sh ... "14:30" depart
```

### Relative Time Calculations

Convert relative times to absolute:

| User Says | Current: 14:00 | Query Time |
|-----------|----------------|------------|
| "in 30m" | -> | "14:30" |
| "in 1h" | -> | "15:00" |
| "in 2 hours" | -> | "16:00" |

---

## LLM Response Formatting

When presenting journey results to users, use these emojis and formatting guidelines.

### Emoji Reference

| Emoji | Use For |
|-------|---------|
| `bus` | Bus (Tabussen/Ultra) |
| `train` | Train |
| `walk` | Walking segment |
| `clock` | Time/duration |
| `clock1` | Departure time |
| `goal` | Arrival time |
| `pin` | Stop/station |
| `house` | Origin (home/start) |
| `target` | Destination |
| `warning` | Delay or disruption |
| `check` | On time |
| `arrows_counterclockwise` | Transfer/change |

### Response Structure

**Always include these key elements from the tool output:**

1. **When to leave** - The actual time user needs to start (including walking)
2. **Walking segments** - Distance and time for any walking
3. **Transport departure** - When the bus actually leaves
4. **Arrival time** - When user reaches destination
5. **Line number and direction** - Which bus to take

### Example Response Format

**For a simple direct journey:**
```
**Leave now** from Vasaplan

**Vasaplan** -> **Universitetet**
Bus 1 (mot Mariehem) departs 09:07
Arrives 09:18 at Universitetet

Total: 11 min
```

**For a journey with transfer:**
```
**Leave at 08:45**

Walk 300m to Vasaplan (~4 min)

**Vasaplan** -> **Umeå C** -> **Skellefteå**

**Leg 1:**
Bus 1 departs 08:51
Arrives Umeå C 09:05

Transfer at Umeå C (15 min)

**Leg 2:**
Bus 100 (mot Skellefteå) departs 09:20
Arrives Skellefteå busstation 11:45

Total: 3h | 1 change
```

### Walking Segment Details

**Always show walking details:**
- Distance in meters
- Include walking in the "leave time" calculation
- Walk time estimate: ~100m per minute (normal walking speed)

### Presenting Multiple Options

When showing journey options, make timing crystal clear:

```
I found 3 options for you:

**Option 1 - Leave now (09:00)** Recommended
Walk 5 min -> Bus 1 at 09:07 -> arrives 09:25
Total: 25 min

**Option 2 - Leave in 15m (09:15)**
Walk 5 min -> Bus 1 at 09:22 -> arrives 09:40
Total: 25 min

**Option 3 - Leave in 30m (09:30)**
Walk 5 min -> Bus 8 at 09:37 -> arrives 09:48
Total: 18 min | Faster but later departure

Which works best for you?
```

---

## LLM Workflow: How to Plan a Trip

Follow this workflow when a user asks for a trip:

### Step 1: Understand Time Intent

Parse what the user wants:
- **"How do I get to..."** -> Travel now
- **"I need to be there at 18:00"** -> Arrive mode
- **"Sometime around 3pm"** -> Query 14:30, show range
- **"In about an hour"** -> Calculate from current time

### Step 2: Search for Both Locations

Search for origin and destination separately:

```bash
./search-location.sh "Vasaplan?"
./search-location.sh "Universitetet?"
```

### Step 3: Validate Search Results

**Check each result carefully:**

1. **Exact or close match?** - If the name matches what the user asked for, proceed.

2. **Multiple results returned?** - The script shows up to 10 matches. If the first result isn't clearly correct, ask the user to confirm.

3. **Name significantly different?** - If user asked for "university" and result shows "Umeå Universitet", confirm with user.

4. **No results found?** - Try alternative strategies (see below).

### Step 4: Handle Ambiguous or Failed Searches

**When results don't match or are ambiguous, ask clarifying questions:**

```
I searched for "centrum" and found multiple locations:
1. Umeå Vasaplan (central bus hub)
2. Skellefteå centrum
3. Lycksele centrum

Which one did you mean?
```

**When no results are found, try these strategies:**

1. **Try with city name:**
   ```bash
   # If "Storgatan 10" fails, try:
   ./search-location.sh "Storgatan 10, Umeå?"
   ```

2. **Try common variations:**
   ```bash
   # "Universitetet" -> "Umeå universitet"
   # "Sjukhuset" -> "NUS" or "Norrlands universitetssjukhus"
   ```

3. **Use fuzzy search (add ?):**
   ```bash
   ./search-location.sh "univ?"
   ```

### Step 5: Execute Journey Search

Once you have confirmed IDs for both locations:

```bash
./journey.sh <from-id> <to-id> [datetime] [mode]
```

### Step 6: Format Response

Use the formatting guide above to present results clearly. **Always use actual numbers from the tool output - never estimate or speculate.**

---

## Query Formatting Rules

**The search API is sensitive to formatting. Follow these rules:**

### Common Stop Names in Umeå

| User Says | Search For |
|-----------|------------|
| "Vasaplan", "centrum" | `"Umeå Vasaplan?"` |
| "Universitetet", "uni" | `"Umeå universitet?"` |
| "NUS", "sjukhuset" | `"Norrlands universitetssjukhus?"` |
| "Ikea" | `"IKEA Umeå?"` |
| "Flygplatsen" | `"Umeå Airport?"` |
| "Järnvägsstationen", "tåget" | `"Umeå centralstation?"` |

### Regional Destinations

| Destination | Search For |
|-------------|------------|
| Skellefteå | `"Skellefteå busstation?"` |
| Lycksele | `"Lycksele busstation?"` |
| Vindeln | `"Vindeln station?"` |
| Robertsfors | `"Robertsfors centrum?"` |
| Holmsund | `"Holmsund centrum?"` |

### Street Addresses

Include city name for better accuracy:
```bash
./search-location.sh "Storgatan 25, Umeå?"
./search-location.sh "Kungsgatan 10, Skellefteå?"
```

---

## Examples

### Example 1: Travel Now (Umeå Local)

User: "How do I get from Vasaplan to NUS?"

```bash
./search-location.sh "Umeå Vasaplan"
./search-location.sh "NUS?"
./journey.sh 740020116 740023840
```

**Response:**
```
**Leave now** from Vasaplan

**Vasaplan** -> **Universitetssjukhuset**
Bus 8 (mot Lyktvägen) departs 11:01
Arrives 11:06

Total: 5 min | Direct, no changes
```

### Example 2: Regional Journey

User: "I need to get to Skellefteå from Umeå tomorrow at 8"

```bash
./search-location.sh "Umeå Vasaplan"
./search-location.sh "Skellefteå?"
./journey.sh 740020116 740000053 "tomorrow 08:00"
```

**Response:**
```
**Depart tomorrow at 08:04** from Vasaplan

Walk 766m to Umeå Busstation (~11 min)

**Umeå Busstation** -> **Skellefteå busstation**
Bus 20 (Länstrafik mot Haparanda) departs 08:15
Arrives 10:40 at Skellefteå busstation

Total: 2h 36min | Direct (with walk)
```

### Example 3: Arrive By Time

User: "I need to be at NUS by 08:00 tomorrow"

```bash
./search-location.sh "Umeå Vasaplan"
./search-location.sh "NUS?"
./journey.sh 740020116 740023840 "tomorrow 08:00" arrive
```

**Response:**
```
**Arrive by 08:00** at NUS

**Vasaplan** -> **Universitetssjukhuset**
Bus 9 departs **07:51**
Arrives **07:56** - 4 min buffer

Leave Vasaplan by 07:51 to arrive on time!
```

### Example 4: From Address/Coordinates

User: "I'm at Storgatan 50 in Umeå, how do I get to IKEA?"

```bash
./search-location.sh "Storgatan 50, Umeå?"
# If no result, use coordinates
./journey.sh "63.826#20.263" 740066123
```

---

## DateTime Formats

All times are Swedish local time (CET/CEST).

| Format | Example | Meaning |
|--------|---------|---------|
| _(empty)_ | | Travel now |
| `HH:MM` | `"08:30"` | Today at 08:30 |
| `tomorrow HH:MM` | `"tomorrow 09:00"` | Tomorrow at 09:00 |
| `YYYY-MM-DD HH:MM` | `"2026-01-28 14:00"` | Specific date |

---

## Output Format

### Journey Option (Raw Tool Output)

```
==============================================================
OPTION 1: Vasaplan -> Universitetet
==============================================================
Date:    2026-01-28
Depart:  09:04
Arrive:  09:12
Changes: 0

LEGS:
  -> BUS Länstrafik - Buss 1
    From: 09:04 Vasaplan (Umeå kn)
    To:   09:12 Universitetet (Umeå kn)
    Direction: mot Mariehem
```

### Transport Types

| Type | Description |
|------|-------------|
| `BUS` | Tabussen/Ultra/Länstrafik bus |
| `JLT` | Regional bus (Länstrafik) |
| `JRE` | Regional train |
| `WALK` | Walking segment |

### Operators in Västerbotten

| Operator | Description |
|----------|-------------|
| Länstrafiken Västerbotten | Regional and local buses |
| Ultra | Umeå local traffic (part of Länstrafiken) |
| SJ | Long-distance trains |
| Norrtåg | Regional trains |

---

## Error Handling

### "No locations found"

The search returned no results.

**Strategies:**
1. Check spelling (Swedish: å, ä, ö)
2. Try with city name suffix
3. Use fuzzy search (add ?)
4. Try common alternative names
5. Ask user for clarification

### "No journeys found"

No routes available.

**Strategies:**
1. Check if service operates at that hour (late night limited)
2. Try different departure time
3. Suggest alternative nearby stops
4. Note that some regional routes have limited frequency

### Common Issues

| Issue | Solution |
|-------|----------|
| "Vasaplan" returns multiple | Use "Umeå Vasaplan" |
| Stop not found | Try fuzzy search with ? |
| No late-night routes | Ultra has limited night service |
| Long wait times | Regional routes may be hourly |

---

## Quick Reference

### Popular Umeå Stops (Ultra)

| Stop | ID | Notes |
|------|-----|-------|
| Vasaplan | 740020116 | Central hub |
| Universitetssjukhuset (NUS) | 740023840 | Hospital |
| Universum | 740026881 | University area |
| Umeå Busstation | - | Regional bus departures |
| Västerslätt Centrum | 740045407 | Western suburb |

### Key Regional Stops

| Stop | ID | Notes |
|------|-----|-------|
| Skellefteå busstation | 740000053 | Regional hub |
| Lycksele busstation | - | Inland hub |
| Vindeln station | - | Train connection |
| Robertsfors centrum | - | Coastal route |

---

## API Details (For Script Development)

This skill uses ResRobot API v2.1 from Trafiklab.

**Base URL:** `https://api.resrobot.se/v2.1/`

**Endpoints:**
- Stop lookup: `/location.name`
- Journey planner: `/trip`

**Key Parameters:**
- `accessId` - API key (required)
- `format` - json or xml
- `originId` / `destId` - Stop IDs
- `date` / `time` - Travel date/time
- `searchForArrival` - 1 for arrive-by searches

**Get API Key:** Register at https://developer.trafiklab.se

---

## Notes on Västerbotten Traffic

### Ultra (Umeå Local)
- Frequent service in central Umeå
- Lines 1-9 are most common
- Night buses (N-lines) on weekends
- Real-time info available in app

### Länstrafiken (Regional)
- Line 100: Umeå - Skellefteå (frequent)
- Line 12/20: Coastal routes
- Lines 30-49: Inland routes
- Frequency varies by route

### Tips for Users
- Vasaplan is the main hub for both Ultra and regional
- Many regional buses depart from Vasaplan, not train station
- Train station (Umeå C) is separate from bus station
- IKEA and Avion have good bus connections

---

## When to Ask Clarifying Questions

**Always ask when:**

1. **Search returns no results:**
   - "I couldn't find [location]. Could you provide more details?"

2. **Multiple plausible matches:**
   - "I found several stops matching '[query]': [list]. Which one?"

3. **Result name very different from query:**
   - "You asked for '[user query]' but I found '[result name]'. Is this correct?"

4. **User request is vague:**
   - "From where in Umeå? Vasaplan (central), or another location?"

5. **Time is unclear:**
   - "When do you want to travel? Now, or at a specific time?"
