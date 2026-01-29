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


def require_email(args) -> str:
    """Require a Tesla email to be provided via --email or TESLA_EMAIL."""
    email = resolve_email(args, prompt=False)
    if not email:
        print(
            "❌ Missing Tesla email. Set TESLA_EMAIL or pass --email\n"
            "   Example: TESLA_EMAIL=\"you@email.com\" python3 scripts/tesla.py list",
            file=sys.stderr,
        )
        sys.exit(2)
    return email


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


def _select_vehicle(vehicles, target_name: str):
    """Select a vehicle from a list by name (exact/partial) or 1-based index.

    - Exact match is case-insensitive.
    - If no exact match, a case-insensitive *substring* match is attempted.
    - If target_name is a digit (e.g., "1"), it's treated as a 1-based index.
    """
    if not vehicles:
        return None

    if not target_name:
        return vehicles[0]

    s = target_name.strip()
    if s.isdigit():
        idx = int(s) - 1
        if 0 <= idx < len(vehicles):
            return vehicles[idx]
        return None

    s_l = s.lower()

    # 1) Exact match (case-insensitive)
    for v in vehicles:
        if v.get('display_name', '').lower() == s_l:
            return v

    # 2) Substring match (case-insensitive)
    matches = [v for v in vehicles if s_l in v.get('display_name', '').lower()]
    if len(matches) == 1:
        return matches[0]

    # Ambiguous / not found
    return None


def get_vehicle(tesla, name: str = None):
    """Get vehicle by name/index, else default car, else first vehicle."""
    vehicles = tesla.vehicle_list()
    if not vehicles:
        print("❌ No vehicles found on this account", file=sys.stderr)
        sys.exit(1)

    target_name = name or resolve_default_car_name()

    if target_name:
        selected = _select_vehicle(vehicles, target_name)
        if selected:
            return selected

        # Give a more helpful error (and show numeric indices too).
        options = "\n".join(
            f"   {i+1}. {v.get('display_name')}" for i, v in enumerate(vehicles)
        )
        print(
            f"❌ Vehicle '{target_name}' not found (or ambiguous).\n"
            "   Tip: you can pass --car with a partial name (substring match) or a 1-based index.\n"
            f"Available vehicles:\n{options}",
            file=sys.stderr,
        )
        sys.exit(1)

    return vehicles[0]


def wake_vehicle(vehicle, allow_wake: bool = True) -> bool:
    """Wake vehicle if asleep.

    Returns True if the vehicle is (or becomes) online.
    If allow_wake is False and the vehicle is not online, returns False.
    """
    state = vehicle.get('state')
    if state == 'online':
        return True

    if not allow_wake:
        return False

    try:
        print("⏳ Waking vehicle...", file=sys.stderr)
        vehicle.sync_wake_up()
        return True
    except Exception as e:
        print(
            f"❌ Failed to wake vehicle (state was: {state}). Try again, or run: python3 scripts/tesla.py wake\n"
            f"   Details: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


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
    tesla = get_tesla(require_email(args))
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


def _bar_to_psi(bar):
    """Convert bar to PSI.

    Tesla APIs commonly return tire pressures in bar.
    """
    try:
        return float(bar) * 14.5037738
    except Exception:
        return None


def _fmt_tire_pressure(bar):
    """Format tire pressure as "X.X bar (Y psi)"."""
    if bar is None:
        return None
    try:
        b = float(bar)
    except Exception:
        return None
    psi = _bar_to_psi(b)
    if psi is None:
        return None
    return f"{b:.2f} bar ({psi:.0f} psi)"


def _fmt_minutes_hhmm(minutes):
    """Format minutes-from-midnight as HH:MM.

    Tesla endpoints commonly represent scheduled times as minutes after midnight.
    """
    try:
        m = int(minutes)
    except Exception:
        return None
    if m < 0:
        return None
    hh = (m // 60) % 24
    mm = m % 60
    return f"{hh:02d}:{mm:02d}"


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

    sentry = vs.get('sentry_mode')
    if sentry is not None:
        lines.append(f"Sentry: {_fmt_bool(sentry, 'On', 'Off')}")

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

    sched_time = charge.get('scheduled_charging_start_time')
    sched_mode = charge.get('scheduled_charging_mode')
    sched_pending = charge.get('scheduled_charging_pending')
    if sched_time is not None or sched_mode is not None or sched_pending is not None:
        bits = []
        if isinstance(sched_mode, str) and sched_mode.strip():
            bits.append(sched_mode.strip())
        elif sched_pending is not None:
            bits.append('On' if sched_pending else 'Off')
        hhmm = _fmt_minutes_hhmm(sched_time)
        if hhmm:
            bits.append(hhmm)
        if bits:
            lines.append(f"Scheduled charging: {' '.join(bits)}")

    inside = _fmt_temp_pair(climate.get('inside_temp'))
    outside = _fmt_temp_pair(climate.get('outside_temp'))
    if inside:
        lines.append(f"Inside: {inside}")
    if outside:
        lines.append(f"Outside: {outside}")

    climate_on = climate.get('is_climate_on')
    if climate_on is not None:
        lines.append(f"Climate: {_fmt_bool(climate_on, 'On', 'Off')}")

    # Tire pressures (TPMS) if available
    fl = _fmt_tire_pressure(vs.get('tpms_pressure_fl'))
    fr = _fmt_tire_pressure(vs.get('tpms_pressure_fr'))
    rl = _fmt_tire_pressure(vs.get('tpms_pressure_rl'))
    rr = _fmt_tire_pressure(vs.get('tpms_pressure_rr'))
    if any([fl, fr, rl, rr]):
        lines.append(
            "Tires (TPMS): "
            f"FL {fl or '(?)'} | FR {fr or '(?)'} | RL {rl or '(?)'} | RR {rr or '(?)'}"
        )

    odo = vs.get('odometer')
    if odo is not None:
        lines.append(f"Odometer: {odo:.0f} mi")

    return "\n".join(lines)


def _ensure_online_or_exit(vehicle, allow_wake: bool):
    if wake_vehicle(vehicle, allow_wake=allow_wake):
        return

    state = vehicle.get('state')
    name = vehicle.get('display_name', 'Vehicle')
    print(
        f"ℹ️ {name} is currently '{state}'. Skipping wake because --no-wake was set.\n"
        "   Re-run without --no-wake, or run: python3 scripts/tesla.py wake",
        file=sys.stderr,
    )
    sys.exit(3)


def cmd_report(args):
    """One-screen status report."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    _ensure_online_or_exit(vehicle, allow_wake=not getattr(args, 'no_wake', False))
    data = vehicle.get_vehicle_data()

    if args.json:
        print(json.dumps(data, indent=2))
        return

    print(_report(vehicle, data))


def cmd_status(args):
    """Get vehicle status."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    _ensure_online_or_exit(vehicle, allow_wake=not getattr(args, 'no_wake', False))
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
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('LOCK')
    print(f"🔒 {vehicle['display_name']} locked")


def cmd_unlock(args):
    """Unlock the vehicle."""
    require_yes(args, 'unlock')
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('UNLOCK')
    print(f"🔓 {vehicle['display_name']} unlocked")


def cmd_climate(args):
    """Control climate."""
    tesla = get_tesla(require_email(args))
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
            raise ValueError("Missing temperature value (e.g., climate temp 72 or climate temp 22 --celsius)")

        value = float(args.value)
        # Default is Fahrenheit unless --celsius is provided.
        in_f = True
        if getattr(args, "celsius", False):
            in_f = False
        elif getattr(args, "fahrenheit", False):
            in_f = True

        temp_c = (value - 32) * 5 / 9 if in_f else value
        vehicle.command('CHANGE_CLIMATE_TEMPERATURE_SETTING', driver_temp=temp_c, passenger_temp=temp_c)
        print(f"🌡️ {vehicle['display_name']} temperature set to {value:g}°{'F' if in_f else 'C'}")


def cmd_charge(args):
    """Control charging."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    # Read-only action can skip waking the car.
    allow_wake = True
    if args.action == 'status':
        allow_wake = not getattr(args, 'no_wake', False)

    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

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
        require_yes(args, 'charge start')
        vehicle.command('START_CHARGE')
        print(f"⚡ {vehicle['display_name']} charging started")
    elif args.action == 'stop':
        require_yes(args, 'charge stop')
        vehicle.command('STOP_CHARGE')
        print(f"🛑 {vehicle['display_name']} charging stopped")
    elif args.action == 'limit':
        if args.value is None:
            raise ValueError("Missing charge limit percent (e.g., charge limit 80)")
        pct = int(args.value)
        if pct < 50 or pct > 100:
            raise ValueError("Invalid charge limit percent. Expected 50–100")
        vehicle.command('CHANGE_CHARGE_LIMIT', percent=pct)
        print(f"🎚️ {vehicle['display_name']} charge limit set to {pct}%")


def _parse_hhmm(value: str):
    """Parse HH:MM into minutes after midnight."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing time. Expected HH:MM (e.g., 23:30)")
    s = value.strip()
    if ":" not in s:
        raise ValueError("Invalid time. Expected HH:MM (e.g., 23:30)")
    hh_s, mm_s = s.split(":", 1)
    hh = int(hh_s)
    mm = int(mm_s)
    if hh < 0 or hh > 23 or mm < 0 or mm > 59:
        raise ValueError("Invalid time. Expected HH:MM using 24-hour time")
    return hh * 60 + mm


def cmd_scheduled_charging(args):
    """Get/set scheduled charging (requires --yes to change)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    # Read-only action can skip waking the car.
    allow_wake = True
    if args.action == 'status':
        allow_wake = not getattr(args, 'no_wake', False)

    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

    if args.action == 'status':
        data = vehicle.get_vehicle_data()
        charge = data.get('charge_state', {})
        sched_time = charge.get('scheduled_charging_start_time')
        sched_mode = charge.get('scheduled_charging_mode')
        sched_pending = charge.get('scheduled_charging_pending')

        if args.json:
            print(json.dumps({'scheduled_charging_start_time': sched_time,
                              'scheduled_charging_mode': sched_mode,
                              'scheduled_charging_pending': sched_pending}, indent=2))
            return

        hhmm = _fmt_minutes_hhmm(sched_time)
        mode = (sched_mode.strip() if isinstance(sched_mode, str) else None)
        if not mode and sched_pending is not None:
            mode = 'On' if sched_pending else 'Off'

        print(f"🚗 {vehicle['display_name']}")
        print(f"Scheduled charging: {mode or '(unknown)'}")
        if hhmm:
            print(f"Start time: {hhmm}")
        return

    # Mutating actions
    require_yes(args, 'scheduled-charging')

    if args.action == 'off':
        vehicle.command('SCHEDULED_CHARGING', enable=False, time=0)
        print(f"⏱️ {vehicle['display_name']} scheduled charging disabled")
        return

    if args.action == 'set':
        minutes = _parse_hhmm(args.time)
        vehicle.command('SCHEDULED_CHARGING', enable=True, time=minutes)
        print(f"⏱️ {vehicle['display_name']} scheduled charging set to {_fmt_minutes_hhmm(minutes)}")
        return

    raise ValueError(f"Unknown action: {args.action}")


def _round_coord(x, digits: int = 2):
    """Round a coordinate for safer display.

    digits=2 is roughly ~1km precision (varies with latitude) and is
    intended as a non-sensitive default.
    """
    try:
        return round(float(x), digits)
    except Exception:
        return None


def cmd_location(args):
    """Get vehicle location.

    Default output is *approximate* (rounded) to reduce accidental leakage.
    Use --yes for precise coordinates.
    """
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    _ensure_online_or_exit(vehicle, allow_wake=not getattr(args, 'no_wake', False))

    data = vehicle.get_vehicle_data()
    drive = data['drive_state']

    lat, lon = drive['latitude'], drive['longitude']

    if getattr(args, "yes", False):
        print(f"📍 {vehicle['display_name']} Location (precise): {lat}, {lon}")
        print(f"   https://www.google.com/maps?q={lat},{lon}")
        return

    lat_r = _round_coord(lat, 2)
    lon_r = _round_coord(lon, 2)
    if lat_r is None or lon_r is None:
        raise ValueError("Missing location coordinates")

    print(f"📍 {vehicle['display_name']} Location (approx): {lat_r}, {lon_r}")
    print(f"   https://www.google.com/maps?q={lat_r},{lon_r}")
    print("   (Use --yes for precise coordinates)")


def cmd_tires(args):
    """Show tire pressures (TPMS) (read-only)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    # Read-only action can skip waking the car.
    allow_wake = not getattr(args, 'no_wake', False)
    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

    data = vehicle.get_vehicle_data()
    vs = data.get('vehicle_state', {})

    fl = _fmt_tire_pressure(vs.get('tpms_pressure_fl'))
    fr = _fmt_tire_pressure(vs.get('tpms_pressure_fr'))
    rl = _fmt_tire_pressure(vs.get('tpms_pressure_rl'))
    rr = _fmt_tire_pressure(vs.get('tpms_pressure_rr'))

    if args.json:
        print(json.dumps({
            'tpms_pressure_fl': vs.get('tpms_pressure_fl'),
            'tpms_pressure_fr': vs.get('tpms_pressure_fr'),
            'tpms_pressure_rl': vs.get('tpms_pressure_rl'),
            'tpms_pressure_rr': vs.get('tpms_pressure_rr'),
        }, indent=2))
        return

    print(f"🚗 {vehicle['display_name']}")
    print("Tire pressures (TPMS):")
    print(f"  FL: {fl or '(unknown)'}")
    print(f"  FR: {fr or '(unknown)'}")
    print(f"  RL: {rl or '(unknown)'}")
    print(f"  RR: {rr or '(unknown)'}")


def cmd_trunk(args):
    """Toggle frunk/trunk (requires --yes)."""
    require_yes(args, 'trunk')
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)

    which = 'front' if args.which == 'frunk' else 'rear'
    vehicle.command('ACTUATE_TRUNK', which_trunk=which)
    label = 'Frunk' if which == 'front' else 'Trunk'
    print(f"🧳 {vehicle['display_name']} {label} toggled")


def cmd_windows(args):
    """Vent or close windows (requires --yes)."""
    require_yes(args, 'windows')
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)

    # Tesla API requires lat/lon parameters; 0/0 works for this endpoint.
    if args.action == 'vent':
        vehicle.command('WINDOW_CONTROL', command='vent', lat=0, lon=0)
        print(f"🪟 {vehicle['display_name']} windows vented")
    elif args.action == 'close':
        vehicle.command('WINDOW_CONTROL', command='close', lat=0, lon=0)
        print(f"🪟 {vehicle['display_name']} windows closed")


def cmd_sentry(args):
    """Get/set Sentry Mode (on/off requires --yes)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    # Read-only action can skip waking the car.
    allow_wake = True
    if args.action == 'status':
        allow_wake = not getattr(args, 'no_wake', False)

    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

    if args.action == 'status':
        data = vehicle.get_vehicle_data()
        sentry = data.get('vehicle_state', {}).get('sentry_mode')
        if args.json:
            print(json.dumps({'sentry_mode': sentry}, indent=2))
            return
        if sentry is None:
            print(f"🚗 {vehicle['display_name']}\nSentry: (unknown)")
        else:
            print(f"🚗 {vehicle['display_name']}\nSentry: {_fmt_bool(sentry, 'On', 'Off')}")
        return

    # Mutating actions
    require_yes(args, 'sentry')
    wake_vehicle(vehicle)

    if args.action == 'on':
        vehicle.command('SET_SENTRY_MODE', on=True)
        print(f"🛡️ {vehicle['display_name']} Sentry turned on")
        return

    if args.action == 'off':
        vehicle.command('SET_SENTRY_MODE', on=False)
        print(f"🛡️ {vehicle['display_name']} Sentry turned off")
        return

    raise ValueError(f"Unknown action: {args.action}")


def cmd_honk(args):
    """Honk the horn."""
    require_yes(args, 'honk')
    tesla = get_tesla(require_email(args))
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
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('FLASH_LIGHTS')
    print(f"💡 {vehicle['display_name']} flashed lights!")


def cmd_charge_port(args):
    """Open/close the charge port door (requires --yes)."""
    require_yes(args, 'charge-port')
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)

    if args.action == 'open':
        vehicle.command('CHARGE_PORT_DOOR_OPEN')
        print(f"🔌 {vehicle['display_name']} charge port opened")
    elif args.action == 'close':
        vehicle.command('CHARGE_PORT_DOOR_CLOSE')
        print(f"🔌 {vehicle['display_name']} charge port closed")
    else:
        raise ValueError(f"Unknown action: {args.action}")


def cmd_wake(args):
    """Wake up the vehicle."""
    tesla = get_tesla(require_email(args))
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
        help=(
            "Safety confirmation for sensitive/disruptive actions "
            "(unlock/charge start|stop/trunk/windows/honk/flash/charge-port open|close/"
            "scheduled-charging set|off/sentry on|off/location precise)"
        ),
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Auth
    subparsers.add_parser("auth", help="Authenticate with Tesla")
    
    # List
    subparsers.add_parser("list", help="List all vehicles")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Get vehicle status")
    status_parser.add_argument("--summary", action="store_true", help="Also print a one-line summary")
    status_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Summary (alias)
    summary_parser = subparsers.add_parser("summary", help="One-line status summary")
    summary_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Report (one-screen)
    report_parser = subparsers.add_parser("report", help="One-screen status report")
    report_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

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
    charge_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")

    # Scheduled charging
    sched_parser = subparsers.add_parser("scheduled-charging", help="Get/set scheduled charging (set/off requires --yes)")
    sched_parser.add_argument("action", choices=["status", "set", "off"], help="status|set|off")
    sched_parser.add_argument("time", nargs="?", help="Start time for 'set' as HH:MM (24-hour)")
    sched_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")

    # Location
    location_parser = subparsers.add_parser("location", help="Get vehicle location (approx by default; use --yes for precise)")
    location_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Tire pressures (TPMS)
    tires_parser = subparsers.add_parser("tires", help="Show tire pressures (TPMS)")
    tires_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Trunk / frunk
    trunk_parser = subparsers.add_parser("trunk", help="Toggle trunk/frunk (requires --yes)")
    trunk_parser.add_argument("which", choices=["trunk", "frunk"], help="Which to actuate")

    # Windows
    windows_parser = subparsers.add_parser("windows", help="Vent/close windows (requires --yes)")
    windows_parser.add_argument("action", choices=["vent", "close"], help="Action to perform")

    # Sentry
    sentry_parser = subparsers.add_parser("sentry", help="Get/set Sentry Mode (on/off requires --yes)")
    sentry_parser.add_argument("action", choices=["status", "on", "off"], help="status|on|off")
    sentry_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")

    # Honk/flash
    subparsers.add_parser("honk", help="Honk the horn")
    subparsers.add_parser("flash", help="Flash the lights")

    # Charge port
    charge_port_parser = subparsers.add_parser("charge-port", help="Open/close the charge port door (requires --yes)")
    charge_port_parser.add_argument("action", choices=["open", "close"], help="Action to perform")

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
        "scheduled-charging": cmd_scheduled_charging,
        "location": cmd_location,
        "tires": cmd_tires,
        "trunk": cmd_trunk,
        "windows": cmd_windows,
        "sentry": cmd_sentry,
        "honk": cmd_honk,
        "flash": cmd_flash,
        "charge-port": cmd_charge_port,
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
