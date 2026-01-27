---
name: mechanic
description: "Vehicle maintenance tracker and mechanic advisor. Tracks mileage, service intervals, fuel economy, costs, warranties, and recalls. Researches manufacturer schedules, estimates costs, projects service dates, tracks providers, and proactively reminds about upcoming/overdue services. Supports VIN decode and auto-population of vehicle specs, NHTSA recall monitoring, MPG tracking with anomaly detection, warranty expiration alerts, pre-trip/seasonal checklists, mileage projection, service provider history, tax deduction integration, emergency info cards, and cost-per-mile analysis. Use when discussing vehicle maintenance, oil changes, service intervals, mileage tracking, fuel economy, warranties, recalls, RV maintenance, roof sealing, generator service, slide-outs, winterization, or anything mechanic-related. Supports any vehicle type including trucks, cars, motorcycles, dirt bikes, ATVs, RVs, and boats."
homepage: https://github.com/ScotTFO/mechanic-skill
metadata: {"clawdbot":{"emoji":"🔧"}}
---

# Mechanic — Vehicle Maintenance Tracker

Track mileage and service intervals for any combination of vehicles — trucks, cars, motorcycles, RVs, dirt bikes, ATVs, boats, and more. Decodes VINs to auto-populate vehicle specs, researches manufacturer-recommended maintenance schedules, tracks service history, estimates costs, monitors recalls, tracks fuel economy, manages warranties, and proactively reminds about upcoming and overdue services.

## Data Storage

All user data lives in `<workspace>/data/mechanic/`:

| File | Purpose |
|------|---------|
| `state.json` | All vehicles: current mileage/hours, history, service records, fuel logs, warranties, providers, emergency info |
| `<key>-schedule.json` | Per-vehicle service schedule with intervals and cost estimates |

**Convention:** Skill logic lives in `<skill>/`, user data lives in `<workspace>/data/mechanic/`. This keeps data safe when the skill is updated or reinstalled.

## First-Time Setup

If `<workspace>/data/mechanic/state.json` doesn't exist:
1. Create `<workspace>/data/mechanic/` directory
2. Ask the user what vehicles they want to track
3. For each vehicle, run the **Adding a New Vehicle** workflow (includes choosing check-in frequency per vehicle)
4. Create `state.json` with the vehicle entries
5. Set up the cron job (see **Mileage Check Setup**)

### State File Structure
```json
{
  "settings": {
    "check_in_tz": "America/Phoenix"
  },
  "providers": [
    {
      "id": "jims_diesel",
      "name": "Jim's Diesel Repair",
      "location": "123 Main St, Mesa, AZ",
      "phone": "480-555-1234",
      "specialties": ["diesel", "trucks"],
      "rating": 5,
      "notes": "Great with Power Stroke engines"
    }
  ],
  "vehicles": {
    "f350": {
      "label": "2021 Ford F-350 6.7L Power Stroke",
      "schedule_file": "f350-schedule.json",
      "check_in_frequency": "monthly",
      "current_miles": 61450,
      "last_updated": "2026-01-26",
      "last_check_in": "2026-01-26",
      "vin": "1FT8W3BT0MED12345",
      "vin_data": {
        "decoded": true,
        "decoded_date": "2026-01-26",
        "year": 2021,
        "make": "Ford",
        "model": "F-350",
        "trim": "Lariat",
        "body_class": "Pickup",
        "drive_type": "4WD",
        "engine": "6.7L Power Stroke V8 Turbo Diesel",
        "displacement_l": 6.7,
        "cylinders": 8,
        "fuel_type": "Diesel",
        "transmission": "10-Speed Automatic",
        "doors": 4,
        "gvwr_class": "Class 3",
        "bed_length": "8 ft",
        "wheel_base": "176 in",
        "plant_country": "United States",
        "plant_city": "Louisville",
        "raw_response": {}
      },
      "business_use": false,
      "business_use_percent": 0,
      "mileage_history": [
        {"date": "2026-01-26", "miles": 61450, "source": "user_reported"}
      ],
      "service_history": [
        {
          "service_id": "oil_filter",
          "date": "2025-11-15",
          "miles": 58000,
          "hours": null,
          "notes": "Full synthetic Motorcraft FL-2051S",
          "actual_cost": 125.00,
          "provider": {
            "id": "jims_diesel",
            "name": "Jim's Diesel Repair",
            "parts_warranty_months": 12,
            "labor_warranty_months": 6
          }
        }
      ],
      "fuel_history": [
        {
          "date": "2026-01-20",
          "gallons": 32.5,
          "cost": 108.55,
          "odometer": 61300,
          "mpg": 14.2,
          "notes": "Regular fill-up"
        }
      ],
      "warranties": [
        {
          "type": "factory_powertrain",
          "provider": "Ford",
          "start_date": "2021-03-15",
          "end_date": "2026-03-15",
          "start_miles": 0,
          "end_miles": 60000,
          "coverage_details": "Engine, transmission, drivetrain components",
          "status": "active"
        }
      ],
      "recalls": {
        "last_checked": "2026-01-26",
        "open_recalls": [],
        "completed_recalls": []
      },
      "emergency_info": {
        "vin": "1FT8W3BT0MED12345",
        "insurance_provider": "State Farm",
        "policy_number": "SF-123456789",
        "roadside_assistance_phone": "1-800-555-1234",
        "tire_size_front": "275/70R18",
        "tire_size_rear": "275/70R18",
        "tire_pressure_front_psi": 65,
        "tire_pressure_rear_psi": 80,
        "oil_type": "15W-40 CK-4 Full Synthetic",
        "oil_capacity": "15 quarts",
        "coolant_type": "Motorcraft Orange VC-3DIL-B",
        "def_type": "API certified DEF",
        "tow_rating_lbs": 20000,
        "gvwr_lbs": 14000,
        "gcwr_lbs": 37000,
        "key_fob_battery": "CR2450",
        "fuel_type": "Diesel (Ultra Low Sulfur)",
        "fuel_tank_gallons": 48,
        "notes": ""
      }
    }
  },
  "last_service_review": "2026-01-26"
}
```

**Top-level fields:**
- `settings` — global settings (timezone, etc.)
- `providers` — reusable list of service providers
- `vehicles` — keyed by short slug (e.g., `f350`, `rv`, `crf450`)
- `last_service_review` — date of last full review

**Per-vehicle fields:**
- `label` — human-readable vehicle name
- `schedule_file` — path to the service schedule JSON
- `check_in_frequency` — how often to ask for mileage (weekly/biweekly/monthly/quarterly)
- `current_miles` / `current_hours` — latest known readings
- `last_updated` / `last_check_in` — date tracking
- `vin` — Vehicle Identification Number (for recalls, VIN decode, and emergency info)
- `vin_data` — decoded VIN data from NHTSA VPIC API (specs, engine, transmission, etc.)
- `business_use` — whether vehicle is used for business (boolean)
- `business_use_percent` — percentage of business use (0-100)
- `mileage_history` — chronological array of mileage/hours entries
- `service_history` — chronological array of completed services (with optional `actual_cost` and `provider`)
- `fuel_history` — chronological array of fuel fill-ups
- `warranties` — array of warranty records
- `recalls` — recall monitoring state (last checked, open/completed)
- `emergency_info` — quick-reference vehicle specs and emergency contacts

## Reading State

On skill load, read:
1. `<workspace>/data/mechanic/state.json` — current state for all vehicles
2. The relevant `<key>-schedule.json` file(s) depending on what's being discussed

## Adding a New Vehicle

When the user wants to track a new vehicle:

### 1. Gather Vehicle Info
**Ask for the VIN first.** If the user provides a VIN, run the **VIN Decode** (see below) to auto-populate year, make, model, engine, transmission, drive type, and other specs. This saves the user from answering questions you can look up automatically.

Ask for:
- **VIN** (strongly recommended — auto-populates specs, enables recall monitoring, emergency info)
- **Year, make, model** (only ask if no VIN provided)
- **Engine/trim** (only ask if no VIN or VIN decode was incomplete)
- **Usage pattern** — daily driver, towing, off-road, weekend toy, etc.
- **Current mileage/hours**
- **Business use?** — if yes, what percentage? (enables tax deduction tracking)
- **Warranty info** — any active factory or extended warranties? Expiration date/mileage?
- **Emergency info** — insurance provider, roadside assistance number, tire sizes (can be filled in later)

If the user doesn't have the VIN handy, proceed with manual info and note that VIN can be added later to unlock auto-population and recall monitoring.

### 2. Determine Duty Level
Ask about usage to classify the maintenance schedule:

| Usage | Duty Level | Effect |
|-------|-----------|--------|
| Normal commuting | Normal | Standard intervals |
| Towing, hauling | Severe | Shorter intervals (typically 50-75% of normal) |
| Off-road, dusty conditions | Severe | Shorter intervals, more frequent filter changes |
| Extreme temps (hot desert, harsh cold) | Severe | Shorter intervals, fluid/battery concerns |
| Track/racing | Severe+ | Aggressive intervals, specialized fluids |
| Light use, garage kept | Normal | Standard intervals, but watch time-based items |

Most manufacturers publish both "normal" and "severe/special conditions" schedules. Use the one that matches.

### 3. Choose Check-In Frequency
Ask how often they want to be asked about this vehicle's mileage/hours:

| Frequency | Best for |
|-----------|----------|
| **Weekly** | Dirt bikes, race vehicles, commercial/fleet, high-mileage daily drivers |
| **Every 2 weeks** | Active riders/drivers, vehicles with short service intervals |
| **Monthly** | Most cars and trucks (recommended default) |
| **Quarterly** | Seasonal vehicles, low-mileage, garage queens, stored boats |

Suggest a frequency based on the vehicle type and usage pattern, but let the user override.

### 4. Research the Service Schedule
**Look up manufacturer-recommended maintenance intervals** for that specific year/make/model/engine:
- Use web search to find the official maintenance schedule
- Check the owner's manual intervals
- Cross-reference with enthusiast forums for real-world advice
- Factor in the duty level from step 2

### 5. Build the Schedule File
Create `<workspace>/data/mechanic/<key>-schedule.json`:

```json
{
  "vehicle": {
    "year": 2021,
    "make": "Ford",
    "model": "F-350",
    "type": "truck",
    "engine": "6.7L Power Stroke V8 Turbo Diesel",
    "transmission": "10R140 10-Speed Automatic",
    "duty": "severe",
    "notes": "Tows fifth wheel RV"
  },
  "services": [
    {
      "id": "oil_filter",
      "name": "Engine Oil & Filter Change",
      "interval_miles": 7500,
      "interval_months": 6,
      "details": "Specific oil type, filter part number, capacity, and any special instructions.",
      "priority": "critical",
      "cost_diy": "$XX-XX",
      "cost_shop": "$XX-XX",
      "cost_dealer": "$XX-XX",
      "cost_note": "Optional note about related expensive repairs"
    }
  ]
}
```

**Required for every service item:**
- `id` — unique snake_case identifier
- `name` — human-readable name
- At least one interval: `interval_miles`, `interval_months`, `interval_hours`, or `interval_rides`
- `details` — specific parts, fluids, capacities, and any warnings
- `priority` — `critical`, `high`, `medium`, or `low`
- `cost_diy`, `cost_shop`, `cost_dealer` — estimated cost ranges

**Research costs:**
- Search for typical costs for each service on that specific vehicle
- DIY = parts cost only
- Shop = independent mechanic
- Dealer = manufacturer dealership
- Add `cost_note` for items where failure/repair is significantly more expensive than maintenance

### 6. Add to State
Add the vehicle to `state.json` under the `vehicles` object:

```json
{
  "<key>": {
    "label": "2021 Ford F-350 6.7L Power Stroke",
    "schedule_file": "<key>-schedule.json",
    "check_in_frequency": "monthly",
    "current_miles": 61450,
    "current_hours": null,
    "last_updated": "2026-01-26",
    "last_check_in": "2026-01-26",
    "vin": null,
    "vin_data": {
      "decoded": false
    },
    "business_use": false,
    "business_use_percent": 0,
    "mileage_history": [
      {"date": "2026-01-26", "miles": 61450, "source": "user_reported"}
    ],
    "service_history": [],
    "fuel_history": [],
    "warranties": [],
    "recalls": {
      "last_checked": null,
      "open_recalls": [],
      "completed_recalls": []
    },
    "emergency_info": {
      "vin": null,
      "insurance_provider": null,
      "policy_number": null,
      "roadside_assistance_phone": null,
      "tire_size_front": null,
      "tire_size_rear": null,
      "tire_pressure_front_psi": null,
      "tire_pressure_rear_psi": null,
      "oil_type": null,
      "oil_capacity": null,
      "coolant_type": null,
      "tow_rating_lbs": null,
      "gvwr_lbs": null,
      "key_fob_battery": null,
      "fuel_type": null,
      "fuel_tank_gallons": null,
      "notes": ""
    }
  }
}
```

**Key naming:** Use a short, memorable slug — `f350`, `civic`, `r1`, `rv`, `crf450`, `harley`, `bass_boat`, etc.

### 7. Update Cron Job
Update the cron job prompt to include the new vehicle. If this vehicle's frequency is higher than the current cron schedule, update the cron to fire at the higher frequency.

### 8. VIN Decode & Auto-Populate
If a VIN was provided, run the **VIN Decode** to auto-populate vehicle specs, emergency info fields, and the schedule file's vehicle section. Present the decoded info to the user for confirmation.

### 9. Run Initial Recall Check
If a VIN was provided, immediately check for open recalls (see **NHTSA Recall Monitoring**). If no VIN, check by make/model/year.

## Vehicle Types and Special Considerations

| Type | Track | Key Maintenance Items |
|------|-------|----------------------|
| **Car** | Miles | Oil, filters, brakes, tires, transmission, coolant |
| **Truck** | Miles | Same as car + diff fluids, transfer case (4WD), heavier brake wear if towing |
| **Motorcycle** | Miles | Oil, chain/sprockets, valve clearance, fork oil, brake fluid, coolant (liquid-cooled), tires (wear faster) |
| **Dirt Bike** | Hours + rides | Air filter (every ride!), oil (very frequent), valve clearance, suspension service, chain, coolant |
| **ATV/UTV** | Hours + miles | Similar to dirt bike + CV boots, belt (CVT), winch maintenance |
| **RV/Trailer** | Miles + months | Roof/sealant inspection, slide-outs, wheel bearings, electric brakes, tires (age-based), water system, generator, winterization |
| **Boat** | Hours | Oil, impeller, lower unit fluid, zincs/anodes, winterization, trailer bearings |
| **Fifth Wheel/Trailer** | Miles + months | No engine, but: bearings, brakes, tires, roof, seals, slides, plumbing, LP gas, seasonal prep |

### Interval Types
Services can use any combination of:
- `interval_miles` — odometer-based
- `interval_hours` — engine/usage hours (generators, dirt bikes, boats)
- `interval_months` — time-based (everything degrades with age)
- `interval_rides` — per-use (e.g., dirt bike air filter = every ride)

**Whichever interval is reached first triggers the service.**

---

## VIN Decode & Auto-Population

When a user provides a VIN (during vehicle setup or later), decode it using the free NHTSA VPIC API to automatically look up and store vehicle specifications.

### NHTSA VPIC API (VIN Decoder)

**Endpoint:** `https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{VIN}?format=json`

No API key required. Free and unlimited.

**Example:**
```
GET https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/1FT8W3BT0MED12345?format=json
```

### Key Fields to Extract

The API returns a `Results` array with one object containing ~140+ fields. Extract and map these:

| VPIC Field | Maps To | Notes |
|------------|---------|-------|
| `ModelYear` | `vin_data.year` | Vehicle year |
| `Make` | `vin_data.make` | Manufacturer |
| `Model` | `vin_data.model` | Model name |
| `Trim` | `vin_data.trim` | Trim level (Lariat, XLT, etc.) |
| `BodyClass` | `vin_data.body_class` | Pickup, SUV, Motorcycle, etc. |
| `DriveType` | `vin_data.drive_type` | 4WD, AWD, RWD, FWD |
| `DisplacementL` | `vin_data.displacement_l` | Engine displacement in liters |
| `EngineCylinders` | `vin_data.cylinders` | Number of cylinders |
| `FuelTypePrimary` | `vin_data.fuel_type` | Gasoline, Diesel, Electric, etc. |
| `EngineModel` | `vin_data.engine` | Combine with displacement for label |
| `TransmissionStyle` | `vin_data.transmission` | Automatic, Manual, CVT |
| `TransmissionSpeeds` | (append to transmission) | "10-Speed Automatic" |
| `Doors` | `vin_data.doors` | Number of doors |
| `GVWR` | `vin_data.gvwr_class` | Gross Vehicle Weight Rating class |
| `WheelBaseShort` | `vin_data.wheel_base` | Wheelbase in inches |
| `BedLengthIN` | `vin_data.bed_length` | Truck bed length (if applicable) |
| `PlantCountry` | `vin_data.plant_country` | Assembly country |
| `PlantCity` | `vin_data.plant_city` | Assembly city |

**Note:** Many fields return empty strings `""` if not applicable. Only store non-empty values.

### VIN Data Storage

Store decoded data in the vehicle's `vin_data` object in `state.json`:

```json
{
  "vin_data": {
    "decoded": true,
    "decoded_date": "2026-01-27",
    "year": 2021,
    "make": "Ford",
    "model": "F-350",
    "trim": "Lariat",
    "body_class": "Pickup",
    "drive_type": "4WD",
    "engine": "6.7L Power Stroke V8 Turbo Diesel",
    "displacement_l": 6.7,
    "cylinders": 8,
    "fuel_type": "Diesel",
    "transmission": "10-Speed Automatic",
    "doors": 4,
    "gvwr_class": "Class 3",
    "bed_length": "8 ft",
    "wheel_base": "176 in",
    "plant_country": "United States",
    "plant_city": "Louisville",
    "raw_response": {}
  }
}
```

Store `raw_response` as the full VPIC result object for reference — it contains additional fields that may be useful later (e.g., `AirBagLocFront`, `SeatBeltsAll`, `TPMS`, `ActiveSafetySysNote`, etc.).

If `vin_data.decoded` is `false` or missing, the VIN hasn't been decoded yet.

### Auto-Population Workflow

When a VIN is decoded:

1. **Update `vin_data`** — store all decoded fields
2. **Update `label`** — build from decoded year/make/model/engine (e.g., "2021 Ford F-350 6.7L Power Stroke")
3. **Update `emergency_info`** — auto-fill fields that can be derived:
   - `fuel_type` from `FuelTypePrimary`
   - `gvwr_lbs` from `GVWR` (parse weight class to approximate lbs)
4. **Update schedule file** — populate the `vehicle` section with decoded specs
5. **Present to user** — show what was decoded, confirm accuracy, ask about anything the VIN couldn't tell us (usage pattern, duty level, insurance, etc.)

### When to Decode

| Trigger | Action |
|---------|--------|
| New vehicle added with VIN | Decode immediately, auto-populate |
| User provides VIN for existing vehicle | Decode, backfill `vin_data` and any empty fields |
| User says "look up my VIN" | Decode and display specs |
| User changes/corrects VIN | Re-decode and update |

### Adding VIN Later

If a vehicle was added without a VIN and the user provides one later:
1. Decode the VIN
2. Store in `vin_data`
3. Update `vin` field
4. Backfill any empty `emergency_info` fields
5. Update `label` if the decoded info is more specific
6. Run an immediate recall check with the new VIN
7. Confirm what was updated

### VIN Decode Presentation Format

When presenting decoded VIN data to the user:
```
🔍 VIN Decoded — [VIN]
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Vehicle
Year: [year] | Make: [make] | Model: [model]
Trim: [trim] | Body: [body_class]
Drive: [drive_type] | Doors: [doors]

🔧 Powertrain
Engine: [engine] ([displacement]L, [cylinders] cyl)
Fuel: [fuel_type]
Transmission: [transmission]

📏 Specs
GVWR: [gvwr_class]
Wheel Base: [wheel_base]
Bed Length: [bed_length] (if truck)

🏭 Built in [plant_city], [plant_country]
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Limitations
- **VPIC is NHTSA data** — best for US-market vehicles. Import/foreign-market VINs may have incomplete data.
- **Trailers and RVs** — VIN decode may return limited data for trailers, fifth wheels, and RVs since they're built by different manufacturers with varying VIN encoding.
- **Motorcycles and powersports** — coverage varies. Japanese brands (Honda, Yamaha, Kawasaki, Suzuki) generally decode well. Smaller manufacturers may not.
- **Pre-1981 vehicles** — VINs weren't standardized until 1981. Older VINs won't decode.
- If decode returns sparse data, fall back to manual entry and web search for specs.

---

## NHTSA Recall Monitoring

Monitor for open recalls on all tracked vehicles using the free NHTSA API (no API key required).

### API Endpoints
- **By make/model/year:** `https://api.nhtsa.dot.gov/recalls/recallsByVehicle?make=Ford&model=F-350&modelYear=2021`
- **By VIN (more precise):** `https://api.nhtsa.dot.gov/recalls/recallsByVin?vin=XXXXX`

If a VIN is stored, prefer the VIN-based lookup. Otherwise fall back to make/model/year.

### Recall Data Storage
Per vehicle in state.json:
```json
{
  "recalls": {
    "last_checked": "2026-01-26",
    "open_recalls": [
      {
        "nhtsa_id": "26V-123",
        "component": "FUEL SYSTEM",
        "summary": "Fuel line may crack under pressure",
        "consequence": "Fuel leak, fire risk",
        "remedy": "Dealer will replace fuel line at no cost",
        "date_reported": "2025-12-01",
        "status": "open"
      }
    ],
    "completed_recalls": [
      {
        "nhtsa_id": "24V-456",
        "component": "ELECTRICAL",
        "summary": "Battery cable may corrode",
        "date_completed": "2025-06-15",
        "notes": "Done at dealer"
      }
    ]
  }
}
```

### When to Check
- **Monthly cron:** Include recall checks in the mileage check cron. Check recalls for all vehicles monthly regardless of their check-in frequency.
- **On vehicle add:** Check immediately when a new vehicle is added.
- **On demand:** User asks "any recalls on my truck?"

### Recall Report Format
Include in service review output:
```
⚠️ OPEN RECALLS
- [NHTSA ID] — [Component]: [Summary]
  Remedy: [What the dealer will do]
  ⚡ Contact your dealer to schedule this recall service (free)
```

When a user reports completing a recall, move it from `open_recalls` to `completed_recalls` with the completion date.

---

## Fuel / MPG Tracking

Track fuel fill-ups to monitor fuel economy, detect mechanical issues early, and track fuel spending.

### Logging a Fill-Up
When user says "filled up", "got gas/diesel", or reports a fill-up:
1. Capture: **date**, **gallons**, **cost** (total or price per gallon), **odometer reading**
2. Calculate MPG: `(current_odometer - previous_odometer) / gallons`
3. Append to the vehicle's `fuel_history` array
4. Check for MPG anomalies

### Fuel History Entry
```json
{
  "date": "2026-01-20",
  "gallons": 32.5,
  "cost": 108.55,
  "price_per_gallon": 3.34,
  "odometer": 61300,
  "mpg": 14.2,
  "partial_fill": false,
  "notes": ""
}
```

### MPG Calculations
- **Per fill-up MPG:** `(current_odometer - previous_fill_odometer) / gallons` (skip if previous fill was partial)
- **Rolling average:** Average of last 10 fill-ups (or all if fewer than 10)
- **Trend:** Compare last 3 fill-ups to rolling average

### Anomaly Detection
If a fill-up MPG is **more than 15% below the rolling average**, flag it:
```
⚠️ MPG Alert — [Vehicle]
Last fill-up: 10.5 MPG (your average is 14.2 MPG)
26% below your rolling average — this could indicate:
- Tire pressure issues
- Air filter needs replacement
- Fuel system issue
- Change in driving conditions (heavy towing, headwinds)
- Mechanical problem developing

Check tire pressures first, then review recent driving conditions.
```

### Fuel Report Format
When asked "how's my fuel economy?" or "MPG report":
```
⛽ Fuel Report — [Vehicle]
Last fill-up: [X] MPG on [date]
Rolling average: [X] MPG (last 10 fills)
Trend: [improving/stable/declining]
Total fuel cost (YTD): $[X]
Total gallons (YTD): [X]
Average cost per gallon: $[X]
```

### Partial Fills
If the user didn't fill up completely, mark `partial_fill: true`. Skip that entry for MPG calculation (the math won't be accurate), but still track cost and gallons.

---

## Actual Cost Tracking

Track what the user actually pays for maintenance to build accurate spending records.

### Capturing Costs
When a user logs a completed service:
1. After confirming the service details, ask: **"What did you end up paying?"** (or accept if they volunteered it)
2. Store as `actual_cost` in the service_history entry
3. If they don't know or don't want to share, leave it null — don't block the log

### Service History Entry (with cost)
```json
{
  "service_id": "oil_filter",
  "date": "2025-11-15",
  "miles": 58000,
  "hours": null,
  "notes": "Full synthetic, Motorcraft filter",
  "actual_cost": 125.00,
  "cost_type": "shop",
  "provider": {
    "id": "jims_diesel",
    "name": "Jim's Diesel Repair"
  }
}
```

`cost_type` values: `diy`, `shop`, `dealer`, `warranty`, `recall` (free)

### Spending Analysis
Track and report on request:
- **Per vehicle, per year:** "You've spent $X on the F-350 this year"
- **Actual vs estimated:** Compare `actual_cost` to the schedule's cost estimates
- **Category breakdown:** Group by service type (oil changes, filters, tires, etc.)
- **All-time total:** Total maintenance spending per vehicle

### Annual Summary
When asked or at year-end:
```
💰 [Year] Maintenance Summary — [Vehicle]
Total spent: $[X]
Services performed: [count]
Biggest expense: [service] — $[X]
Average cost per service: $[X]
vs. Estimated: $[X] ([over/under] by [X]%)
```

---

## Warranty Tracking

Track warranties to know what's covered and get alerts before they expire.

### Warranty Entry Structure
```json
{
  "type": "factory_powertrain",
  "provider": "Ford",
  "start_date": "2021-03-15",
  "end_date": "2026-03-15",
  "start_miles": 0,
  "end_miles": 60000,
  "coverage_details": "Engine, transmission, transfer case, driveshaft, axle assemblies",
  "status": "active",
  "contact_phone": "1-800-392-3673",
  "claim_number": null,
  "notes": ""
}
```

### Warranty Types
| Type | Typical Coverage |
|------|-----------------|
| `factory_bumper_to_bumper` | Everything except wear items, shortest duration |
| `factory_powertrain` | Engine, transmission, drivetrain — longer duration |
| `factory_corrosion` | Body rust-through — usually 5+ years |
| `factory_emissions` | Emissions components — federally mandated 8yr/80k for major components |
| `extended` | Third-party or manufacturer extended warranty |
| `parts_warranty` | Specific parts from a shop/dealer (e.g., "new alternator, 2yr warranty") |
| `labor_warranty` | Shop's labor guarantee on a specific repair |

### Expiration Alerts
Check warranties during every service review. Alert when:
- **Within 3 months** of end_date, OR
- **Within 3,000 miles** of end_miles (whichever comes first)

Alert format:
```
⚠️ WARRANTY EXPIRING SOON
[Vehicle] — [Warranty type] from [Provider]
Expires: [date] or [miles] miles (whichever first)
Remaining: ~[X] months / ~[X] miles
Coverage: [details]
💡 Schedule any warranty-covered concerns before expiration!
```

### Warranty Coverage Check
When user asks "is this covered under warranty?" or when flagging a due service:
1. Check all active warranties for the vehicle
2. Match the service type to warranty coverage
3. If potentially covered: "This may be covered under your [warranty type] from [provider] (expires [date]). Contact them before paying out of pocket."

### Status Values
- `active` — currently in effect
- `expiring_soon` — within alert threshold
- `expired` — past end date or end miles
- `claimed` — warranty claim was filed

---

## Pre-Trip / Seasonal Checklists

Generate vehicle-specific checklists when a trip or seasonal change is mentioned.

### Trigger Phrases
Activate when user says things like:
- "I'm heading on a trip" / "road trip" / "going to [location]"
- "towing this weekend" / "pulling the RV to [place]"
- "getting ready for winter" / "time to winterize"
- "spring is coming" / "time to de-winterize"
- "going off-road this weekend" / "trail ride"

### Checklist Generation
Build the checklist by combining:

1. **Overdue/due-soon services** — Pull from service review for this vehicle
2. **Weather at destination** — Check forecast if location given (hot, cold, rain, snow, altitude)
3. **Trip-type items** — Based on what they're doing
4. **Seasonal items** — Based on current date and location

### Towing Checklist (Truck + Trailer/RV)
```
🚛 Pre-Tow Checklist — [Truck] + [Trailer/RV]

TRUCK:
□ Engine oil level
□ Coolant level
□ DEF level (diesel)
□ Tire pressures (loaded spec: front [X] psi, rear [X] psi)
□ Brake controller connected and tested
□ Transmission temp gauge working
□ All lights working
□ Mirrors adjusted for towing

HITCH/CONNECTION:
□ Fifth wheel / gooseneck / ball mount secured
□ Pin box / kingpin locked (verify with tug test)
□ Safety chains crossed under tongue
□ Breakaway cable attached
□ 7-pin connector — test all lights (brake, turn, running, reverse)
□ Breakaway battery charged

TRAILER/RV:
□ Tire pressures (spec: [X] psi) — check age on sidewall
□ Wheel lug torque (spec: [X] ft-lbs)
□ Slides fully retracted and locked
□ Awning secured
□ Fridge set to travel mode (or propane off)
□ All compartments latched
□ Stabilizer jacks fully up
□ Roof vents closed
□ TV antenna down
□ Water heater bypass (if applicable)
□ LP gas tank valve position (check local laws for travel)
□ Cargo secured inside (open fridge, cabinets after arrival)

OVERDUE/DUE SERVICES:
[List any from service review]
```

### Seasonal Checklists

**Pre-Winter / Winterization:**
- Antifreeze protection level (test with hydrometer)
- Battery load test (cold reduces capacity 30-50%)
- Wiper blades and washer fluid (cold-rated)
- Tire condition (all-season or winter tires?)
- Block heater working (diesel trucks)
- RV: Full winterization procedure (blow out lines, RV antifreeze, water heater drain, bypass)
- Boat: Winterize engine, fog cylinders, stabilize fuel, drain water systems

**Pre-Summer / De-Winterization:**
- AC system check (run it before you need it)
- Coolant level and condition
- RV: De-winterize water system, sanitize tanks, check AC units
- Check tire pressures (heat increases pressure)
- Inspect belts and hoses (heat accelerates wear)

**Pre-Trip (General):**
- All fluid levels
- Tire pressures and condition
- Lights and signals
- Brakes (visual or recent service)
- Wiper blades
- Emergency kit (jumper cables, flashlight, first aid)
- Registration and insurance current

---

## Mileage Projection

Calculate driving pace and project when future services will come due.

### Calculation
Requires **2+ data points** in `mileage_history` at least 14 days apart.

```
average_miles_per_month = (latest_miles - earliest_miles) / months_between_readings
```

Use the full history for a stable average, but weight recent data more heavily if there's a significant change in driving pattern.

### Service Date Projection
For each service:
1. Calculate miles remaining: `next_due_miles - current_miles`
2. Project months: `miles_remaining / average_miles_per_month`
3. Project date: `today + projected_months`
4. Also check time-based interval independently

Include in service review:
```
📅 Projected Service Dates
- Oil Change: ~[Month Year] (at ~[X] miles)
- Fuel Filters: ~[Month Year] (at ~[X] miles)
- Trans Fluid: ~[Month Year] (at ~[X] miles)
```

### Budget Projection
When asked or included in reviews:
```
💰 Next 6-Month Budget Forecast — [Vehicle]
At [X] miles/month, expect:
- Oil change (~[Month]): $[X]
- Fuel filters (~[Month]): $[X]
- Cabin air filter (~[Month]): $[X]
Total estimated: $[X]
```

### Insufficient Data
If fewer than 2 data points or readings are too close together:
- Note: "Need more mileage history to project dates — will be available after next check-in"
- Still show mile-based estimates without dates

---

## Service Provider Tracking

Track where services are performed for easy reference and provider management.

### Capturing Provider Info
When logging a completed service, optionally ask:
- **Shop name** (or "same as last time" / "DIY")
- **Location** (city/address)
- **Phone number**
- **Satisfaction rating** (1-5)
- **Parts warranty** (months)
- **Labor warranty** (months)

Don't make this burdensome — if they just say "got my oil changed", log the service first, then casually ask where. Skip if they seem uninterested.

### Provider Storage
Providers are stored in two places:

1. **Global `providers` array** in state.json root — reusable across vehicles:
```json
{
  "id": "jims_diesel",
  "name": "Jim's Diesel Repair",
  "location": "123 Main St, Mesa, AZ",
  "phone": "480-555-1234",
  "specialties": ["diesel", "trucks"],
  "rating": 5,
  "notes": "Great with Power Stroke engines"
}
```

2. **Per service_history entry** — reference by `id` plus any service-specific warranty:
```json
{
  "provider": {
    "id": "jims_diesel",
    "name": "Jim's Diesel Repair",
    "parts_warranty_months": 12,
    "labor_warranty_months": 6
  }
}
```

### Provider Queries
Handle questions like:
- "Where did I get my last oil change?" → Search service_history for most recent oil_filter entry, return provider
- "What shop did I use for the transmission service?" → Search by service_id
- "Show me all services at Jim's" → Filter service_history by provider.id
- "What's Jim's phone number?" → Look up in providers array
- "Same shop as last time" → Use the provider from the most recent service_history entry

---

## Tax Deduction Integration

For vehicles flagged as business-use, help track deductible maintenance expenses.

### Configuration
Per vehicle in state.json:
```json
{
  "business_use": true,
  "business_use_percent": 50
}
```

If `business_use` is `true` and no percentage is set, assume 100%.

### Deduction Tracking
When a service is completed with an `actual_cost` on a business-use vehicle:

1. Calculate deductible portion: `actual_cost × (business_use_percent / 100)`
2. Note it to the user:
   ```
   💼 Tax Note: This $450 trans fluid service is 50% business use.
   Deductible amount: $225.00 (vehicle maintenance expense)
   ```
3. Suggest logging to the tax-professional skill:
   ```
   Want me to log this to your tax deductions? 
   → $225.00 as vehicle maintenance expense
   ```

### Integration with Tax-Professional Skill
If the user confirms, reference `skills/tax-professional/SKILL.md` and log to `data/tax-professional/YYYY-expenses.json`:
```json
{
  "date": "2026-01-15",
  "category": "vehicle_maintenance",
  "description": "Trans fluid service — F-350 (50% business use)",
  "amount": 225.00,
  "vehicle": "f350",
  "full_cost": 450.00,
  "business_percent": 50,
  "receipt": false
}
```

### Annual Tax Summary
On request or at tax time:
```
💼 [Year] Business Vehicle Deductions — [Vehicle]
Total maintenance costs: $[X]
Business use: [X]%
Deductible amount: $[X]
Services included: [count] services
```

---

## Emergency Info Card

Store and quickly retrieve critical vehicle information for roadside emergencies, parts lookup, or quick reference.

### Emergency Info Structure
Per vehicle in state.json:
```json
{
  "emergency_info": {
    "vin": "1FT8W3BT0MED12345",
    "insurance_provider": "State Farm",
    "policy_number": "SF-123456789",
    "roadside_assistance_phone": "1-800-555-1234",
    "tire_size_front": "275/70R18",
    "tire_size_rear": "275/70R18",
    "tire_pressure_front_psi": 65,
    "tire_pressure_rear_psi": 80,
    "oil_type": "15W-40 CK-4 Full Synthetic",
    "oil_capacity": "15 quarts",
    "coolant_type": "Motorcraft Orange VC-3DIL-B",
    "def_type": "API certified DEF",
    "trans_fluid": "Motorcraft Mercon ULV",
    "tow_rating_lbs": 20000,
    "gvwr_lbs": 14000,
    "gcwr_lbs": 37000,
    "payload_lbs": 4300,
    "key_fob_battery": "CR2450",
    "fuel_type": "Diesel (Ultra Low Sulfur)",
    "fuel_tank_gallons": 48,
    "lug_nut_torque_ft_lbs": 165,
    "jack_points": "Frame rails, front and rear",
    "notes": ""
  }
}
```

### Quick Access Queries
Respond instantly to:
- "What's my VIN?" → Return VIN
- "What are my truck's tire specs?" → Tire sizes and pressures
- "What oil does my truck take?" → Oil type and capacity
- "Insurance info?" → Provider, policy number, phone
- "Roadside assistance number?" → Phone number
- "What's my tow rating?" → Tow rating, GVWR, GCWR
- "Key fob battery?" → Battery type
- "Lug nut torque?" → Torque spec

### Emergency Card Format
When asked for "emergency info" or "vehicle card":
```
🚨 Emergency Info — [Vehicle Label]
━━━━━━━━━━━━━━━━━━━━━━━━━━━
VIN: [vin]
Insurance: [provider] — Policy #[number]
Roadside: [phone]

🔧 Specs
Tires: F:[size] R:[size]
Pressure: F:[X]psi R:[X]psi
Oil: [type] ([capacity])
Coolant: [type]
Fuel: [type] ([tank] gal)
Key fob battery: [type]

📏 Ratings
Tow: [X] lbs | GVWR: [X] lbs
GCWR: [X] lbs | Payload: [X] lbs
Lug torque: [X] ft-lbs
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Population
When adding a new vehicle, collect what's available. Many specs can be researched from the year/make/model. Let the user fill in personal info (insurance, roadside number) over time. Fields can be null until populated.

---

## Cost Per Mile Analysis

Calculate total cost of vehicle ownership on a per-mile basis.

### Calculations
Requires mileage history with at least 2 data points.

```
total_miles_driven = latest_miles - earliest_miles (from mileage_history)

Maintenance cost per mile = total_actual_costs / total_miles_driven
Fuel cost per mile = total_fuel_cost / total_miles_driven
Total operating cost per mile = (total_actual_costs + total_fuel_cost) / total_miles_driven
```

### Report Format
When asked "cost per mile" or "operating cost":
```
📊 Cost Per Mile — [Vehicle]
Period: [earliest date] to [latest date] ([X] miles driven)

Maintenance only: $[X.XX]/mile
Fuel only: $[X.XX]/mile (if fuel tracking active)
Total operating: $[X.XX]/mile

💡 National averages (approximate):
Cars: ~$0.10/mi maintenance, ~$0.12/mi fuel
Trucks: ~$0.14/mi maintenance, ~$0.20/mi fuel (diesel)
Heavy-duty diesel (towing): ~$0.18/mi maintenance, ~$0.25/mi fuel
```

### Fleet Overview
If tracking multiple vehicles, show a comparison:
```
📊 Fleet Cost Per Mile
[Vehicle 1]: $[X.XX]/mi (maintenance) | $[X.XX]/mi (total)
[Vehicle 2]: $[X.XX]/mi (maintenance) | $[X.XX]/mi (total)
Fleet average: $[X.XX]/mi
```

### Notes
- Only include services with `actual_cost` recorded (skip nulls)
- If no fuel data, show maintenance-only
- Warn if data period is short (<3 months or <1,000 miles): "Limited data — will become more accurate over time"
- Cost per mile naturally decreases as expensive one-time services are amortized over more miles

---

## Mileage Check (Cron-Triggered)

A single cron job runs **weekly** (the highest possible frequency) and checks which vehicles are due for a check-in based on their individual `check_in_frequency` and `last_check_in` date. It also performs monthly recall checks.

> Prompt: "Mechanic skill: mileage check"

When this fires:
1. Read `<workspace>/data/mechanic/state.json`
2. For each vehicle, check if it's due for a check-in:
   - Compare `last_check_in` date against `check_in_frequency`
   - **Weekly**: due if 7+ days since last check-in
   - **Biweekly**: due if 14+ days
   - **Monthly**: due if 30+ days
   - **Quarterly**: due if 90+ days
3. **Monthly recall check**: If 30+ days since any vehicle's `recalls.last_checked`, fetch latest recalls from NHTSA API and update state
4. If **no vehicles are due for check-in AND no new recalls found**, reply with `HEARTBEAT_OK` (skip silently)
5. If vehicles are due, ask for current readings on **only the due vehicles**
6. If new recalls found, include them in the message even if no vehicles are due for mileage check-in
7. Update state and `last_check_in` when they respond
8. Run a **Service Review** for the updated vehicles (includes warranty alerts, projections, recalls)

### Mileage Check Setup

Create a single cron job that runs **weekly**. It will internally filter which vehicles are due. Check `<workspace>/USER.md` for timezone.

**Cron expression:** `0 17 * * 0` (every Sunday at 5pm in user's timezone)

**Cron job config:**
- **Session:** isolated with delivery to their chat channel
- **Prompt:** Read the mechanic skill, load state from `data/mechanic/state.json`. Check each vehicle's `check_in_frequency` and `last_check_in` to determine which are due. Also check recalls if 30+ days since last recall check. If none are due and no new recalls, reply HEARTBEAT_OK. Otherwise, ask for current readings on the due vehicles only, report any new recalls, then run a service review with costs, warranty alerts, and projections. Be conversational.

### Changing Frequency

The user can change frequency per vehicle at any time:
- "Check my dirt bike weekly" → update that vehicle's `check_in_frequency`
- "Ask about the truck less often" → switch to quarterly
- "Change all vehicles to monthly" → update all

Update the vehicle's `check_in_frequency` in `state.json` and confirm the change.

## Mileage/Hours Update

When the user reports mileage or hours (in any context, not just monthly):

1. Update the vehicle's `current_miles` and/or `current_hours`
2. Set `last_updated` to today
3. Append to `mileage_history`:
```json
{"date": "YYYY-MM-DD", "miles": <value>, "source": "user_reported"}
```
4. Run a **Service Review**

## Service Review

After any mileage/hours update, analyze all services from the vehicle's schedule file.

### For each service item:
1. Find the **last time this service was done** from `service_history` (match by `service_id`)
2. If never done, assume done at **mile 0 / hour 0** (vehicle acquisition)
3. Calculate against all applicable intervals:
   - `miles_since_service` vs `interval_miles`
   - `months_since_service` vs `interval_months`
   - `hours_since_service` vs `interval_hours`
4. Categorize:
   - **🔴 OVERDUE**: Exceeded ANY interval
   - **🟡 DUE SOON**: Within 15% of ANY interval
   - **🟢 OK**: Not yet due

### Report Format

**Full report (when issues found):**
```
🔧 Vehicle Service Report

━━━ [Vehicle Label] @ [miles] mi ━━━

⚠️ OPEN RECALLS
- [NHTSA ID] — [Component]: [Summary]
  Remedy: [description] (FREE at dealer)

⚠️ WARRANTY ALERTS
- [Warranty type] from [Provider] — expires [date] or [miles] mi
  [X] months / [X] miles remaining

🔴 OVERDUE
- [service] — [X] miles/months overdue
  💰 DIY: $X | Shop: $X | Dealer: $X
  [💼 [X]% deductible] (if business use)

🟡 DUE SOON
- [service] — due in ~[X] miles/months
  💰 DIY: $X | Shop: $X | Dealer: $X

📅 PROJECTED SCHEDULE (next 6 months)
- [service] — ~[Month Year] at ~[X] mi ($[X] est.)
- [service] — ~[Month Year] at ~[X] mi ($[X] est.)
Total upcoming (6mo): ~$[X]

⛽ FUEL ECONOMY
Current: [X] MPG | Average: [X] MPG | Trend: [stable/improving/declining]
[⚠️ MPG Alert if applicable]

💰 SPENDING (YTD)
Maintenance: $[X] | Fuel: $[X] | Total: $[X]
Cost per mile: $[X.XX]

[Repeat for each vehicle]

🟢 [count] services current across all vehicles
```

**All clear (brief):**
```
🔧 All vehicles current ✅
[Vehicle] @ [mi] — next: [soonest service] at ~[miles] (~[Month])
No open recalls | Warranties current
```

**When multiple services are due at once**, provide a bundled total estimate and suggest combining them in one shop visit.

### Conditional Sections
Only include sections that have relevant data:
- Skip recalls section if no open recalls
- Skip warranty alerts if none expiring soon
- Skip fuel economy if no fuel_history data
- Skip projections if insufficient mileage data
- Skip spending if no actual_cost data
- Skip tax note if vehicle isn't business-use

## Logging Completed Services

When the user says they've done a service (e.g., "just got my oil changed", "did the fuel filters at 65k"):

1. Identify which vehicle and which service
2. Ask what they paid (casually — "What'd that run you?" / "How much was it?")
3. Optionally capture provider ("Where'd you take it?" / "Same shop as last time?")
4. Add to that vehicle's `service_history`:
```json
{
  "service_id": "<matching id>",
  "date": "YYYY-MM-DD",
  "miles": <mileage_at_service>,
  "hours": <hours_if_applicable>,
  "notes": "<any details the user mentions>",
  "actual_cost": <amount_or_null>,
  "cost_type": "shop",
  "provider": {
    "id": "<provider_id>",
    "name": "<provider_name>",
    "parts_warranty_months": null,
    "labor_warranty_months": null
  }
}
```
5. If business-use vehicle, note the deductible portion
6. Offer to log to tax-professional if applicable
7. Confirm what was logged
8. Recalculate next due date for that service

## Ad-Hoc Queries

Handle questions about any tracked vehicle. If ambiguous, ask which vehicle.

**Examples:**
- "When's my next oil change?" → Check the relevant vehicle(s)
- "What oil does my truck take?" → Reference schedule details or emergency_info
- "What maintenance do I need?" → Full review, all vehicles
- "I just hit 70,000 miles" → Update mileage, run review
- "Got new tires at 61k" → Log service, track rotation from there
- "I just got a new [vehicle]" → Walk through adding it
- "How much would an oil change cost?" → Reference cost estimates
- "What's the most urgent thing?" → Prioritize across all vehicles
- "Any recalls on my truck?" → Check NHTSA API
- "How's my fuel economy?" → MPG report
- "How much have I spent this year?" → Spending summary
- "Is my warranty still good?" → Check warranty status
- "Is this covered under warranty?" → Match service to active warranties
- "I'm heading on a road trip" → Pre-trip checklist
- "When will my trans fluid be due?" → Mileage projection
- "Where did I get my last oil change?" → Provider lookup
- "What's my VIN?" → Emergency info
- "Look up my VIN" / "Decode my VIN" → Run VIN decode, show specs
- "Here's my VIN: [VIN]" → Decode, store, auto-populate, run recall check
- "What are my tire specs?" → Emergency info
- "Cost per mile?" → Operating cost analysis
- "How much will I spend on maintenance in the next 6 months?" → Budget projection

## Environmental Awareness

Check `<workspace>/USER.md` for the user's location and use it to tailor advice:

**Hot climates (desert, southern states):**
- Battery life shortened significantly by heat
- Tire UV damage — recommend tire covers for parked vehicles
- Coolant system more stressed
- Rubber components (belts, hoses, seals) degrade faster
- Mud daubers/wasps in vents and exhaust (RVs especially)

**Cold climates (northern states, mountains):**
- Winterization critical for RVs and boats
- Battery capacity reduced in cold
- Check antifreeze protection level
- Furnace/heating system inspection before cold season

**Dusty/off-road environments:**
- Engine and cabin air filters need more frequent inspection
- Generator air filters (RVs)
- Check CV boots (ATVs/UTVs)

**Coastal/marine environments:**
- Corrosion concerns
- More frequent undercarriage wash
- Check electrical connections

## Cost Estimates

**Always include cost estimates** when flagging overdue or due-soon services:
- **DIY** — parts cost only
- **Shop** — independent mechanic / specialty shop
- **Dealer** — manufacturer dealership

Include any `cost_note` warnings about expensive failure scenarios.

When presenting a batch of services, provide a **total estimate** for bundling them in one shop visit.

## Important General Notes

- **Transmission flushes** — Many modern transmissions (especially Ford 10R series, CVTs) should ONLY be drain-and-fill, never flushed. Always check manufacturer recommendation.
- **RV roofs** — Water intrusion is the #1 RV killer. Always emphasize sealant and roof inspections.
- **Tire age** — Tires should be replaced at 5-6 years regardless of tread depth, especially RV/trailer tires.
- **Severe duty** — If someone tows, hauls, drives off-road, or operates in extreme temps, they're almost always on the severe/special conditions schedule whether they realize it or not.
- **Part numbers** — Include OEM part numbers in schedule details. Users can then find equivalent aftermarket parts.
- **Seasonal items** — Flag winterization, de-winterization, and seasonal prep based on the user's location and time of year.
- **Generator hours** — Track separately from vehicle miles. Generators have their own service intervals.
- **Breakaway batteries** (trailers) — Often forgotten. Include in trailer/RV inspections.
- **Recall completions** — Always free at the dealer. Never pay for a recall repair.
- **Warranty work** — Document everything. Keep receipts. Note warranty claim numbers in service history.
- **Fuel tracking consistency** — Always fill to the same level (full) for accurate MPG calculations. Mark partial fills.
