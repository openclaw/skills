---
name: frigate
description: Access Frigate NVR cameras with session-based authentication. Get live snapshots, retrieve motion events, and fetch stream URLs. Includes CLI helper script for doorbell, driveway, front, east, mailbox, and garage cameras.
---

# Frigate NVR Integration

Access Frigate NVR server at `FRIGATE_URL` with credentials from `FRIGATE_USER` and `FRIGATE_PASS` environment variables.

## Authentication

Frigate uses session-based authentication (not HTTP Basic Auth):

```python
import requests

session = requests.Session()
response = session.post(
    f"{FRIGATE_URL}/api/login",
    json={"user": FRIGATE_USER, "password": FRIGATE_PASS},
    verify=False  # For self-signed certificates
)
# session.cookies contains frigate_token for subsequent requests
```

## Common Operations

### Get Camera List
```python
response = session.get(f"{FRIGATE_URL}/api/config", verify=False)
config = response.json()
cameras = list(config.get('cameras', {}).keys())
# Returns: ['driveway', 'front', 'east', 'mailbox', 'garage', 'doorbell']
```

### Get Snapshot from Camera
```python
snapshot = session.get(
    f"{FRIGATE_URL}/api/{camera_name}/latest.jpg",
    verify=False
)
# Save: with open(f"/tmp/{camera_name}.jpg", "wb") as f: f.write(snapshot.content)
```

### Get Motion Events
```python
events = session.get(
    f"{FRIGATE_URL}/api/events?cameras={camera_name}&has_clip=1",
    verify=False
).json()
# Returns list of motion detection events with timestamps
```

### Get Camera Stream URL
```python
config = session.get(f"{FRIGATE_URL}/api/config", verify=False).json()
stream_config = config.get('go2rtc', {}).get('streams', {}).get(camera_name)
# Returns RTSP/WebRTC stream URLs
```

## Environment Variables

Required:
- `FRIGATE_URL` - Frigate server URL (e.g., `https://server.local:8971/`)
- `FRIGATE_USER` - Username for authentication
- `FRIGATE_PASS` - Password for authentication

Optional:
- None required beyond the above

## Example: Send Doorbell Snapshot to Telegram
```python
import requests

session = requests.Session()
session.post(f"{FRIGATE_URL}/api/login",
    json={"user": FRIGATE_USER, "password": FRIGATE_PASS}, verify=False)

# Get doorbell snapshot
snapshot = session.get(f"{FRIGATE_URL}/api/doorbell/latest.jpg", verify=False)

# Send to Telegram
from clawdbot import message
message(action="send", channel="telegram", target="3215551212",
        message="Doorbell snapshot", path="/tmp/doorbell_snapshot.jpg")
```

## Notes

- Always use `verify=False` for self-signed certificates on home networks
- Session tokens expire after 24 hours (configurable via `session_length`)
- The `/api/cameras` endpoint doesn't exist; use `/api/config` for camera info
- Frigate version 0.16+ uses this authentication model

## Bundled Resources

- **Scripts**: See [scripts/frigate.py](scripts/frigate.py) for CLI utility with commands: `list`, `snapshot`, `events`, `stream`
- **API Reference**: See [references/api.md](references/api.md) for complete API documentation
