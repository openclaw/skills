#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///
"""
Event planner using Google Places API.

Usage:
    uv run plan_event.py EVENT_TYPE --location LOCATION [OPTIONS]
"""

import argparse
import json
import math
import os
import re
import sys
import time
import urllib.parse
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Literal

import requests


# Data structures
@dataclass
class Coordinates:
    lat: float
    lng: float
    address: str


@dataclass
class Venue:
    name: str
    address: str
    location: Coordinates
    rating: float
    price_level: int
    place_id: str
    types: list[str]
    open_now: bool | None  # None means unknown
    hours_known: bool
    user_ratings_total: int


@dataclass
class BudgetConstraints:
    min_price_level: int
    max_price_level: int
    total_estimate: float | None


@dataclass
class ItineraryItem:
    venue: Venue
    arrival_time: str
    duration_minutes: int
    departure_time: str
    travel_from_previous_minutes: int
    travel_distance_km: float = 0.0  # Walking distance in km
    travel_time_source: str = ""  # 'directions_api' or 'estimated'


@dataclass
class Itinerary:
    event_type: str
    location: str
    party_size: int
    budget: str
    items: list[ItineraryItem]
    total_duration_hours: float
    total_cost_estimate: str
    map_link: str
    preferences_applied: list[str]
    warnings: list[str]


# Event templates
EVENT_TEMPLATES = {
    "night-out": [
        {"type": "restaurant", "query": "dinner restaurant", "duration": 90, "filters": {"min_rating": 4.0}},
        {"type": "bar", "query": "cocktail bar", "duration": 60, "filters": {"min_rating": 4.0}},
    ],
    "weekend-day": [
        {"type": "restaurant", "query": "brunch", "duration": 90, "filters": {"min_rating": 4.0}},
        {"type": "activity", "query": "museum", "duration": 180, "filters": {}},
        {"type": "restaurant", "query": "dinner restaurant", "duration": 90, "filters": {"min_rating": 4.0}},
    ],
    "date-night": [
        {"type": "restaurant", "query": "romantic restaurant", "duration": 120, "filters": {"min_rating": 4.2}},
        {"type": "dessert", "query": "dessert cafe", "duration": 45, "filters": {"min_rating": 4.0}},
    ],
    "team-event": [
        {"type": "activity", "query": "bowling", "duration": 120, "filters": {}},
        {"type": "restaurant", "query": "restaurant", "duration": 90, "filters": {"min_rating": 4.0}},
    ],
    "lunch": [
        {"type": "restaurant", "query": "lunch restaurant", "duration": 60, "filters": {"min_rating": 4.0}},
    ],
    "dinner": [
        {"type": "restaurant", "query": "dinner restaurant", "duration": 90, "filters": {"min_rating": 4.0}},
    ],
}

# Venue types with variable hours or event-dependent operation
EVENT_DEPENDENT_TYPES = {
    "cultural_center",
    "performing_arts_theater",
    "event_venue",
    "community_center",
    "concert_hall",
    "theater",
    "night_club",
    "movie_theater",
    "amusement_park",
}

# Google Places API configuration
BASE_URL = "https://places.googleapis.com/v1"
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")


def parse_budget(budget_str: str, party_size: int) -> BudgetConstraints:
    """Parse budget string into price level constraints."""
    # Check for dollar amount
    dollar_match = re.match(r'\$?(\d+(?:\.\d+)?)\s*(?:per\s+person)?', budget_str.lower())
    if dollar_match:
        amount = float(dollar_match.group(1))
        total = amount * party_size

        # Map to Google price levels (0-4)
        # Rough mapping: 0-20: level 1, 20-40: level 2, 40-60: level 3, 60+: level 4
        if amount < 20:
            return BudgetConstraints(1, 2, total)
        elif amount < 40:
            return BudgetConstraints(2, 3, total)
        elif amount < 60:
            return BudgetConstraints(3, 4, total)
        else:
            return BudgetConstraints(3, 4, total)

    # Text levels
    budget_lower = budget_str.lower()
    if budget_lower == "low":
        return BudgetConstraints(1, 2, None)
    elif budget_lower == "medium":
        return BudgetConstraints(2, 3, None)
    elif budget_lower == "high":
        return BudgetConstraints(3, 4, None)
    else:
        # Default to medium
        return BudgetConstraints(2, 3, None)


def call_places_api(endpoint: str, body: dict, retry_count: int = 3) -> dict:
    """Call Google Places API with retry logic."""
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.rating,places.priceLevel,places.id,places.types,places.currentOpeningHours,places.userRatingCount"
    }

    url = f"{BASE_URL}/{endpoint}"

    for attempt in range(retry_count):
        try:
            response = requests.post(url, json=body, headers=headers, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt
                    print(f"Rate limit hit, waiting {wait_time}s...", file=sys.stderr)
                    time.sleep(wait_time)
                    continue
            else:
                print(f"API error: {response.status_code} - {response.text}", file=sys.stderr)
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {}

        except Exception as e:
            if attempt < retry_count - 1:
                print(f"Request failed: {e}, retrying...", file=sys.stderr)
                time.sleep(2 ** attempt)
            else:
                print(f"Request failed after {retry_count} attempts: {e}", file=sys.stderr)
                return {}

    return {}


def resolve_location(location: str) -> Coordinates | None:
    """Resolve location string to coordinates."""
    body = {
        "textQuery": location
    }

    result = call_places_api("places:searchText", body)

    if not result or "places" not in result or not result["places"]:
        return None

    place = result["places"][0]

    if "location" not in place:
        return None

    loc = place["location"]
    address = place.get("formattedAddress", location)

    return Coordinates(
        lat=loc["latitude"],
        lng=loc["longitude"],
        address=address
    )


def search_venues_with_fallback(query: str, location: Coordinates, filters: dict) -> list[Venue]:
    """Search with expanding radius if too few results."""
    venues = search_venues(query, location, filters, radius=5000)

    if len(venues) < 3:
        # Try larger radius
        venues = search_venues(query, location, filters, radius=10000)

    if len(venues) < 3:
        # Try without min_rating filter
        relaxed = {k: v for k, v in filters.items() if k != "min_rating"}
        venues = search_venues(query, location, relaxed, radius=10000)

    return venues


def search_venues(query: str, location: Coordinates, filters: dict, radius: int = 5000) -> list[Venue]:
    """Search for venues near a location."""
    body = {
        "textQuery": f"{query} near {location.address}",
        "locationBias": {
            "circle": {
                "center": {"latitude": location.lat, "longitude": location.lng},
                "radius": radius
            }
        },
        "maxResultCount": 20
    }

    result = call_places_api("places:searchText", body)

    if not result or "places" not in result:
        return []

    venues = []
    for place in result.get("places", []):
        if "location" not in place:
            continue

        # Extract data
        name = place.get("displayName", {}).get("text", "Unknown")
        address = place.get("formattedAddress", "")
        loc = place["location"]
        rating = place.get("rating", 0.0)
        price_level = place.get("priceLevel", "PRICE_LEVEL_UNSPECIFIED")
        place_id = place.get("id", "")
        types = place.get("types", [])
        user_rating_count = place.get("userRatingCount", 0)

        # Convert price level string to int
        price_map = {
            "PRICE_LEVEL_FREE": 0,
            "PRICE_LEVEL_INEXPENSIVE": 1,
            "PRICE_LEVEL_MODERATE": 2,
            "PRICE_LEVEL_EXPENSIVE": 3,
            "PRICE_LEVEL_VERY_EXPENSIVE": 4,
            "PRICE_LEVEL_UNSPECIFIED": 2,  # Default to medium
        }
        price_int = price_map.get(price_level, 2)

        # Check open status - don't assume open if unknown
        current_hours = place.get("currentOpeningHours")
        if current_hours is not None:
            open_now = current_hours.get("openNow")  # May still be None if not present
            hours_known = True
        else:
            open_now = None
            hours_known = False

        # Apply filters
        min_rating = filters.get("min_rating", 0.0)
        if rating < min_rating:
            continue

        venue = Venue(
            name=name,
            address=address,
            location=Coordinates(loc["latitude"], loc["longitude"], address),
            rating=rating,
            price_level=price_int,
            place_id=place_id,
            types=types,
            open_now=open_now,
            hours_known=hours_known,
            user_ratings_total=user_rating_count
        )
        venues.append(venue)

    return venues


def calculate_distance(coord1: Coordinates, coord2: Coordinates) -> float:
    """Calculate distance in miles using Haversine formula."""
    R = 3959  # Earth radius in miles

    lat1 = math.radians(coord1.lat)
    lat2 = math.radians(coord2.lat)
    dlat = math.radians(coord2.lat - coord1.lat)
    dlng = math.radians(coord2.lng - coord1.lng)

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def get_directions_info(origin: Coordinates, dest: Coordinates, mode: str = "walking") -> tuple[int, float] | None:
    """Get travel time (minutes) and distance (km) via Google Directions API."""
    params = {
        "origin": f"{origin.lat},{origin.lng}",
        "destination": f"{dest.lat},{dest.lng}",
        "mode": mode,
        "key": API_KEY,
    }
    try:
        resp = requests.get(DIRECTIONS_URL, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "OK":
                leg = data["routes"][0]["legs"][0]
                duration_min = leg["duration"]["value"] // 60
                distance_km = leg["distance"]["value"] / 1000
                return (duration_min, distance_km)
    except Exception as e:
        print(f"Directions API error: {e}", file=sys.stderr)
    return None


def calculate_travel_time(origin: Coordinates, destination: Coordinates) -> tuple[int, float, str]:
    """Calculate travel time and distance using Directions API with Haversine fallback.

    Returns (minutes, distance_km, source) where source is 'directions_api' or 'estimated'.
    """
    # Try Directions API first
    result = get_directions_info(origin, destination)
    if result is not None:
        return (result[0], result[1], "directions_api")

    # Fallback: Haversine with 30% buffer for realistic routes
    distance_miles = calculate_distance(origin, destination)
    distance_km = distance_miles * 1.609
    haversine_time = int(distance_miles * 20 * 1.3)  # 3mph + 30% buffer
    return (haversine_time, distance_km * 1.3, "estimated")


def select_best_venues(venues: list[Venue], origin: Coordinates, budget: BudgetConstraints, count: int = 1) -> list[Venue]:
    """Select best venues based on scoring algorithm."""
    if not venues:
        return []

    scores = []
    for venue in venues:
        # Rating score (40%)
        rating_score = (venue.rating / 5.0) * 0.4

        # Distance score (30%) - closer is better
        distance = calculate_distance(origin, venue.location)
        distance_score = max(0, (1 - distance / 5.0)) * 0.3  # Normalize to 5 miles

        # Price match score (20%)
        if budget.min_price_level <= venue.price_level <= budget.max_price_level:
            price_score = 0.2
        else:
            price_score = 0.05

        # Popularity score (10%)
        popularity_score = min(venue.user_ratings_total / 1000, 1.0) * 0.1

        total_score = rating_score + distance_score + price_score + popularity_score
        scores.append((total_score, venue))

    # Sort by score descending
    scores.sort(key=lambda x: x[0], reverse=True)

    return [venue for _, venue in scores[:count]]


def check_venue_warnings(venue: Venue) -> list[str]:
    """Generate warnings for venues with variable availability."""
    warnings = []

    # Event-dependent venues
    venue_types = set(venue.types or [])
    event_types = venue_types & EVENT_DEPENDENT_TYPES
    if event_types:
        warnings.append(f"{venue.name} may have variable hours - check schedule before visiting")

    # Unknown opening hours
    if not venue.hours_known:
        warnings.append(f"Opening hours for {venue.name} could not be verified")
    elif venue.open_now is False:
        warnings.append(f"{venue.name} appears to be currently closed")

    return warnings


def generate_google_maps_link(start_location: str, venues: list[Venue]) -> str:
    """Generate Google Maps link with waypoints."""
    if not venues:
        return ""

    # URL encode addresses
    origin = urllib.parse.quote(start_location)
    destination = urllib.parse.quote(venues[-1].address)

    # Waypoints (all except last)
    waypoints = []
    for venue in venues[:-1]:
        waypoints.append(urllib.parse.quote(venue.address))

    waypoints_str = "|".join(waypoints) if waypoints else ""

    # Build URL
    base = "https://www.google.com/maps/dir/?api=1"
    url = f"{base}&origin={origin}&destination={destination}"

    if waypoints_str:
        url += f"&waypoints={waypoints_str}"

    url += "&travelmode=walking"

    return url


def generate_itinerary(event_type: str, location: str, party_size: int, budget_str: str, venues: list[Venue], start_time_str: str = None) -> Itinerary:
    """Generate full itinerary from selected venues."""
    if not venues:
        return Itinerary(
            event_type=event_type,
            location=location,
            party_size=party_size,
            budget=budget_str,
            items=[],
            total_duration_hours=0.0,
            total_cost_estimate="N/A",
            map_link="",
            preferences_applied=[],
            warnings=["No venues found"]
        )

    # Get event template
    template = EVENT_TEMPLATES.get(event_type.lower(), EVENT_TEMPLATES["dinner"])

    # Parse start time
    if start_time_str:
        try:
            current_time = datetime.strptime(start_time_str, "%H:%M")
        except:
            current_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    else:
        # Default times based on event type
        defaults = {
            "night-out": 19,  # 7 PM
            "date-night": 19,
            "lunch": 12,
            "dinner": 19,
            "weekend-day": 10,  # 10 AM
            "team-event": 18,
        }
        hour = defaults.get(event_type.lower(), 19)
        current_time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)

    # Build itinerary items
    items = []
    warnings = []
    total_duration = 0

    prev_location = None

    for i, venue in enumerate(venues):
        # Check venue-specific warnings
        venue_warnings = check_venue_warnings(venue)
        warnings.extend(venue_warnings)

        # Travel time and distance from previous
        travel_time = 0
        travel_distance_km = 0.0
        travel_source = ""
        if prev_location:
            travel_time, travel_distance_km, travel_source = calculate_travel_time(prev_location, venue.location)
            if travel_time > 20:
                source_note = " (estimated)" if travel_source == "estimated" else ""
                warnings.append(f"Long walk to {venue.name}: {travel_time} minutes{source_note}")

        # Arrival time
        if i > 0:
            current_time += timedelta(minutes=travel_time)

        arrival_time = current_time.strftime("%I:%M %p")

        # Duration
        duration = template[min(i, len(template)-1)].get("duration", 60)

        # Departure time
        departure_time = (current_time + timedelta(minutes=duration)).strftime("%I:%M %p")

        item = ItineraryItem(
            venue=venue,
            arrival_time=arrival_time,
            duration_minutes=duration,
            departure_time=departure_time,
            travel_from_previous_minutes=travel_time,
            travel_distance_km=travel_distance_km,
            travel_time_source=travel_source
        )
        items.append(item)

        total_duration += duration + travel_time
        current_time += timedelta(minutes=duration)
        prev_location = venue.location

    # Calculate cost estimate
    avg_price = sum(v.price_level for v in venues) / len(venues)
    price_ranges = {
        1: "$10-20",
        2: "$20-40",
        3: "$40-60",
        4: "$60+"
    }
    cost_estimate = f"{price_ranges.get(round(avg_price), '$20-40')} per person"

    # Generate map link
    map_link = generate_google_maps_link(location, venues)

    return Itinerary(
        event_type=event_type,
        location=location,
        party_size=party_size,
        budget=budget_str,
        items=items,
        total_duration_hours=total_duration / 60,
        total_cost_estimate=cost_estimate,
        map_link=map_link,
        preferences_applied=[],
        warnings=warnings
    )


def format_output_text(itinerary: Itinerary) -> str:
    """Format itinerary as Markdown text."""
    lines = [
        f"# Your {itinerary.event_type.title()} Itinerary",
        "",
        f"**Location**: {itinerary.location}",
        f"**Party Size**: {itinerary.party_size} {'person' if itinerary.party_size == 1 else 'people'}",
        f"**Budget**: {itinerary.budget}",
        f"**Total Duration**: {itinerary.total_duration_hours:.1f} hours",
        "",
        "## Schedule",
        "",
        "| Time | Venue | Type | Rating | Price | Notes |",
        "|------|-------|------|--------|-------|-------|",
    ]

    price_symbols = {0: "Free", 1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}

    for i, item in enumerate(itinerary.items):
        venue = item.venue
        price_str = price_symbols.get(venue.price_level, "$$")

        # Venue row
        venue_type = venue.types[0] if venue.types else "venue"
        notes = f"{item.duration_minutes} min"

        lines.append(
            f"| {item.arrival_time} | {venue.name} | {venue_type.title()} | {venue.rating:.1f} ⭐ | {price_str} | {notes} |"
        )

        # Travel row (if not last)
        if i < len(itinerary.items) - 1:
            next_item = itinerary.items[i+1]
            next_travel = next_item.travel_from_previous_minutes
            if next_travel > 0:
                distance_km = next_item.travel_distance_km
                source_note = " ~" if next_item.travel_time_source == "estimated" else ""
                lines.append(
                    f"| *Walk {next_travel} min{source_note}* | - | - | - | - | {distance_km:.1f} km |"
                )

    # Total walking distance
    total_distance_km = sum(item.travel_distance_km for item in itinerary.items)

    lines.extend([
        "",
        f"**Total Walking**: {total_distance_km:.1f} km",
        f"**Estimated Cost**: {itinerary.total_cost_estimate}",
        "",
        f"🗺️ **[View Route on Google Maps]({itinerary.map_link})**",
    ])

    if itinerary.warnings:
        lines.extend([
            "",
            "⚠️ **Warnings**:",
        ])
        for warning in itinerary.warnings:
            lines.append(f"- {warning}")

    lines.extend([
        "",
        "---",
        "💡 *Generated by Clawdbot Event Planner*"
    ])

    return "\n".join(lines)


def format_output_json(itinerary: Itinerary) -> str:
    """Format itinerary as JSON."""
    # Convert dataclasses to dicts
    items_dicts = []
    for item in itinerary.items:
        items_dicts.append({
            "venue": {
                "name": item.venue.name,
                "address": item.venue.address,
                "location": asdict(item.venue.location),
                "rating": item.venue.rating,
                "price_level": item.venue.price_level,
                "place_id": item.venue.place_id,
                "types": item.venue.types,
                "open_now": item.venue.open_now,
                "hours_known": item.venue.hours_known,
                "user_ratings_total": item.venue.user_ratings_total,
            },
            "arrival_time": item.arrival_time,
            "duration_minutes": item.duration_minutes,
            "departure_time": item.departure_time,
            "travel_from_previous_minutes": item.travel_from_previous_minutes,
            "travel_distance_km": item.travel_distance_km,
            "travel_time_source": item.travel_time_source,
        })

    output = {
        "event_type": itinerary.event_type,
        "location": itinerary.location,
        "party_size": itinerary.party_size,
        "budget": itinerary.budget,
        "items": items_dicts,
        "total_duration_hours": itinerary.total_duration_hours,
        "total_cost_estimate": itinerary.total_cost_estimate,
        "map_link": itinerary.map_link,
        "preferences_applied": itinerary.preferences_applied,
        "warnings": itinerary.warnings,
    }

    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Plan events using Google Places API"
    )
    parser.add_argument(
        "event_type",
        choices=["night-out", "weekend-day", "date-night", "team-event", "lunch", "dinner", "trip"],
        help="Type of event to plan"
    )
    parser.add_argument(
        "--location",
        required=True,
        help="Location for the event (city, address, landmark)"
    )
    parser.add_argument(
        "--party-size",
        type=int,
        default=2,
        help="Number of people (default: 2)"
    )
    parser.add_argument(
        "--budget",
        default="medium",
        help="Budget: 'low/medium/high' or '$X per person' (default: medium)"
    )
    parser.add_argument(
        "--duration",
        help="Duration (e.g., '3h', '4h', 'full day') - currently unused"
    )
    parser.add_argument(
        "--preferences",
        help="Comma-separated preferences (e.g., 'vegetarian, outdoor seating')"
    )
    parser.add_argument(
        "--start-time",
        help="Start time in HH:MM format (e.g., '19:00')"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--date",
        help="Target date in YYYY-MM-DD format for day-specific checks (default: today)"
    )

    args = parser.parse_args()

    # Check API key
    if not API_KEY:
        print("Error: GOOGLE_PLACES_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Resolve location
    print(f"Resolving location: {args.location}", file=sys.stderr)
    coords = resolve_location(args.location)

    if not coords:
        print(f"Error: Could not resolve location '{args.location}'", file=sys.stderr)
        sys.exit(2)

    print(f"Found: {coords.address} ({coords.lat}, {coords.lng})", file=sys.stderr)

    # Parse budget
    budget = parse_budget(args.budget, args.party_size)

    # Get event template
    template = EVENT_TEMPLATES.get(args.event_type, EVENT_TEMPLATES["dinner"])

    # Search for venues for each template item (with deduplication)
    all_venues = []
    selected_place_ids: set[str] = set()

    for template_item in template:
        query = template_item["query"]
        filters = template_item["filters"]

        print(f"Searching for: {query}", file=sys.stderr)
        venues = search_venues_with_fallback(query, coords, filters)

        # Filter out already-selected venues
        available = [v for v in venues if v.place_id not in selected_place_ids]

        if available:
            # Select best venue from available
            best = select_best_venues(available, coords, budget, count=1)
            if best:
                all_venues.append(best[0])
                selected_place_ids.add(best[0].place_id)
                print(f"  Found: {best[0].name} ({best[0].rating}⭐, {best[0].price_level})", file=sys.stderr)
        elif venues:
            # All filtered out - use best if not already selected
            best = select_best_venues(venues, coords, budget, count=1)
            if best and best[0].place_id not in selected_place_ids:
                all_venues.append(best[0])
                selected_place_ids.add(best[0].place_id)
                print(f"  Found (fallback): {best[0].name} ({best[0].rating}⭐)", file=sys.stderr)
            else:
                print(f"  No unique venues available for: {query}", file=sys.stderr)
        else:
            print(f"  No venues found for: {query}", file=sys.stderr)

    # Generate itinerary
    itinerary = generate_itinerary(
        args.event_type,
        args.location,
        args.party_size,
        args.budget,
        all_venues,
        args.start_time
    )

    # Output
    if args.output == "json":
        print(format_output_json(itinerary))
    else:
        print(format_output_text(itinerary))


if __name__ == "__main__":
    main()
