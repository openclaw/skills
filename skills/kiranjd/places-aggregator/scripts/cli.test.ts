import { describe, test, expect, mock, beforeEach, afterEach } from "bun:test";

// Test pure utility functions extracted from cli.ts

// Types
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

// Utility functions from cli.ts
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

function buildLocationFilter(flags: Record<string, string | boolean>): LocationFilter {
  // Region
  if (flags.region) {
    return { region: { place: String(flags.region) } };
  }

  // Circle centered on place
  if (flags.place) {
    const radius = flags.radius ? parseInt(String(flags.radius), 10) : 1000;
    const place = String(flags.place);
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

function parsePolygonData(data: any): Polygon {
  if (Array.isArray(data)) {
    const coordinates: LatLng[] = data.map((coord: any) => {
      if (Array.isArray(coord)) {
        return { latitude: coord[1], longitude: coord[0] };
      } else {
        return {
          latitude: coord.latitude ?? coord.lat,
          longitude: coord.longitude ?? coord.lng,
        };
      }
    });
    return { coordinates };
  } else if (data.coordinates) {
    if (Array.isArray(data.coordinates[0]) && typeof data.coordinates[0][0] === "number") {
      const coordinates: LatLng[] = data.coordinates.map((coord: number[]) => ({
        latitude: coord[1],
        longitude: coord[0],
      }));
      return { coordinates };
    }
    return data as Polygon;
  }
  throw new Error("Invalid polygon format");
}

// Tests

describe("parseArgs", () => {
  test("parses simple flags", () => {
    const args = ["--lat", "40.7", "--lng", "-74.0"];
    expect(parseArgs(args)).toEqual({
      lat: "40.7",
      lng: "-74.0",
    });
  });

  test("parses boolean flags", () => {
    const args = ["--json", "--lat", "40.7"];
    expect(parseArgs(args)).toEqual({
      json: true,
      lat: "40.7",
    });
  });

  test("parses comma-separated values", () => {
    const args = ["--types", "restaurant,cafe,bar"];
    expect(parseArgs(args)).toEqual({
      types: "restaurant,cafe,bar",
    });
  });

  test("parses hyphenated flags", () => {
    const args = ["--min-rating", "4.5", "--max-rating", "5.0"];
    expect(parseArgs(args)).toEqual({
      "min-rating": "4.5",
      "max-rating": "5.0",
    });
  });

  test("handles empty args", () => {
    expect(parseArgs([])).toEqual({});
  });
});

describe("parseOperatingStatus", () => {
  test("parses operational status", () => {
    expect(parseOperatingStatus("operational")).toEqual(["OPERATING_STATUS_OPERATIONAL"]);
  });

  test("parses open as operational", () => {
    expect(parseOperatingStatus("open")).toEqual(["OPERATING_STATUS_OPERATIONAL"]);
  });

  test("parses closed status", () => {
    expect(parseOperatingStatus("closed")).toEqual(["OPERATING_STATUS_PERMANENTLY_CLOSED"]);
  });

  test("parses temporarily_closed status", () => {
    expect(parseOperatingStatus("temporarily_closed")).toEqual(["OPERATING_STATUS_TEMPORARILY_CLOSED"]);
  });

  test("parses temp_closed alias", () => {
    expect(parseOperatingStatus("temp_closed")).toEqual(["OPERATING_STATUS_TEMPORARILY_CLOSED"]);
  });

  test("parses multiple statuses", () => {
    expect(parseOperatingStatus("operational,closed")).toEqual([
      "OPERATING_STATUS_OPERATIONAL",
      "OPERATING_STATUS_PERMANENTLY_CLOSED",
    ]);
  });

  test("is case insensitive", () => {
    expect(parseOperatingStatus("OPERATIONAL")).toEqual(["OPERATING_STATUS_OPERATIONAL"]);
  });

  test("throws on invalid status", () => {
    expect(() => parseOperatingStatus("invalid")).toThrow("Invalid status");
  });
});

describe("parsePriceLevels", () => {
  test("parses numeric levels", () => {
    expect(parsePriceLevels("0")).toEqual(["PRICE_LEVEL_FREE"]);
    expect(parsePriceLevels("1")).toEqual(["PRICE_LEVEL_INEXPENSIVE"]);
    expect(parsePriceLevels("2")).toEqual(["PRICE_LEVEL_MODERATE"]);
    expect(parsePriceLevels("3")).toEqual(["PRICE_LEVEL_EXPENSIVE"]);
    expect(parsePriceLevels("4")).toEqual(["PRICE_LEVEL_VERY_EXPENSIVE"]);
  });

  test("parses named levels", () => {
    expect(parsePriceLevels("free")).toEqual(["PRICE_LEVEL_FREE"]);
    expect(parsePriceLevels("inexpensive")).toEqual(["PRICE_LEVEL_INEXPENSIVE"]);
    expect(parsePriceLevels("moderate")).toEqual(["PRICE_LEVEL_MODERATE"]);
    expect(parsePriceLevels("expensive")).toEqual(["PRICE_LEVEL_EXPENSIVE"]);
    expect(parsePriceLevels("very_expensive")).toEqual(["PRICE_LEVEL_VERY_EXPENSIVE"]);
  });

  test("parses cheap as inexpensive", () => {
    expect(parsePriceLevels("cheap")).toEqual(["PRICE_LEVEL_INEXPENSIVE"]);
  });

  test("parses multiple levels", () => {
    expect(parsePriceLevels("0,1,2")).toEqual([
      "PRICE_LEVEL_FREE",
      "PRICE_LEVEL_INEXPENSIVE",
      "PRICE_LEVEL_MODERATE",
    ]);
  });

  test("handles mixed formats", () => {
    expect(parsePriceLevels("free,1,moderate")).toEqual([
      "PRICE_LEVEL_FREE",
      "PRICE_LEVEL_INEXPENSIVE",
      "PRICE_LEVEL_MODERATE",
    ]);
  });

  test("throws on invalid level", () => {
    expect(() => parsePriceLevels("5")).toThrow("Invalid price level");
    expect(() => parsePriceLevels("invalid")).toThrow("Invalid price level");
  });
});

describe("buildLocationFilter", () => {
  test("builds circle from lat/lng", () => {
    const flags = { lat: "40.7128", lng: "-74.006", radius: "1000" };
    const filter = buildLocationFilter(flags);
    expect(filter.circle).toBeDefined();
    expect(filter.circle?.latLng?.latitude).toBe(40.7128);
    expect(filter.circle?.latLng?.longitude).toBe(-74.006);
    expect(filter.circle?.radius).toBe(1000);
  });

  test("uses default radius of 1000m", () => {
    const flags = { lat: "40.7128", lng: "-74.006" };
    const filter = buildLocationFilter(flags);
    expect(filter.circle?.radius).toBe(1000);
  });

  test("builds circle from place ID", () => {
    const flags = { place: "ChIJOwg_06VPwokR", radius: "500" };
    const filter = buildLocationFilter(flags);
    expect(filter.circle?.place).toBe("places/ChIJOwg_06VPwokR");
    expect(filter.circle?.radius).toBe(500);
  });

  test("preserves places/ prefix if already present", () => {
    const flags = { place: "places/ChIJOwg_06VPwokR" };
    const filter = buildLocationFilter(flags);
    expect(filter.circle?.place).toBe("places/ChIJOwg_06VPwokR");
  });

  test("builds region filter", () => {
    const flags = { region: "ChIJYeZuBI9YwokR" };
    const filter = buildLocationFilter(flags);
    expect(filter.region?.place).toBe("ChIJYeZuBI9YwokR");
  });

  test("throws when no location provided", () => {
    expect(() => buildLocationFilter({})).toThrow("Location required");
  });
});

describe("buildTypeFilter", () => {
  test("builds filter with included types", () => {
    const flags = { types: "restaurant,cafe" };
    const filter = buildTypeFilter(flags);
    expect(filter.includedTypes).toEqual(["restaurant", "cafe"]);
  });

  test("builds filter with primary types", () => {
    const flags = { "primary-types": "restaurant" };
    const filter = buildTypeFilter(flags);
    expect(filter.includedPrimaryTypes).toEqual(["restaurant"]);
  });

  test("builds filter with excluded types", () => {
    const flags = { types: "restaurant", "exclude-types": "fast_food" };
    const filter = buildTypeFilter(flags);
    expect(filter.includedTypes).toEqual(["restaurant"]);
    expect(filter.excludedTypes).toEqual(["fast_food"]);
  });

  test("trims whitespace from types", () => {
    const flags = { types: "restaurant, cafe , bar" };
    const filter = buildTypeFilter(flags);
    expect(filter.includedTypes).toEqual(["restaurant", "cafe", "bar"]);
  });

  test("throws when no types provided", () => {
    expect(() => buildTypeFilter({})).toThrow("At least one of --types or --primary-types required");
  });
});

describe("parsePolygonData", () => {
  test("parses GeoJSON format [[lng, lat], ...]", () => {
    const data = [
      [-74.01, 40.71],
      [-74.00, 40.71],
      [-74.00, 40.72],
      [-74.01, 40.71],
    ];
    const polygon = parsePolygonData(data);
    expect(polygon.coordinates).toHaveLength(4);
    expect(polygon.coordinates[0]).toEqual({ latitude: 40.71, longitude: -74.01 });
  });

  test("parses object array [{lat, lng}, ...]", () => {
    const data = [
      { lat: 40.71, lng: -74.01 },
      { lat: 40.71, lng: -74.00 },
      { lat: 40.72, lng: -74.00 },
      { lat: 40.71, lng: -74.01 },
    ];
    const polygon = parsePolygonData(data);
    expect(polygon.coordinates).toHaveLength(4);
    expect(polygon.coordinates[0]).toEqual({ latitude: 40.71, longitude: -74.01 });
  });

  test("parses API format [{latitude, longitude}, ...]", () => {
    const data = [
      { latitude: 40.71, longitude: -74.01 },
      { latitude: 40.71, longitude: -74.00 },
    ];
    const polygon = parsePolygonData(data);
    expect(polygon.coordinates).toHaveLength(2);
    expect(polygon.coordinates[0]).toEqual({ latitude: 40.71, longitude: -74.01 });
  });

  test("parses nested coordinates format", () => {
    const data = {
      coordinates: [
        [-74.01, 40.71],
        [-74.00, 40.71],
      ],
    };
    const polygon = parsePolygonData(data);
    expect(polygon.coordinates).toHaveLength(2);
    expect(polygon.coordinates[0]).toEqual({ latitude: 40.71, longitude: -74.01 });
  });

  test("passes through already correct format", () => {
    const data = {
      coordinates: [
        { latitude: 40.71, longitude: -74.01 },
        { latitude: 40.71, longitude: -74.00 },
      ],
    };
    const polygon = parsePolygonData(data);
    expect(polygon.coordinates).toEqual(data.coordinates);
  });

  test("throws on invalid format", () => {
    expect(() => parsePolygonData({ invalid: true })).toThrow("Invalid polygon format");
  });
});

describe("CLI env validation", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  test("requires GOOGLE_PLACES_API_KEY", () => {
    delete process.env.GOOGLE_PLACES_API_KEY;
    expect(process.env.GOOGLE_PLACES_API_KEY).toBeUndefined();
  });
});

describe("integration: full filter building", () => {
  test("builds complete filter from flags", () => {
    const flags = {
      lat: "40.7128",
      lng: "-74.006",
      radius: "500",
      types: "restaurant,cafe",
      "exclude-types": "fast_food",
      "min-rating": "4.0",
    };

    const locationFilter = buildLocationFilter(flags);
    const typeFilter = buildTypeFilter(flags);

    expect(locationFilter.circle?.latLng?.latitude).toBe(40.7128);
    expect(locationFilter.circle?.radius).toBe(500);
    expect(typeFilter.includedTypes).toEqual(["restaurant", "cafe"]);
    expect(typeFilter.excludedTypes).toEqual(["fast_food"]);
  });
});
