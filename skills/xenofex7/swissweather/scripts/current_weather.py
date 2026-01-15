#!/usr/bin/env python3
"""
Get current weather from Swiss MeteoSwiss measurement stations.
Data source: https://data.geo.admin.ch (official Swiss government data)
"""
import argparse
import csv
import sys
from datetime import datetime
from io import StringIO

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip3 install requests", file=sys.stderr)
    sys.exit(1)

CURRENT_WEATHER_URL = "https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv"

# CSV column mappings (important fields)
FIELDS = {
    'tre200s0': 'Temperature (°C)',
    'rre150z0': 'Precipitation (mm)',
    'sre000z0': 'Sunshine duration (min)',
    'gre000z0': 'Global radiation (W/m²)',
    'ure200s0': 'Rel. humidity (%)',
    'tde200s0': 'Dew point (°C)',
    'dkl010z0': 'Wind direction (°)',
    'fu3010z0': 'Wind speed (km/h)',
    'fu3010z1': 'Wind gust (km/h)',
    'prestas0': 'Pressure station (hPa)',
    'pp0qffs0': 'Pressure sea level QFF (hPa)',
    'pp0qnhs0': 'Pressure sea level QNH (hPa)',
}


def fetch_current_weather():
    """Fetch current weather data CSV from MeteoSwiss."""
    try:
        response = requests.get(CURRENT_WEATHER_URL, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}", file=sys.stderr)
        sys.exit(1)


def parse_csv(csv_text):
    """Parse MeteoSwiss CSV data."""
    reader = csv.DictReader(StringIO(csv_text), delimiter=';')
    return list(reader)


def format_value(value):
    """Format value, handling missing data."""
    if not value or value == '-':
        return 'N/A'
    try:
        return f"{float(value):.1f}"
    except ValueError:
        return value


def print_station_data(station_data):
    """Print formatted weather data for a station."""
    station = station_data['Station/Location']
    date = station_data['Date']
    
    # Parse date (format: YYYYMMDDHHMM)
    try:
        dt = datetime.strptime(date, '%Y%m%d%H%M')
        timestamp = dt.strftime('%Y-%m-%d %H:%M UTC')
    except:
        timestamp = date
    
    print(f"\n{'='*60}")
    print(f"Station: {station}")
    print(f"Time: {timestamp}")
    print(f"{'='*60}")
    
    for field_id, field_name in FIELDS.items():
        if field_id in station_data:
            value = format_value(station_data[field_id])
            print(f"{field_name:.<40} {value}")


def main():
    parser = argparse.ArgumentParser(
        description='Get current weather from Swiss MeteoSwiss stations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --station BER              # Berlin (Bern)
  %(prog)s --station ZRH              # Zurich Airport
  %(prog)s --station RAG              # Rapperswil
  %(prog)s --list                      # List all available stations
  %(prog)s --station BER --json       # Output as JSON

Popular stations:
  BER - Bern, ZRH - Zurich Airport, GVE - Geneva, LUG - Lugano,
  BAS - Basel, RAG - Rapperswil, SMA - Säntis, DAV - Davos
        '''
    )
    
    parser.add_argument('--station', '-s', help='Station code (e.g., BER, ZRH, RAG)')
    parser.add_argument('--list', '-l', action='store_true', help='List all available stations')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--all', '-a', action='store_true', help='Show all stations')
    
    args = parser.parse_args()
    
    # Fetch data
    csv_text = fetch_current_weather()
    stations = parse_csv(csv_text)
    
    # List mode
    if args.list:
        print("\nAvailable MeteoSwiss stations:")
        print(f"{'Code':<8} {'Last Update (UTC)'}")
        print("-" * 40)
        for s in stations:
            code = s['Station/Location']
            date = s['Date']
            try:
                dt = datetime.strptime(date, '%Y%m%d%H%M')
                timestamp = dt.strftime('%Y-%m-%d %H:%M')
            except:
                timestamp = date
            print(f"{code:<8} {timestamp}")
        return
    
    # Show specific station
    if args.station:
        station_code = args.station.upper()
        for s in stations:
            if s['Station/Location'] == station_code:
                if args.json:
                    import json
                    print(json.dumps(s, indent=2))
                else:
                    print_station_data(s)
                return
        print(f"Error: Station '{station_code}' not found. Use --list to see available stations.", file=sys.stderr)
        sys.exit(1)
    
    # Show all stations
    if args.all:
        for s in stations:
            print_station_data(s)
        return
    
    # No arguments: show help
    parser.print_help()


if __name__ == '__main__':
    main()
