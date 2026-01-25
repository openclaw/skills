#!/usr/bin/env python3
"""
Flight tracker using AviationStack API
Fetches real-time flight data and displays in Flighty-style format
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' library not installed. Install with: pip3 install requests")
    sys.exit(1)


def get_api_key() -> Optional[str]:
    """Get API key from environment variable"""
    api_key = os.environ.get('AVIATIONSTACK_API_KEY')
    if not api_key:
        print("Error: AVIATIONSTACK_API_KEY environment variable not set")
        print("Get your free API key at: https://aviationstack.com/signup/free")
        print("Then set it: export AVIATIONSTACK_API_KEY='your-key-here'")
        sys.exit(1)
    return api_key


def fetch_flight_data(flight_number: str, api_key: str) -> dict:
    """Fetch flight data from AviationStack API"""
    base_url = "http://api.aviationstack.com/v1/flights"
    
    params = {
        'access_key': api_key,
        'flight_iata': flight_number.upper()
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching flight data: {e}")
        sys.exit(1)


def format_time(time_str: Optional[str]) -> str:
    """Format ISO time string to readable format"""
    if not time_str:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.strftime("%I:%M %p %Z")
    except (ValueError, AttributeError):
        return time_str or "N/A"


def format_date(time_str: Optional[str]) -> str:
    """Format ISO time string to date"""
    if not time_str:
        return ""
    
    try:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d")
    except (ValueError, AttributeError):
        return ""


def get_status_emoji(status: Optional[str]) -> str:
    """Get emoji for flight status"""
    if not status:
        return "⚪"
    
    status_lower = status.lower()
    if "active" in status_lower or "airborne" in status_lower or "en-route" in status_lower:
        return "🟢"
    elif "landed" in status_lower or "arrived" in status_lower:
        return "✅"
    elif "scheduled" in status_lower:
        return "🟡"
    elif "delayed" in status_lower:
        return "🟠"
    elif "cancelled" in status_lower or "canceled" in status_lower:
        return "🔴"
    else:
        return "⚪"


def calculate_delay(scheduled: Optional[str], actual: Optional[str]) -> Optional[str]:
    """Calculate delay in minutes"""
    if not scheduled or not actual:
        return None
    
    try:
        sched_dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
        actual_dt = datetime.fromisoformat(actual.replace('Z', '+00:00'))
        diff = (actual_dt - sched_dt).total_seconds() / 60
        
        if diff > 5:
            return f"{int(diff)} min delay"
        elif diff < -5:
            return f"{int(abs(diff))} min early"
        else:
            return "On time"
    except (ValueError, AttributeError):
        return None


def display_flight(flight_data: dict) -> None:
    """Display flight data in Flighty-style format"""
    
    if not flight_data.get('data') or len(flight_data['data']) == 0:
        print("❌ No flight found with that number")
        return
    
    # Get first flight result
    flight = flight_data['data'][0]
    
    # Extract data
    flight_num = flight.get('flight', {})
    airline = flight.get('airline', {})
    departure = flight.get('departure', {})
    arrival = flight.get('arrival', {})
    aircraft = flight.get('aircraft', {})
    live = flight.get('live', {})
    flight_status = flight.get('flight_status', '')
    
    # Airline info
    airline_name = airline.get('name', 'Unknown Airline')
    flight_iata = flight_num.get('iata', flight_num.get('icao', 'N/A'))
    
    # Departure info
    dep_airport = departure.get('airport', 'Unknown')
    dep_iata = departure.get('iata', 'N/A')
    dep_terminal = departure.get('terminal', '')
    dep_gate = departure.get('gate', '')
    dep_scheduled = departure.get('scheduled')
    dep_estimated = departure.get('estimated')
    dep_actual = departure.get('actual')
    
    # Arrival info
    arr_airport = arrival.get('airport', 'Unknown')
    arr_iata = arrival.get('iata', 'N/A')
    arr_terminal = arrival.get('terminal', '')
    arr_gate = arrival.get('gate', '')
    arr_scheduled = arrival.get('scheduled')
    arr_estimated = arrival.get('estimated')
    arr_actual = arrival.get('actual')
    
    # Aircraft info
    aircraft_reg = aircraft.get('registration', '')
    aircraft_iata = aircraft.get('iata', '')
    aircraft_icao = aircraft.get('icao', '')
    
    # Live position
    altitude = live.get('altitude') if live else None
    speed = live.get('speed_horizontal') if live else None
    latitude = live.get('latitude') if live else None
    longitude = live.get('longitude') if live else None
    
    # Calculate delay
    dep_delay = calculate_delay(dep_scheduled, dep_actual or dep_estimated)
    arr_delay = calculate_delay(arr_scheduled, arr_actual or arr_estimated)
    
    # Status emoji
    status_emoji = get_status_emoji(flight_status)
    
    # Display in Flighty style
    print("─" * 50)
    print(f"\n✈️  **{airline_name.upper()} {flight_iata}**")
    if aircraft_iata or aircraft_icao:
        print(f"🛩️  {aircraft_icao or aircraft_iata}{' • ' + aircraft_reg if aircraft_reg else ''}")
    print()
    
    # Departure
    print("**🛫 DEPARTURE**")
    print(f"{dep_airport} ({dep_iata})")
    if dep_terminal:
        print(f"Terminal {dep_terminal}{', Gate ' + dep_gate if dep_gate else ''}")
    print(f"Scheduled: {format_time(dep_scheduled)}")
    if dep_estimated and dep_estimated != dep_scheduled:
        print(f"Estimated: {format_time(dep_estimated)}", end="")
        if dep_delay:
            print(f" ⏱️  *{dep_delay}*")
        else:
            print()
    if dep_actual:
        print(f"Actual: {format_time(dep_actual)}")
    print()
    
    # Arrival
    print("**🛬 ARRIVAL**")
    print(f"{arr_airport} ({arr_iata})")
    if arr_terminal:
        print(f"Terminal {arr_terminal}{', Gate ' + arr_gate if arr_gate else ''}")
    print(f"Scheduled: {format_time(arr_scheduled)}")
    if arr_estimated and arr_estimated != arr_scheduled:
        print(f"Estimated: {format_time(arr_estimated)}", end="")
        if arr_delay:
            print(f" ⏱️  *{arr_delay}*")
        else:
            print()
    if arr_actual:
        print(f"Actual: {format_time(arr_actual)}")
    print()
    
    # Flight status & progress
    print("**📊 FLIGHT STATUS**")
    print(f"Status: {status_emoji} **{flight_status.upper()}**")
    
    if altitude or speed:
        print()
        if altitude:
            print(f"Altitude: {int(altitude):,} ft")
        if speed:
            print(f"Speed: {int(speed)} km/h")
        if latitude and longitude:
            print(f"Position: {latitude:.4f}, {longitude:.4f}")
    
    print("\n" + "─" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='Track flights in real-time using AviationStack API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s AA100
  %(prog)s UA2402
  %(prog)s BA123 --json

Setup:
  1. Get free API key: https://aviationstack.com/signup/free
  2. Set environment: export AVIATIONSTACK_API_KEY='your-key-here'
        """
    )
    
    parser.add_argument(
        'flight_number',
        help='Flight number (e.g., AA100, UA2402)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON data instead of formatted display'
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = get_api_key()
    
    # Fetch flight data
    flight_data = fetch_flight_data(args.flight_number, api_key)
    
    # Display results
    if args.json:
        print(json.dumps(flight_data, indent=2))
    else:
        display_flight(flight_data)


if __name__ == '__main__':
    main()
