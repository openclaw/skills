# WHOOP API Reference

Base URL: `https://api.prod.whoop.com`

All endpoints require an `Authorization: Bearer {access_token}` header.

## User Endpoints

### GET /v1/user/profile/basic
Get basic user profile information.

**Scope**: `read:profile`

**Response**:
```json
{
  "user_id": 10129,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Smith"
}
```

### GET /v1/user/body_measurement
Get user body measurements.

**Scope**: `read:body_measurement`

**Response**:
```json
{
  "height_meter": 1.8288,
  "weight_kilogram": 90.7185,
  "max_heart_rate": 200
}
```

## Recovery Endpoints

### GET /v1/recovery
Get all recovery records (paginated).

**Scope**: `read:recovery`

**Query Parameters**:
- `start` (string, ISO 8601): Filter by start time (inclusive)
- `end` (string, ISO 8601): Filter by end time (exclusive)
- `limit` (integer, max 25): Records per page
- `nextToken` (string): Pagination cursor

**Response**:
```json
{
  "records": [
    {
      "cycle_id": 93845,
      "sleep_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": 10129,
      "created_at": "2022-04-24T11:25:44.774Z",
      "updated_at": "2022-04-24T14:25:44.774Z",
      "score_state": "SCORED",
      "score": {
        "user_calibrating": false,
        "recovery_score": 44,
        "resting_heart_rate": 64,
        "hrv_rmssd_milli": 31.813562,
        "spo2_percentage": 95.6875,
        "skin_temp_celsius": 33.7
      }
    }
  ],
  "next_token": "MTIzOjEyMzEyMw"
}
```

**Score Fields**:
- `recovery_score`: 0-100 readiness score
- `resting_heart_rate`: Morning baseline HR in bpm
- `hrv_rmssd_milli`: Heart rate variability in milliseconds
- `spo2_percentage`: Blood oxygen percentage
- `skin_temp_celsius`: Skin temperature deviation from baseline
- `user_calibrating`: Whether user is in calibration period

### GET /v1/cycle/{cycleId}/recovery
Get recovery for a specific cycle.

**Scope**: `read:recovery`

**Response**: Same as single record from collection endpoint.

## Sleep Endpoints

### GET /v1/sleep
Get all sleep records (paginated).

**Scope**: `read:sleep`

**Query Parameters**: Same as recovery endpoint.

**Response**:
```json
{
  "records": [
    {
      "id": "ecfc6a15-4661-442f-a9a4-f160dd7afae8",
      "cycle_id": 93845,
      "user_id": 10129,
      "created_at": "2022-04-24T11:25:44.774Z",
      "updated_at": "2022-04-24T14:25:44.774Z",
      "start": "2022-04-24T02:25:44.774Z",
      "end": "2022-04-24T10:25:44.774Z",
      "timezone_offset": "-05:00",
      "nap": false,
      "score_state": "SCORED",
      "score": {
        "stage_summary": {
          "total_in_bed_time_milli": 30272735,
          "total_awake_time_milli": 1403507,
          "total_light_sleep_time_milli": 14905851,
          "total_slow_wave_sleep_time_milli": 6630370,
          "total_rem_sleep_time_milli": 5879573,
          "sleep_cycle_count": 3,
          "disturbance_count": 12
        },
        "sleep_needed": {
          "baseline_milli": 27395716,
          "need_from_sleep_debt_milli": 352230,
          "need_from_recent_strain_milli": 208595,
          "need_from_recent_nap_milli": -12312
        },
        "respiratory_rate": 16.11328125,
        "sleep_performance_percentage": 98,
        "sleep_consistency_percentage": 90,
        "sleep_efficiency_percentage": 91.69533848
      }
    }
  ],
  "next_token": "MTIzOjEyMzEyMw"
}
```

**Score Fields**:
- `stage_summary`: Time spent in each sleep stage (milliseconds)
  - `total_in_bed_time_milli`: Total time in bed
  - `total_awake_time_milli`: Time awake
  - `total_light_sleep_time_milli`: Light sleep duration
  - `total_slow_wave_sleep_time_milli`: Deep/SWS duration
  - `total_rem_sleep_time_milli`: REM sleep duration
  - `sleep_cycle_count`: Number of sleep cycles
  - `disturbance_count`: Wake-ups or disturbances
- `sleep_needed`: Sleep debt calculation (milliseconds)
- `respiratory_rate`: Breaths per minute
- `sleep_performance_percentage`: How well you met your sleep need (0-100)
- `sleep_consistency_percentage`: How consistent your sleep schedule is (0-100)
- `sleep_efficiency_percentage`: Time asleep / time in bed (0-100)

### GET /v1/sleep/{sleepId}
Get specific sleep record by ID.

**Scope**: `read:sleep`

**Response**: Same as single record from collection endpoint.

### GET /v1/cycle/{cycleId}/sleep
Get sleep for a specific cycle.

**Scope**: `read:sleep`

**Response**: Same as single record from collection endpoint.

## Cycle Endpoints

### GET /v1/cycle
Get all physiological cycles (paginated).

**Scope**: `read:cycles`

**Query Parameters**: Same as recovery endpoint.

**Response**:
```json
{
  "records": [
    {
      "id": 93845,
      "user_id": 10129,
      "created_at": "2022-04-24T11:25:44.774Z",
      "updated_at": "2022-04-24T14:25:44.774Z",
      "start": "2022-04-24T02:25:44.774Z",
      "end": "2022-04-24T10:25:44.774Z",
      "timezone_offset": "-05:00",
      "score_state": "SCORED",
      "score": {
        "strain": 5.2951527,
        "kilojoule": 8288.297,
        "average_heart_rate": 68,
        "max_heart_rate": 141
      }
    }
  ],
  "next_token": "MTIzOjEyMzEyMw"
}
```

**Score Fields**:
- `strain`: Daily strain score (0-21 scale)
- `kilojoule`: Energy expenditure in kilojoules
- `average_heart_rate`: Average HR during cycle (bpm)
- `max_heart_rate`: Peak HR during cycle (bpm)

**Note**: A "cycle" is WHOOP's physiological day, typically starting when you wake up and ending when you go to sleep.

### GET /v1/cycle/{cycleId}
Get specific cycle by ID.

**Scope**: `read:cycles`

**Response**: Same as single record from collection endpoint.

## Workout Endpoints

### GET /v1/workout
Get all workouts (paginated).

**Scope**: `read:workout`

**Query Parameters**: Same as recovery endpoint.

**Response**:
```json
{
  "records": [
    {
      "id": "ecfc6a15-4661-442f-a9a4-f160dd7afae8",
      "user_id": 9012,
      "created_at": "2022-04-24T11:25:44.774Z",
      "updated_at": "2022-04-24T14:25:44.774Z",
      "start": "2022-04-24T02:25:44.774Z",
      "end": "2022-04-24T10:25:44.774Z",
      "timezone_offset": "-05:00",
      "sport_name": "running",
      "sport_id": 1,
      "score_state": "SCORED",
      "score": {
        "strain": 8.2463,
        "average_heart_rate": 123,
        "max_heart_rate": 146,
        "kilojoule": 1569.34033203125,
        "percent_recorded": 100,
        "distance_meter": 1772.77035916,
        "altitude_gain_meter": 46.64384460449,
        "altitude_change_meter": -0.781372010707855,
        "zone_durations": {
          "zone_zero_milli": 300000,
          "zone_one_milli": 600000,
          "zone_two_milli": 900000,
          "zone_three_milli": 900000,
          "zone_four_milli": 600000,
          "zone_five_milli": 300000
        }
      }
    }
  ],
  "next_token": "MTIzOjEyMzEyMw"
}
```

**Score Fields**:
- `strain`: Activity strain score
- `average_heart_rate`: Average HR during workout (bpm)
- `max_heart_rate`: Peak HR during workout (bpm)
- `kilojoule`: Energy expenditure in kilojoules
- `percent_recorded`: % of workout captured by WHOOP
- `distance_meter`: Distance traveled in meters (GPS activities)
- `altitude_gain_meter`: Elevation gain in meters (GPS activities)
- `zone_durations`: Time in each HR zone (milliseconds)
  - Zone 0: <50% max HR
  - Zone 1: 50-60% max HR
  - Zone 2: 60-70% max HR
  - Zone 3: 70-80% max HR
  - Zone 4: 80-90% max HR
  - Zone 5: 90-100% max HR

### GET /v1/workout/{workoutId}
Get specific workout by ID.

**Scope**: `read:workout`

**Response**: Same as single record from collection endpoint.

## Common Response Fields

### score_state
All scored data includes a `score_state` field:
- `SCORED`: Data has been processed and scored
- `PENDING_SCORE`: Data is being processed
- `UNSCORABLE`: Data cannot be scored

### Pagination
Collection endpoints return:
- `records`: Array of data records
- `next_token`: Cursor for next page (omitted if last page)

To get next page, include `nextToken` query parameter:
```
GET /v1/recovery?limit=25&nextToken=MTIzOjEyMzEyMw
```

### Date Filtering
Use ISO 8601 timestamps:
```
GET /v1/sleep?start=2026-01-20T00:00:00Z&end=2026-01-27T23:59:59Z
```

## Error Responses

### 401 Unauthorized
Access token is invalid or expired. Refresh the token.

### 429 Too Many Requests
Rate limit exceeded. Check `Retry-After` header.

### 400 Bad Request
Invalid parameters or request format.

### 404 Not Found
Resource doesn't exist or user doesn't have access.
