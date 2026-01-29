#!/usr/bin/env bun
/**
 * Places Aggregator CLI - Area insights from Google Places
 * Usage: bun skills/places-aggregator/scripts/cli.ts <command> [options]
 *
 * Full API coverage for https://areainsights.googleapis.com/v1:computeInsights
 */

import { readFileSync, existsSync } from "fs";

const API_KEY = process.env.GOOGLE_PLACES_API_KEY;
const API_URL = "https://areainsights.googleapis.com/v1:computeInsights";

if (!API_KEY) {
  console.error("Error: GOOGLE_PLACES_API_KEY environment variable required");
  process.exit(1);
}

// Types matching the API exactly
interface LatLng {
  latitude: number;
  longitude: number;
}

interface Circle {
  radius: number;
  latLng?: LatLng;
  place?: string;
}

interface Region {
  place: string;
}

interface Polygon {
  coordinates: LatLng[];
}

interface CustomArea {
  polygon: Polygon;
}

interface LocationFilter {
  circle?: Circle;
  region?: Region;
  customArea?: CustomArea;
}

interface TypeFilter {
  includedTypes?: string[];
  excludedTypes?: string[];
  includedPrimaryTypes?: string[];
  excludedPrimaryTypes?: string[];
}

interface RatingFilter {
  minRating?: number;
  maxRating?: number;
}

type OperatingStatus =
  | "OPERATING_STATUS_OPERATIONAL"
  | "OPERATING_STATUS_PERMANENTLY_CLOSED"
  | "OPERATING_STATUS_TEMPORARILY_CLOSED";

type PriceLevel =
  | "PRICE_LEVEL_FREE"
  | "PRICE_LEVEL_INEXPENSIVE"
  | "PRICE_LEVEL_MODERATE"
  | "PRICE_LEVEL_EXPENSIVE"
  | "PRICE_LEVEL_VERY_EXPENSIVE";

interface Filter {
  locationFilter: LocationFilter;
  typeFilter: TypeFilter;
  operatingStatus?: OperatingStatus[];
  priceLevels?: PriceLevel[];
  ratingFilter?: RatingFilter;
}

type Insight = "INSIGHT_COUNT" | "INSIGHT_PLACES";

interface InsightsRequest {
  insights: Insight[];
  filter: Filter;
}

interface PlaceInsight {
  place: string;
}

interface InsightsResponse {
  placeInsights?: PlaceInsight[];
  count?: string;
}

// Parse command line
function parseArgs(args: string[]): Record<string, string | boolean> {
  const flags: Record<string, string | boolean> = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith("--")) {
        flags[key] = next;
        i++;
      } else {
        flags[key] = true;
      }
    }
  }
  return flags;
}

// Parse polygon from file or inline JSON
function parsePolygon(input: string): Polygon {
  let data: any;

  // Check if it's a file path
  if (existsSync(input)) {
    const content = readFileSync(input, "utf-8");
    data = JSON.parse(content);
  } else {
    // Try parsing as inline JSON
    data = JSON.parse(input);
  }

  // Handle different formats
  if (Array.isArray(data)) {
    // Array of [lng, lat] pairs (GeoJSON style) or {lat, lng} objects
    const coordinates: LatLng[] = data.map((coord: any) => {
      if (Array.isArray(coord)) {
        // [lng, lat] format
        return { latitude: coord[1], longitude: coord[0] };
      } else {
        // {lat, lng} or {latitude, longitude} format
        return {
          latitude: coord.latitude ?? coord.lat,
          longitude: coord.longitude ?? coord.lng,
        };
      }
    });
    return { coordinates };
  } else if (data.coordinates) {
    // Already in correct format or nested
    if (Array.isArray(data.coordinates[0]) && typeof data.coordinates[0][0] === "number") {
      // GeoJSON polygon coordinates [[lng,lat], ...]
      const coordinates: LatLng[] = data.coordinates.map((coord: number[]) => ({
        latitude: coord[1],
        longitude: coord[0],
      }));
      return { coordinates };
    }
    return data as Polygon;
  }

  throw new Error("Invalid polygon format. Expected array of coordinates or {coordinates: [...]}");
}

// Build location filter (one of: circle, region, customArea)
function buildLocationFilter(flags: Record<string, string | boolean>): LocationFilter {
  // CustomArea with polygon
  if (flags.polygon) {
    const polygon = parsePolygon(String(flags.polygon));
    return { customArea: { polygon } };
  }

  // Region
  if (flags.region) {
    return { region: { place: String(flags.region) } };
  }

  // Circle centered on place
  if (flags.place) {
    const radius = flags.radius ? parseInt(String(flags.radius), 10) : 1000;
    const place = String(flags.place);
    // API expects "places/PLACE_ID" format
    const formattedPlace = place.startsWith("places/") ? place : `places/${place}`;
    return {
      circle: {
        place: formattedPlace,
        radius,
      },
    };
  }

  // Circle with lat/lng
  if (flags.lat && flags.lng) {
    const radius = flags.radius ? parseInt(String(flags.radius), 10) : 1000;
    return {
      circle: {
        latLng: {
          latitude: parseFloat(String(flags.lat)),
          longitude: parseFloat(String(flags.lng)),
        },
        radius,
      },
    };
  }

  throw new Error(
    "Location required: --lat/--lng/--radius (circle), --place (circle), --region, or --polygon (custom area)"
  );
}

// Build type filter
function buildTypeFilter(flags: Record<string, string | boolean>): TypeFilter {
  const filter: TypeFilter = {};

  if (flags.types) {
    filter.includedTypes = String(flags.types).split(",").map((t) => t.trim());
  }
  if (flags["exclude-types"]) {
    filter.excludedTypes = String(flags["exclude-types"]).split(",").map((t) => t.trim());
  }
  if (flags["primary-types"]) {
    filter.includedPrimaryTypes = String(flags["primary-types"]).split(",").map((t) => t.trim());
  }
  if (flags["exclude-primary-types"]) {
    filter.excludedPrimaryTypes = String(flags["exclude-primary-types"]).split(",").map((t) => t.trim());
  }

  if (!filter.includedTypes && !filter.includedPrimaryTypes) {
    throw new Error("At least one of --types or --primary-types required");
  }

  return filter;
}

// Parse operating status
function parseOperatingStatus(input: string): OperatingStatus[] {
  const statusMap: Record<string, OperatingStatus> = {
    operational: "OPERATING_STATUS_OPERATIONAL",
    open: "OPERATING_STATUS_OPERATIONAL",
    closed: "OPERATING_STATUS_PERMANENTLY_CLOSED",
    permanently_closed: "OPERATING_STATUS_PERMANENTLY_CLOSED",
    temporarily_closed: "OPERATING_STATUS_TEMPORARILY_CLOSED",
    temp_closed: "OPERATING_STATUS_TEMPORARILY_CLOSED",
  };

  return input.split(",").map((s) => {
    const key = s.trim().toLowerCase();
    const mapped = statusMap[key];
    if (!mapped) {
      throw new Error(`Invalid status: ${s}. Valid: operational, closed, temporarily_closed`);
    }
    return mapped;
  });
}

// Parse price levels
function parsePriceLevels(input: string): PriceLevel[] {
  const priceMap: Record<string, PriceLevel> = {
    "0": "PRICE_LEVEL_FREE",
    free: "PRICE_LEVEL_FREE",
    "1": "PRICE_LEVEL_INEXPENSIVE",
    inexpensive: "PRICE_LEVEL_INEXPENSIVE",
    cheap: "PRICE_LEVEL_INEXPENSIVE",
    "2": "PRICE_LEVEL_MODERATE",
    moderate: "PRICE_LEVEL_MODERATE",
    "3": "PRICE_LEVEL_EXPENSIVE",
    expensive: "PRICE_LEVEL_EXPENSIVE",
    "4": "PRICE_LEVEL_VERY_EXPENSIVE",
    very_expensive: "PRICE_LEVEL_VERY_EXPENSIVE",
  };

  return input.split(",").map((p) => {
    const key = p.trim().toLowerCase();
    const mapped = priceMap[key];
    if (!mapped) {
      throw new Error(`Invalid price level: ${p}. Valid: 0-4 or free/inexpensive/moderate/expensive/very_expensive`);
    }
    return mapped;
  });
}

// Build full filter
function buildFilter(flags: Record<string, string | boolean>): Filter {
  const filter: Filter = {
    locationFilter: buildLocationFilter(flags),
    typeFilter: buildTypeFilter(flags),
  };

  // Operating status
  if (flags.status) {
    filter.operatingStatus = parseOperatingStatus(String(flags.status));
  }

  // Price levels
  if (flags.price) {
    filter.priceLevels = parsePriceLevels(String(flags.price));
  }

  // Rating filter
  if (flags["min-rating"] || flags["max-rating"]) {
    filter.ratingFilter = {};
    if (flags["min-rating"]) {
      const min = parseFloat(String(flags["min-rating"]));
      if (min < 1 || min > 5) throw new Error("min-rating must be between 1.0 and 5.0");
      filter.ratingFilter.minRating = min;
    }
    if (flags["max-rating"]) {
      const max = parseFloat(String(flags["max-rating"]));
      if (max < 1 || max > 5) throw new Error("max-rating must be between 1.0 and 5.0");
      filter.ratingFilter.maxRating = max;
    }
  }

  return filter;
}

// Make API request
async function computeInsights(request: InsightsRequest): Promise<InsightsResponse> {
  const response = await fetch(`${API_URL}?key=${API_KEY}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error ${response.status}: ${error}`);
  }

  return response.json();
}

// Format location for display
function formatLocation(loc: LocationFilter): string {
  if (loc.circle?.latLng) {
    const { latitude, longitude } = loc.circle.latLng;
    return `Circle: ${latitude.toFixed(4)}, ${longitude.toFixed(4)} (${loc.circle.radius}m)`;
  }
  if (loc.circle?.place) {
    return `Circle: ${loc.circle.place} (${loc.circle.radius}m)`;
  }
  if (loc.region) {
    return `Region: ${loc.region.place}`;
  }
  if (loc.customArea?.polygon) {
    const coords = loc.customArea.polygon.coordinates;
    return `Polygon: ${coords.length} vertices`;
  }
  return "Unknown";
}

// Format price level for display
function formatPriceLevel(level: PriceLevel): string {
  const names: Record<PriceLevel, string> = {
    PRICE_LEVEL_FREE: "Free",
    PRICE_LEVEL_INEXPENSIVE: "Inexpensive ($)",
    PRICE_LEVEL_MODERATE: "Moderate ($$)",
    PRICE_LEVEL_EXPENSIVE: "Expensive ($$$)",
    PRICE_LEVEL_VERY_EXPENSIVE: "Very Expensive ($$$$)",
  };
  return names[level] || level;
}

// Format operating status for display
function formatStatus(status: OperatingStatus): string {
  const names: Record<OperatingStatus, string> = {
    OPERATING_STATUS_OPERATIONAL: "Operational",
    OPERATING_STATUS_PERMANENTLY_CLOSED: "Permanently Closed",
    OPERATING_STATUS_TEMPORARILY_CLOSED: "Temporarily Closed",
  };
  return names[status] || status;
}

// Print filter summary
function printFilterSummary(filter: Filter) {
  console.log("\nFilter:");
  console.log(`  Location: ${formatLocation(filter.locationFilter)}`);

  const types =
    filter.typeFilter.includedTypes?.join(", ") ||
    filter.typeFilter.includedPrimaryTypes?.join(", ");
  console.log(`  Types: ${types}`);

  if (filter.typeFilter.excludedTypes?.length) {
    console.log(`  Excluded: ${filter.typeFilter.excludedTypes.join(", ")}`);
  }

  if (filter.operatingStatus?.length) {
    console.log(`  Status: ${filter.operatingStatus.map(formatStatus).join(", ")}`);
  }

  if (filter.priceLevels?.length) {
    console.log(`  Price: ${filter.priceLevels.map(formatPriceLevel).join(", ")}`);
  }

  if (filter.ratingFilter) {
    const { minRating, maxRating } = filter.ratingFilter;
    if (minRating && maxRating) {
      console.log(`  Rating: ${minRating} - ${maxRating}`);
    } else if (minRating) {
      console.log(`  Rating: >= ${minRating}`);
    } else if (maxRating) {
      console.log(`  Rating: <= ${maxRating}`);
    }
  }
}

// Commands

async function count(flags: Record<string, string | boolean>) {
  const request: InsightsRequest = {
    insights: ["INSIGHT_COUNT"],
    filter: buildFilter(flags),
  };

  const result = await computeInsights(request);

  if (flags.json) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  const count = result.count || "0";
  console.log(`Places matching criteria: ${count}`);
  printFilterSummary(request.filter);
}

async function list(flags: Record<string, string | boolean>) {
  const request: InsightsRequest = {
    insights: ["INSIGHT_PLACES"],
    filter: buildFilter(flags),
  };

  const result = await computeInsights(request);

  if (flags.json) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  const places = result.placeInsights || [];
  const count = result.count || places.length.toString();

  console.log(`Found ${count} places`);

  if (places.length === 0) {
    console.log("\nNo place IDs returned (count may exceed 100)");
    printFilterSummary(request.filter);
    return;
  }

  console.log("\nPlace IDs:");
  for (const p of places) {
    // Extract place ID from "places/PLACE_ID" format
    const placeId = p.place.replace("places/", "");
    console.log(`  ${placeId}`);
  }

  printFilterSummary(request.filter);
  console.log("\nTip: Use 'goplaces details <place_id>' to get full details");
}

async function both(flags: Record<string, string | boolean>) {
  const request: InsightsRequest = {
    insights: ["INSIGHT_COUNT", "INSIGHT_PLACES"],
    filter: buildFilter(flags),
  };

  const result = await computeInsights(request);

  if (flags.json) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  const places = result.placeInsights || [];
  const count = result.count || "0";

  console.log(`Total count: ${count}`);
  console.log(`Place IDs returned: ${places.length}`);

  if (places.length > 0) {
    console.log("\nPlace IDs:");
    for (const p of places) {
      const placeId = p.place.replace("places/", "");
      console.log(`  ${placeId}`);
    }
  } else if (parseInt(count, 10) > 100) {
    console.log("\n(Place IDs only returned when count <= 100)");
  }

  printFilterSummary(request.filter);
}

// Help
function help() {
  console.log(`
Places Aggregator CLI - Full API Coverage

Usage: places-aggregator <command> [options]

Commands:
  count    Count places matching filters (INSIGHT_COUNT)
  list     List place IDs matching filters (INSIGHT_PLACES, max 100)
  both     Get both count and place IDs in one request

Location Filters (exactly one required):

  Circle by coordinates:
    --lat <number>              Latitude (-90 to 90)
    --lng <number>              Longitude (-180 to 180)
    --radius <meters>           Search radius (default: 1000)

  Circle by place:
    --place <place_id>          Center circle on place ID
    --radius <meters>           Search radius (default: 1000)

  Region:
    --region <place_id>         Geographic region boundary (city, state, etc.)

  Custom polygon:
    --polygon <file_or_json>    Polygon coordinates (JSON file or inline)
                                Formats: [[lng,lat],...] or [{lat,lng},...]
                                Must be counterclockwise, first=last point

Type Filters (at least one of --types or --primary-types required):
  --types <t1,t2,...>           Place types to include
  --exclude-types <t1,t2>       Place types to exclude
  --primary-types <t1,t2>       Primary types to include
  --exclude-primary-types <t>   Primary types to exclude

Operating Status:
  --status <s1,s2>              Filter by status (comma-separated)
                                Values: operational, closed, temporarily_closed

Price Levels:
  --price <p1,p2,...>           Filter by price (comma-separated)
                                Values: 0-4 or free/inexpensive/moderate/expensive/very_expensive

Rating:
  --min-rating <1.0-5.0>        Minimum rating
  --max-rating <1.0-5.0>        Maximum rating

Output:
  --json                        Output raw JSON response

Examples:

  # Count coffee shops in 500m radius
  places-aggregator count --lat 40.7484 --lng -73.9857 --radius 500 --types coffee_shop

  # List highly-rated restaurants (IDs only when <= 100)
  places-aggregator list --lat 40.758 --lng -73.9855 --radius 300 --types restaurant --min-rating 4.5

  # Budget cafes only
  places-aggregator count --lat 51.5074 --lng -0.1278 --radius 1000 --types cafe --price 0,1,2

  # Filter by status
  places-aggregator count --lat 40.7 --lng -74.0 --radius 1000 --types restaurant --status operational

  # Use a region (Manhattan)
  places-aggregator count --region ChIJYeZuBI9YwokRjMDs_IEyCwo --types bar

  # Use a polygon (from file)
  places-aggregator count --polygon ./my-area.json --types restaurant

  # Use polygon inline (GeoJSON format: [lng, lat])
  places-aggregator count --polygon '[[-74.01,40.71],[-74.00,40.71],[-74.00,40.72],[-74.01,40.72],[-74.01,40.71]]' --types cafe

  # Get both count and place IDs
  places-aggregator both --lat 40.75 --lng -73.98 --radius 200 --types coffee_shop

Common Place Types:
  restaurant, cafe, bar, coffee_shop, bakery, grocery_store, supermarket,
  gym, park, museum, hotel, hospital, pharmacy, bank, atm, gas_station,
  parking, school, university, library, movie_theater, shopping_mall

Full list: https://developers.google.com/maps/documentation/places/web-service/place-types

Environment:
  GOOGLE_PLACES_API_KEY      Google Places API key (required)
`);
}

// Main
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  const flags = parseArgs(args.slice(1));

  try {
    switch (cmd) {
      case "count":
        await count(flags);
        break;
      case "list":
        await list(flags);
        break;
      case "both":
        await both(flags);
        break;
      case "help":
      case "--help":
      case "-h":
      case undefined:
        help();
        break;
      default:
        console.error(`Unknown command: ${cmd}`);
        help();
        process.exit(1);
    }
  } catch (err) {
    console.error(`Error: ${err instanceof Error ? err.message : err}`);
    process.exit(1);
  }
}

main();
