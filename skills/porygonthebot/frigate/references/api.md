# Frigate API Reference

## Authentication

### POST /api/login
Authenticate and receive a session cookie.

**Request:**
```json
{
  "user": "username",
  "password": "password"
}
```

**Response:** Empty body on success

**Cookie:** `frigate_token=<JWT token>`

**Example:**
```python
import requests
session = requests.Session()
session.post(
    "https://server.local:8971/api/login",
    json={"user": "username", "password": "password123"},
    verify=False
)
```

## Configuration

### GET /api/config
Get full Frigate configuration including cameras, streams, and settings.

**Response:**
```json
{
  "version": "0.16-0",
  "cameras": {
    "driveway": {
      "detect": {
        "enabled": true,
        "width": 640,
        "height": 480,
        "fps": 5
      },
      "rtmp": { ... },
      "rtsp": { ... }
    }
  },
  "go2rtc": {
    "streams": {
      "driveway_cam": ["rtsp://...@..."]
    }
  }
}
```

### GET /api/version
Get Frigate version.

**Response:**
```json
{
  "version": "0.16-0"
}
```

## Cameras

### GET /api/camera/notifications
Get active camera notifications.

### GET /api/camera/<name>/best.jpg
Get the best frame for a camera.

### GET /api/camera/<name>/latest.jpg
Get the latest frame for a camera.

**Example:**
```python
snapshot = session.get(
    "https://server.local:8971/api/doorbell/latest.jpg",
    verify=False
)
with open("doorbell.jpg", "wb") as f:
    f.write(snapshot.content)
```

## Events

### GET /api/events
Get motion/events.

**Query Parameters:**
- `cameras` - Comma-separated camera names
- `limit` - Maximum number of events (default: 10)
- `has_clip` - Filter for events with clips (1/0)
- `has_snapshot` - Filter for events with snapshots (1/0)

**Example:**
```python
events = session.get(
    "https://server.local:8971/api/events?cameras=doorbell,front&limit=20",
    verify=False
).json()
```

**Response:**
```json
[
  {
    "id": "...",
    "camera": "doorbell",
    "start_time": "2026-01-27T20:00:00Z",
    "end_time": "2026-01-27T20:01:00Z",
    "top_score": 0.85,
    "labels": ["person", "car"]
  }
]
```

### DELETE /api/events/<event_id>
Delete an event.

## Clips and Snapshots

### GET /api/clips/<camera_name>
Get clips for a camera.

### GET /api/clips/<camera_name>/<event_id>.mp4
Download a specific clip.

## Statistics

### GET /api/stats
Get system statistics.

**Response:**
```json
{
  "cpu_usages": {...},
  "gpu_usages": {...},
  "mem_usages": {...},
  "recordings": {...},
  "cameras": {...}
}
```

## Bird's Eye View

### GET /api/birdseye
Get Bird's Eye View configuration.

## Zones

### GET /api/zones
Get all zone definitions.

### GET /api/zones/<camera_name>
Get zones for a specific camera.

## WebRTC Streams

The go2rtc configuration provides WebRTC stream URLs:

```json
{
  "go2rtc": {
    "streams": {
      "driveway_cam": [
        "rtsp://username:password@192.168.1.100:554/live",
        "ffmpeg:driveway_cam#audio=aac"
      ]
    },
    "webrtc": {
      "candidates": ["192.168.0.157:8555"]
    }
  }
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (invalid or missing session)
- `404` - Not Found
- `500` - Server Error

Error response format:
```json
{
  "success": false,
  "message": "Error description"
}
```

## Session Management

- Session tokens expire after 24 hours (configurable via `session_length`)
- Tokens are JWTs containing: `{"sub": "username", "role": "viewer", "exp": timestamp}`
- Use `refresh_time` to refresh tokens before expiration (default: 12 hours)

## Complete Example

```python
import requests
import os

# Configuration
FRIGATE_URL = os.environ.get("FRIGATE_URL", "https://server.local:8971/")
FRIGATE_USER = os.environ.get("FRIGATE_USER", "username")
FRIGATE_PASS = os.environ.get("FRIGATE_PASS", "")

# Login
session = requests.Session()
session.post(
    f"{FRIGATE_URL}/api/login",
    json={"user": FRIGATE_USER, "password": FRIGATE_PASS},
    verify=False
)

# Get cameras
config = session.get(f"{FRIGATE_URL}/api/config", verify=False).json()
cameras = list(config['cameras'].keys())

# Get snapshot from first camera
snapshot = session.get(
    f"{FRIGATE_URL}/api/{cameras[0]}/latest.jpg",
    verify=False
)

# Get recent events
events = session.get(
    f"{FRIGATE_URL}/api/events?limit=10",
    verify=False
).json()

print(f"Found {len(cameras)} cameras: {cameras}")
print(f"Recent events: {len(events)}")
```
