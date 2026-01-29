#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "teslapy>=2.0.0",
# ]
# ///
"""
Tesla vehicle control via unofficial API.
Supports multiple vehicles.
"""

import argparse
import json
import os
import sys
from pathlib import Path

CACHE_FILE = Path.home() / ".tesla_cache.json"
DEFAULTS_FILE = Path.home() / ".my_tesla.json"


def resolve_email(args, prompt: bool = True) -> str:
    """Resolve Tesla account email from args/env, optionally prompting."""
    email = getattr(args, "email", None) or os.environ.get("TESLA_EMAIL")
    if isinstance(email, str) and email.strip():
        return email.strip()
    if not prompt:
        return None
    return input("Tesla email: ").strip()


def get_tesla(email: str):
    """Get authenticated Tesla instance."""
    import teslapy
    
    def custom_auth(url):
        print(f"\n🔐 Open this URL in your browser:\n{url}\n")
        print("Log in to Tesla, then paste the final URL here")
        print("(it will start with https://auth.tesla.com/void/callback?...)")
        return input("\nCallback URL: ").strip()
    
    tesla = teslapy.Tesla(email, authenticator=custom_auth, cache_file=str(CACHE_FILE))
    
    if not tesla.authorized:
        tesla.fetch_token()
        print("✅ Authenticated successfully!")
    
    return tesla


def load_defaults():
    """Load optional user defaults from ~/.my_tesla.json (local only)."""
    try:
        if DEFAULTS_FILE.exists():
            return json.loads(DEFAULTS_FILE.read_text())
    except Exception:
        pass
    return {}


def save_defaults(obj: dict):
    DEFAULTS_FILE.write_text(json.dumps(obj, indent=2) + "\n")


def resolve_default_car_name():
    # Highest priority: env var
    env_name = os.environ.get("MY_TESLA_DEFAULT_CAR")
    if env_name:
        return env_name.strip()

    defaults = load_defaults()
    name = defaults.get("default_car")
    return name.strip() if isinstance(name, str) and name.strip() else None


def get_vehicle(tesla, name: str = None):
    """Get vehicle by name, else default car, else first vehicle."""
    vehicles = tesla.vehicle_list()
    if not vehicles:
        print("❌ No vehicles found on this account", file=sys.stderr)
        sys.exit(1)

    target_name = name or resolve_default_car_name()

    if target_name:
        for v in vehicles:
            if v['display_name'].lower() == target_name.lower():
                return v
        print(
            f"❌ Vehicle '{target_name}' not found. Available: {', '.join(v['display_name'] for v in vehicles)}",
            file=sys.stderr,
        )
        sys.exit(1)

    return vehicles[0]


def wake_vehicle(vehicle):
    """Wake vehicle if asleep."""
    if vehicle['state'] != 'online':
        print("⏳ Waking vehicle...", file=sys.stderr)
        vehicle.sync_wake_up()


def cmd_auth(args):
    """Authenticate with Tesla."""
    email = resolve_email(args)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)

    tesla = get_tesla(email)
    vehicles = tesla.vehicle_list()
    print(f"\n✅ Authentication cached at {CACHE_FILE}")
    print(f"\n🚗 Found {len(vehicles)} vehicle(s):")
    for v in vehicles:
        # Avoid printing VINs by default.
        print(f"   - {v['display_name']} ({v['state']})")


def cmd_list(args):
    """List all vehicles."""
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicles = tesla.vehicle_list()

    default_name = resolve_default_car_name()

    print(f"Found {len(vehicles)} vehicle(s):\n")
    for i, v in enumerate(vehicles):
        star = " (default)" if default_name and v['display_name'].lower() == default_name.lower() else ""
        print(f"{i+1}. {v['display_name']}{star}")
        # Avoid printing VIN in normal output (privacy). Use --json if you really need full data.
        print(f"   State: {v['state']}")
        print()

    if default_name:
        print(f"Default car: {default_name}")
    else:
        print("Default car: (none) — set with: python3 scripts/tesla.py default-car \"Name\"")


def _c_to_f(c):
    try:
        return c * 9 / 5 + 32
    except Exception:
        return None


def _fmt_bool(b, yes="Yes", no="No"):
    return yes if b else no


def _short_status(vehicle, data):
    charge = data.get('charge_state', {})
    climate = data.get('climate_state', {})
    vs = data.get('vehicle_state', {})

    batt = charge.get('battery_level')
    rng = charge.get('battery_range')
    charging = charge.get('charging_state')
    locked = vs.get('locked')
    inside_c = climate.get('inside_temp')
    inside_f = _c_to_f(inside_c) if inside_c is not None else None
    climate_on = climate.get('is_climate_on')

    parts = [f"🚗 {vehicle['display_name']}"]
    if locked is not None:
        parts.append(f"🔒 {_fmt_bool(locked, 'Locked', 'Unlocked')}")
    if batt is not None:
        if rng is not None:
            parts.append(f"🔋 {batt}% ({rng:.0f} mi)")
        else:
            parts.append(f"🔋 {batt}%")
    if charging:
        parts.append(f"⚡ {charging}")
    if inside_c is not None and inside_f is not None:
        parts.append(f"🌡️ {inside_f:.0f}°F")
    if climate_on is not None:
        parts.append(f"❄️ {_fmt_bool(climate_on, 'On', 'Off')}")

    return " • ".join(parts)


def _fmt_temp_pair(c):
    if c is None:
        return None
    f = _c_to_f(c)
    if f is None:
        return None
    return f"{c}°C ({f:.0f}°F)"


def _report(vehicle, data):
    """One-screen status report (safe for chat)."""
    charge = data.get('charge_state', {})
    climate = data.get('climate_state', {})
    vs = data.get('vehicle_state', {})

    lines = []
    lines.append(f"🚗 {vehicle['display_name']}")
    lines.append(f"State: {vehicle.get('state')}")

    locked = vs.get('locked')
    if locked is not None:
        lines.append(f"Locked: {_fmt_bool(locked, 'Yes', 'No')}")

    batt = charge.get('battery_level')
    rng = charge.get('battery_range')
    if batt is not None and rng is not None:
        lines.append(f"Battery: {batt}% ({rng:.0f} mi)")
    elif batt is not None:
        lines.append(f"Battery: {batt}%")

    charging_state = charge.get('charging_state')
    if charging_state is not None:
        extra = []
        limit = charge.get('charge_limit_soc')
        if limit is not None:
            extra.append(f"limit {limit}%")
        if charging_state == 'Charging':
            ttf = charge.get('time_to_full_charge')
            if ttf is not None:
                extra.append(f"{ttf:.1f}h to full")
            rate = charge.get('charge_rate')
            if rate is not None:
                extra.append(f"{rate} mph")
        suffix = f" ({', '.join(extra)})" if extra else ""
        lines.append(f"Charging: {charging_state}{suffix}")

    inside = _fmt_temp_pair(climate.get('inside_temp'))
    outside = _fmt_temp_pair(climate.get('outside_temp'))
    if inside:
        lines.append(f"Inside: {inside}")
    if outside:
        lines.append(f"Outside: {outside}")

    climate_on = climate.get('is_climate_on')
    if climate_on is not None:
        lines.append(f"Climate: {_fmt_bool(climate_on, 'On', 'Off')}")

    odo = vs.get('odometer')
    if odo is not None:
        lines.append(f"Odometer: {odo:.0f} mi")

    return "\n".join(lines)


def cmd_report(args):
    """One-screen status report."""
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    data = vehicle.get_vehicle_data()

    if args.json:
        print(json.dumps(data, indent=2))
        return

    print(_report(vehicle, data))


def cmd_status(args):
    """Get vehicle status."""
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)

    wake_vehicle(vehicle)
    data = vehicle.get_vehicle_data()

    charge = data.get('charge_state', {})
    climate = data.get('climate_state', {})
    vehicle_state = data.get('vehicle_state', {})

    if getattr(args, 'summary', False):
        print(_short_status(vehicle, data))
        return

    # Human-friendly detailed view
    print(f"🚗 {vehicle['display_name']}")
    print(f"   State: {vehicle.get('state')}")

    batt = charge.get('battery_level')
    rng = charge.get('battery_range')
    if batt is not None and rng is not None:
        print(f"   Battery: {batt}% ({rng:.0f} mi)")
    elif batt is not None:
        print(f"   Battery: {batt}%")

    charging_state = charge.get('charging_state')
    if charging_state is not None:
        print(f"   Charging: {charging_state}")

    inside_c = climate.get('inside_temp')
    outside_c = climate.get('outside_temp')
    if inside_c is not None:
        inside_f = _c_to_f(inside_c)
        if inside_f is not None:
            print(f"   Inside temp: {inside_c}°C ({inside_f:.0f}°F)")
    if outside_c is not None:
        outside_f = _c_to_f(outside_c)
        if outside_f is not None:
            print(f"   Outside temp: {outside_c}°C ({outside_f:.0f}°F)")

    climate_on = climate.get('is_climate_on')
    if climate_on is not None:
        print(f"   Climate on: {climate_on}")

    locked = vehicle_state.get('locked')
    if locked is not None:
        print(f"   Locked: {locked}")

    odo = vehicle_state.get('odometer')
    if odo is not None:
        print(f"   Odometer: {odo:.0f} mi")

    if args.json:
        print(json.dumps(data, indent=2))


def cmd_lock(args):
    """Lock the vehicle."""
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('LOCK')
    print(f"🔒 {vehicle['display_name']} locked")


def cmd_unlock(args):
    """Unlock the vehicle."""
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('UNLOCK')
    print(f"🔓 {vehicle['display_name']} unlocked")


def cmd_climate(args):
    """Control climate."""
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    
    if args.action == 'on':
        vehicle.command('CLIMATE_ON')
        print(f"❄️ {vehicle['display_name']} climate turned on")
    elif args.action == 'off':
        vehicle.command('CLIMATE_OFF')
        print(f"🌡️ {vehicle['display_name']} climate turned off")
    elif args.action == 'temp':
        if args.value is None:
            raise ValueError("Missing temperature value")

        value = float(args.value)
        in_f = not getattr(args, "celsius", False)  # default: Fahrenheit unless --celsius
        temp_c = (value - 32) * 5 / 9 if in_f else value
        vehicle.command('CHANGE_CLIMATE_TEMPERATURE_SETTING', driver_temp=temp_c, passenger_temp=temp_c)
        print(f"🌡️ {vehicle['display_name']} temperature set to {value:g}°{'F' if in_f else 'C'}")


def cmd_charge(args):
    """Control charging."""
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    
    if args.action == 'status':
        data = vehicle.get_vehicle_data()
        charge = data['charge_state']
        print(f"🔋 {vehicle['display_name']} Battery: {charge['battery_level']}%")
        print(f"   Range: {charge['battery_range']:.0f} mi")
        print(f"   State: {charge['charging_state']}")
        print(f"   Limit: {charge['charge_limit_soc']}%")
        if charge['charging_state'] == 'Charging':
            print(f"   Time left: {charge['time_to_full_charge']:.1f} hrs")
            print(f"   Rate: {charge['charge_rate']} mph")
    elif args.action == 'start':
        vehicle.command('START_CHARGE')
        print(f"⚡ {vehicle['display_name']} charging started")
    elif args.action == 'stop':
        vehicle.command('STOP_CHARGE')
        print(f"🛑 {vehicle['display_name']} charging stopped")
    elif args.action == 'limit':
        vehicle.command('CHANGE_CHARGE_LIMIT', percent=int(args.value))
        print(f"🎚️ {vehicle['display_name']} charge limit set to {int(args.value)}%")


def cmd_location(args):
    """Get vehicle location (sensitive)."""
    require_yes(args, 'location')
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)

    data = vehicle.get_vehicle_data()
    drive = data['drive_state']

    lat, lon = drive['latitude'], drive['longitude']
    print(f"📍 {vehicle['display_name']} Location: {lat}, {lon}")
    print(f"   https://www.google.com/maps?q={lat},{lon}")


def cmd_trunk(args):
    """Toggle frunk/trunk (requires --yes)."""
    require_yes(args, 'trunk')
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)

    which = 'front' if args.which == 'frunk' else 'rear'
    vehicle.command('ACTUATE_TRUNK', which_trunk=which)
    label = 'Frunk' if which == 'front' else 'Trunk'
    print(f"🧳 {vehicle['display_name']} {label} toggled")


def cmd_windows(args):
    """Vent or close windows (requires --yes)."""
    require_yes(args, 'windows')
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)

    # Tesla API requires lat/lon parameters; 0/0 works for this endpoint.
    if args.action == 'vent':
        vehicle.command('WINDOW_CONTROL', command='vent', lat=0, lon=0)
        print(f"🪟 {vehicle['display_name']} windows vented")
    elif args.action == 'close':
        vehicle.command('WINDOW_CONTROL', command='close', lat=0, lon=0)
        print(f"🪟 {vehicle['display_name']} windows closed")


def cmd_honk(args):
    """Honk the horn."""
    require_yes(args, 'honk')
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('HONK_HORN')
    print(f"📢 {vehicle['display_name']} honked!")


def require_yes(args, action: str):
    if not getattr(args, "yes", False):
        print(f"❌ Refusing to run '{action}' without --yes (safety gate)", file=sys.stderr)
        sys.exit(2)


def cmd_flash(args):
    """Flash the lights."""
    require_yes(args, 'flash')
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('FLASH_LIGHTS')
    print(f"💡 {vehicle['display_name']} flashed lights!")


def cmd_wake(args):
    """Wake up the vehicle."""
    email = resolve_email(args, prompt=False)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)
    tesla = get_tesla(email)
    vehicle = get_vehicle(tesla, args.car)
    print(f"⏳ Waking {vehicle['display_name']}...")
    vehicle.sync_wake_up()
    print(f"✅ {vehicle['display_name']} is awake")


def cmd_summary(args):
    """One-line status summary."""
    args.summary = True
    return cmd_status(args)


def cmd_default_car(args):
    """Set or show the default car used when --car is not provided."""
    if not args.name:
        name = resolve_default_car_name()
        if name:
            print(f"Default car: {name}")
        else:
            print("Default car: (none)")
        return

    defaults = load_defaults()
    defaults["default_car"] = args.name
    save_defaults(defaults)
    print(f"✅ Default car set to: {args.name}")
    print(f"Saved to: {DEFAULTS_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Tesla vehicle control")
    parser.add_argument("--email", "-e", help="Tesla account email")
    parser.add_argument("--car", "-c", help="Vehicle name (default: first vehicle)")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Safety confirmation for sensitive/disruptive actions (location/trunk/windows/honk/flash)",
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Auth
    subparsers.add_parser("auth", help="Authenticate with Tesla")
    
    # List
    subparsers.add_parser("list", help="List all vehicles")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Get vehicle status")
    status_parser.add_argument("--summary", action="store_true", help="Also print a one-line summary")

    # Summary (alias)
    subparsers.add_parser("summary", help="One-line status summary")

    # Report (one-screen)
    subparsers.add_parser("report", help="One-screen status report")

    # Default car
    default_parser = subparsers.add_parser("default-car", help="Set/show default vehicle name")
    default_parser.add_argument("name", nargs="?", help="Vehicle display name to set as default")
    
    # Lock/unlock
    subparsers.add_parser("lock", help="Lock the vehicle")
    subparsers.add_parser("unlock", help="Unlock the vehicle")
    
    # Climate
    climate_parser = subparsers.add_parser("climate", help="Climate control")
    climate_parser.add_argument("action", choices=["on", "off", "temp"])
    climate_parser.add_argument("value", nargs="?", help="Temperature value")
    temp_units = climate_parser.add_mutually_exclusive_group()
    temp_units.add_argument("--fahrenheit", "-f", action="store_true", help="Temperature value is in °F (default)")
    temp_units.add_argument("--celsius", action="store_true", help="Temperature value is in °C")
    
    # Charge
    charge_parser = subparsers.add_parser("charge", help="Charging control")
    charge_parser.add_argument("action", choices=["status", "start", "stop", "limit"])
    charge_parser.add_argument("value", nargs="?", help="Charge limit percent for 'limit' (e.g., 80)")
    
    # Location
    subparsers.add_parser("location", help="Get vehicle location (requires --yes)")

    # Trunk / frunk
    trunk_parser = subparsers.add_parser("trunk", help="Toggle trunk/frunk (requires --yes)")
    trunk_parser.add_argument("which", choices=["trunk", "frunk"], help="Which to actuate")

    # Windows
    windows_parser = subparsers.add_parser("windows", help="Vent/close windows (requires --yes)")
    windows_parser.add_argument("action", choices=["vent", "close"], help="Action to perform")

    # Honk/flash
    subparsers.add_parser("honk", help="Honk the horn")
    subparsers.add_parser("flash", help="Flash the lights")
    
    # Wake
    subparsers.add_parser("wake", help="Wake up the vehicle")
    
    args = parser.parse_args()
    
    commands = {
        "auth": cmd_auth,
        "list": cmd_list,
        "status": cmd_status,
        "summary": cmd_summary,
        "report": cmd_report,
        "lock": cmd_lock,
        "unlock": cmd_unlock,
        "climate": cmd_climate,
        "charge": cmd_charge,
        "location": cmd_location,
        "trunk": cmd_trunk,
        "windows": cmd_windows,
        "honk": cmd_honk,
        "flash": cmd_flash,
        "wake": cmd_wake,
        "default-car": cmd_default_car,
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
