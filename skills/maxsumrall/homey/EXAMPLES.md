# Homey CLI Examples

Real-world usage examples for `homeycli`.

## Setup

```bash
# Set your token (get from https://tools.developer.homey.app/api/clients)
export HOMEY_TOKEN="your-bearer-token-here"

# Or save to config
mkdir -p ~/.homey
echo '{"token":"your-token"}' > ~/.homey/config.json

# Test connection
homeycli status
```

## Basic Commands

### Check Status
```bash
homeycli status
```

Output:
```
🏠 Homey Status:

  Name: Home
  Platform: local v8.1.0
  Hostname: homey-abc123
  Cloud ID: 5f9a1234567890abcdef
  Status: ✓ Connected
```

### List All Devices
```bash
homeycli devices
```

### List Devices (JSON)
```bash
homeycli devices --json | jq '.[] | select(.class == "light")'
```

## Controlling Lights

### Basic On/Off
```bash
# Turn on
homeycli device "Living Room Light" on

# Turn off
homeycli device "Bedroom Lamp" off
```

### Dimming
```bash
# 50% brightness
homeycli device "Kitchen Light" set dim 0.5

# 100% brightness
homeycli device "Kitchen Light" set dim 1.0

# 10% brightness (night mode)
homeycli device "Bedroom Light" set dim 0.1
```

### Color Control
```bash
# Set hue (0-1 scale)
homeycli device "RGB Strip" set light_hue 0.0    # Red
homeycli device "RGB Strip" set light_hue 0.33   # Green
homeycli device "RGB Strip" set light_hue 0.66   # Blue

# Set saturation
homeycli device "RGB Strip" set light_saturation 1.0   # Full color
homeycli device "RGB Strip" set light_saturation 0.5   # Pastel

# Set temperature (warm to cool)
homeycli device "White Light" set light_temperature 0.0   # Warm
homeycli device "White Light" set light_temperature 1.0   # Cool
```

## Climate Control

### Thermostat
```bash
# Set target temperature (Celsius)
homeycli device "Living Room Thermostat" set target_temperature 21

# Get current temperature
homeycli device "Living Room Thermostat" get measure_temperature

# Check heating status
homeycli device "Living Room Thermostat" get thermostat_state
```

## Media Control

### Volume
```bash
# Set volume (0-1 scale)
homeycli device "Sonos Living Room" set volume_set 0.5

# Mute
homeycli device "Sonos Living Room" set volume_mute true

# Unmute
homeycli device "Sonos Living Room" set volume_mute false
```

## Security

### Locks
```bash
# Lock
homeycli device "Front Door" set locked true

# Unlock
homeycli device "Front Door" set locked false

# Check status
homeycli device "Front Door" get locked
```

### Sensors
```bash
# Check motion
homeycli device "Hallway Motion" get alarm_motion

# Check door/window contact
homeycli device "Front Door Sensor" get alarm_contact

# Check battery level
homeycli device "Motion Sensor" get measure_battery
```

## Flows (Automations)

### List Flows
```bash
homeycli flows
```

### Trigger Flows
```bash
# By name
homeycli flow trigger "Good Morning"
homeycli flow trigger "Good Night"
homeycli flow trigger "Movie Time"

# By ID (if you know it)
homeycli flow trigger "5f9a1234567890abcdef"
```

## Zones

### List All Zones
```bash
homeycli zones
```

## Complex Workflows

### Morning Routine
```bash
#!/bin/bash
# Turn on bedroom light at low brightness
homeycli device "Bedroom Light" on
homeycli device "Bedroom Light" set dim 0.2

# Set comfortable temperature
homeycli device "Bedroom Thermostat" set target_temperature 20

# Trigger morning flow
homeycli flow trigger "Good Morning"
```

### Movie Mode
```bash
#!/bin/bash
# Dim living room lights
homeycli device "Living Room Main" set dim 0.1
homeycli device "TV Backlight" on
homeycli device "TV Backlight" set dim 0.3

# Or just trigger a flow
homeycli flow trigger "Movie Time"
```

### Night Routine
```bash
#!/bin/bash
# Turn off all main lights
homeycli device "Living Room" off
homeycli device "Kitchen" off
homeycli device "Hallway" off

# Night light in bedroom
homeycli device "Bedroom Light" on
homeycli device "Bedroom Light" set dim 0.05

# Lock doors
homeycli device "Front Door" set locked true

# Trigger night flow
homeycli flow trigger "Good Night"
```

### Check All Sensors
```bash
#!/bin/bash
# Get all sensor readings as JSON
homeycli devices --json | jq '.[] | select(.class == "sensor") | {
  name: .name,
  temperature: .capabilitiesObj.measure_temperature.value,
  humidity: .capabilitiesObj.measure_humidity.value,
  battery: .capabilitiesObj.measure_battery.value
}'
```

## Integration with AI (Clawdbot)

When using with Clawdbot, the AI can:

```bash
# Natural language → command translation
User: "Turn on the living room lights"
Clawd: homeycli device "Living Room" on

User: "Set bedroom temperature to 21"
Clawd: homeycli device "Bedroom Thermostat" set target_temperature 21

User: "Dim the kitchen lights to 50%"
Clawd: homeycli device "Kitchen" set dim 0.5

User: "What's the temperature in the living room?"
Clawd: homeycli device "Living Room Sensor" get measure_temperature
```

## Fuzzy Matching Examples

The CLI is forgiving with device names:

```bash
# All of these work for "Living Room - Main Light":
homeycli device "Living Room - Main Light" on     # Exact match
homeycli device "Living Room Main Light" on       # Close match
homeycli device "living room light" on            # Case insensitive
homeycli device "living light" on                 # Substring match
homeycli device "livng light" on                  # Typo tolerance
```

## JSON Processing

### Extract Specific Info
```bash
# All lights that are on
homeycli devices --json | jq '.[] | select(.class == "light" and .capabilitiesObj.onoff.value == true)'

# All devices in "Living Room" zone
homeycli devices --json | jq '.[] | select(.zone == "Living Room")'

# All sensors with low battery
homeycli devices --json | jq '.[] | select(.capabilitiesObj.measure_battery.value < 20)'

# Temperature readings
homeycli devices --json | jq '.[] | select(.capabilitiesObj.measure_temperature) | {name, temp: .capabilitiesObj.measure_temperature.value}'
```

## Error Handling

### Device Not Found
```bash
# If device doesn't exist, you'll see suggestions
homeycli device "Living Ight" on
# Error: Device not found: Living Ight
# Did you mean: Living Room - Main Light?
```

### Invalid Capability
```bash
homeycli device "Motion Sensor" set onoff true
# Error: Device "Motion Sensor" does not support capability: onoff
# Available: alarm_motion, measure_battery, measure_temperature
```

## Tips

1. **Use `--json` for scripting** - Parse output with `jq`, `grep`, etc.
2. **Fuzzy matching** - Don't worry about exact device names
3. **Check capabilities first** - Use `homeycli devices` to see what each device supports
4. **Group commands in flows** - Complex automations are easier as Homey flows

## Getting Help

```bash
homeycli --help                  # General help
homeycli device --help           # Device command help
homeycli flow --help             # Flow command help
```

## Troubleshooting

**No token found:**
```bash
# Check if token is set
echo $HOMEY_TOKEN

# Or check config file
cat ~/.homey/config.json
```

**Connection timeout:**
```bash
# Check Homey is online
homeycli status

homeycli status
```

**API rate limits:**
- The Homey Cloud API has rate limits
- If you hit limits, wait a minute and retry
- Batch operations when possible
