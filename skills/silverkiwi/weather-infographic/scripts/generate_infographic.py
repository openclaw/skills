import os
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types
import requests

# Constants
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CODES = {
    0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
    45: 'Foggy', 48: 'Depositing rime fog', 51: 'Light drizzle',
    53: 'Moderate drizzle', 55: 'Dense drizzle', 56: 'Light freezing drizzle',
    57: 'Dense freezing drizzle', 61: 'Slight rain', 63: 'Moderate rain',
    65: 'Heavy rain', 66: 'Light freezing rain', 67: 'Heavy freezing rain',
    71: 'Slight snow fall', 73: 'Moderate snow fall', 75: 'Heavy snow fall',
    77: 'Snow grains', 80: 'Slight rain showers', 81: 'Moderate rain showers',
    82: 'Violent rain showers', 85: 'Slight snow showers', 86: 'Heavy snow showers',
    95: 'Thunderstorm', 96: 'Thunderstorm with slight hail',
    99: 'Thunderstorm with heavy hail',
}

def get_current_season():
    month = datetime.now().month
    if 3 <= month <= 5: return 'autumn'
    if 6 <= month <= 8: return 'winter'
    if 9 <= month <= 11: return 'spring'
    return 'summer'

def fetch_weather(lat, lon, timezone="Pacific/Auckland"):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m,uv_index,is_day",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code,wind_speed_10m_max,wind_direction_10m_dominant,uv_index_max,sunrise,sunset",
        "forecast_days": 7,
        "timezone": timezone
    }
    resp = requests.get(OPEN_METEO_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    
    forecast = []
    for i in range(len(data["daily"]["time"])):
        code = data["daily"]["weather_code"][i]
        forecast.append({
            "date": data["daily"]["time"][i],
            "temp_max": data["daily"]["temperature_2m_max"][i],
            "temp_min": data["daily"]["temperature_2m_min"][i],
            "precip_prob": data["daily"]["precipitation_probability_max"][i],
            "weather": WEATHER_CODES.get(code, "Unknown"),
            "wind_speed": data["daily"]["wind_speed_10m_max"][i],
            "wind_dir": data["daily"]["wind_direction_10m_dominant"][i],
            "uv": data["daily"]["uv_index_max"][i],
            "sunrise": data["daily"]["sunrise"][i],
            "sunset": data["daily"]["sunset"][i]
        })
    
    return {
        "temp": data["current"]["temperature_2m"],
        "apparent_temp": data["current"]["apparent_temperature"],
        "humidity": data["current"]["relative_humidity_2m"],
        "weather": WEATHER_CODES.get(data["current"]["weather_code"], "Unknown"),
        "wind_speed": data["current"]["wind_speed_10m"],
        "wind_dir": data["current"]["wind_direction_10m"],
        "uv": data["current"]["uv_index"],
        "forecast": forecast
    }

async def generate_infographic(address, lat, lon, output_path):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment")
        return False
    
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
    
    season = get_current_season()
    weather_data = fetch_weather(lat, lon)
    
    # Step 1: Generate Background
    bg_prompt = f"Generate a photorealistic high-resolution landscape photograph of {address} in New Zealand during {season}. Professional aerial scenery, wide angle, clean and uncluttered, suitable as a TV weather broadcast backdrop. No text, no people."
    print(f"Generating background for {address} ({season})...")
    
    bg_response = client.models.generate_content(
        model='gemini-3-pro-image-preview',
        contents=bg_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )
    )
    
    bg_image_part = None
    for part in bg_response.candidates[0].content.parts:
        if part.inline_data:
            bg_image_part = part.inline_data
            break
    
    if not bg_image_part:
        print("ERROR: Failed to generate background image")
        return False

    # Step 2: Generate Infographic
    infographic_prompt = f"""
    MASTER PROMPT: Photorealistic New Zealand TV weather broadcast frame.
    Studio environment with a curved video wall displaying the provided background image.
    Overlay a professional broadcast UI with the following weather data for {address}:
    - Current: {weather_data['temp']}°C, {weather_data['weather']}, Wind {weather_data['wind_speed']}km/h {weather_data['wind_dir']}°
    - 7-Day Forecast: {json.dumps(weather_data['forecast'], indent=2)}
    
    Requirements:
    - High legibility, accurate numerals.
    - Horizontal row of exactly 7 forecast tiles.
    - Deep blue theme, consistent NZ broadcast style.
    - No channel logos.
    - Accurate representation of weather icons.
    """
    
    print("Stitching weather data onto background...")
    final_response = client.models.generate_content(
        model='gemini-3-pro-image-preview',
        contents=[
            types.Part.from_bytes(data=bg_image_part.data, mime_type=bg_image_part.mime_type),
            infographic_prompt
        ],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(image_size="1K")
        )
    )
    
    final_image_data = None
    for part in final_response.candidates[0].content.parts:
        if part.inline_data:
            final_image_data = part.inline_data.data
            break
            
    if final_image_data:
        with open(output_path, "wb") as f:
            f.write(final_image_data)
        print(f"MEDIA:{os.path.abspath(output_path)}")
        return True
    else:
        print("ERROR: Failed to generate final infographic")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", required=True)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--output", default="weather_infographic.png")
    args = parser.parse_args()
    
    asyncio.run(generate_infographic(args.address, args.lat, args.lon, args.output))
