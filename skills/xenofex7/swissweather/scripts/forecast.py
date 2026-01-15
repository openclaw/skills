#!/usr/bin/env python3
"""
Get weather forecast for Swiss locations by postal code.
Data source: MeteoSwiss API (official Swiss government weather service)

Note: The MeteoSwiss API endpoint may change or require updates.
If this script fails, check references/api_info.md for alternative methods.
"""
import argparse
import json
import sys

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip3 install requests", file=sys.stderr)
    sys.exit(1)

FORECAST_URL = "https://app-prod-ws.meteoswiss-app.ch/v1/plzDetail?plz={plz:06d}"
USER_AGENT = "android-31 ch.admin.meteoswiss-2160000"

# Weather condition mapping (from MeteoSwiss icon codes)
CONDITIONS = {
    1: "☀️ Sunny",
    2: "🌤️ Partly cloudy",
    3: "🌤️ Partly cloudy",
    4: "🌤️ Partly cloudy",
    5: "☁️ Cloudy",
    6: "🌧️ Rainy",
    7: "🌧️ Rainy/Snowy",
    8: "❄️ Snowy",
    9: "🌧️ Light rain",
    10: "🌨️ Rain/Snow mix",
    11: "❄️ Light snow",
    12: "⛈️ Thunderstorm",
    13: "⛈️ Thunderstorm with rain",
    101: "🌙 Clear night",
    102: "🌙 Partly cloudy night",
}


def fetch_forecast(plz):
    """Fetch forecast data from MeteoSwiss API."""
    try:
        url = FORECAST_URL.format(plz=int(plz))
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching forecast: {e}", file=sys.stderr)
        print("\nNote: The MeteoSwiss API may have changed.", file=sys.stderr)
        print("Check references/api_info.md for alternative methods.", file=sys.stderr)
        sys.exit(1)


def format_forecast(data, days=3):
    """Format forecast data for display."""
    if 'forecast' not in data:
        print("Error: Unexpected API response format", file=sys.stderr)
        return
    
    forecast = data['forecast']
    if 'dayForecast' in forecast:
        daily = forecast['dayForecast'][:days]
        
        print(f"\n{'='*60}")
        print(f"Weather Forecast - {data.get('currentWeather', {}).get('location', 'Unknown')}")
        print(f"{'='*60}\n")
        
        for day in daily:
            date = day.get('date', 'Unknown')
            icon = day.get('icon', 0)
            condition = CONDITIONS.get(icon, f"Code {icon}")
            temp_max = day.get('temperatureMax', 'N/A')
            temp_min = day.get('temperatureMin', 'N/A')
            precip = day.get('precipitation', 'N/A')
            
            print(f"{date}")
            print(f"  {condition}")
            print(f"  Temperature: {temp_min}°C - {temp_max}°C")
            print(f"  Precipitation: {precip} mm")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Get weather forecast for Swiss locations by postal code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s 8640              # Rapperswil-Jona
  %(prog)s 8001              # Zurich
  %(prog)s 3000              # Bern
  %(prog)s 1200 --days 7     # Geneva, 7-day forecast
  %(prog)s 8640 --json       # Raw JSON output

Common postal codes:
  8001 - Zurich, 3000 - Bern, 1200 - Geneva, 4000 - Basel,
  6900 - Lugano, 8640 - Rapperswil-Jona, 9000 - St. Gallen
        '''
    )
    
    parser.add_argument('plz', type=int, help='Swiss postal code (4 or 5 digits)')
    parser.add_argument('--days', '-d', type=int, default=3, help='Number of days to show (default: 3)')
    parser.add_argument('--json', '-j', action='store_true', help='Output raw JSON')
    
    args = parser.parse_args()
    
    # Fetch forecast
    data = fetch_forecast(args.plz)
    
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        format_forecast(data, args.days)


if __name__ == '__main__':
    main()
