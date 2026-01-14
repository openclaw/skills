#!/usr/bin/env bun
/**
 * Morning Report Script
 * Fetches weather from Open-Meteo (free) and pollen from IQVIA
 * Sends combined report to Telegram
 *
 * Usage: bun morning_report.ts [lat] [lon] [zip] [location_name]
 * Example: bun morning_report.ts 33.3506 -96.3175 75409 "Anna, TX"
 */

// Parse CLI args with defaults for Anna, TX
const args = process.argv.slice(2);
const LAT = parseFloat(args[0]) || 33.3506;
const LON = parseFloat(args[1]) || -96.3175;
const ZIP_CODE = args[2] || "75409";
const LOCATION_NAME = args[3] || "Anna, TX";

interface WeatherData {
  current: {
    temperature_2m: number;
    relative_humidity_2m: number;
    weather_code: number;
    wind_speed_10m: number;
  };
  daily: {
    weather_code: number[];
    temperature_2m_max: number[];
    temperature_2m_min: number[];
    precipitation_probability_max: number[];
    precipitation_sum: number[];
    uv_index_max: number[];
    sunrise: string[];
    sunset: string[];
  };
}

interface PollenData {
  index: number;
  category: string;
  triggers: string[];
}

// Weather code mappings
const weatherIcons: Record<number, string> = {
  0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
  45: "🌫️", 48: "🌫️",
  51: "🌧️", 53: "🌧️", 55: "🌧️",
  61: "🌧️", 63: "🌧️", 65: "🌧️",
  71: "❄️", 73: "❄️", 75: "❄️",
  80: "🌦️", 81: "🌦️", 82: "🌦️",
  95: "⛈️", 96: "⛈️", 99: "⛈️",
};

const weatherDescriptions: Record<number, string> = {
  0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
  45: "Foggy", 48: "Foggy",
  51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
  61: "Light rain", 63: "Rain", 65: "Heavy rain",
  71: "Light snow", 73: "Snow", 75: "Heavy snow",
  80: "Light showers", 81: "Showers", 82: "Heavy showers",
  95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
};

async function getWeather(): Promise<string> {
  try {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,uv_index_max,sunrise,sunset&temperature_unit=fahrenheit&timezone=auto`;
    const res = await fetch(url);
    const data = await res.json() as WeatherData;
    
    const temp = Math.round(data.current.temperature_2m);
    const humidity = data.current.relative_humidity_2m;
    const wind = Math.round(data.current.wind_speed_10m);
    const code = data.current.weather_code;
    
    // Daily forecast
    const high = Math.round(data.daily.temperature_2m_max[0]);
    const low = Math.round(data.daily.temperature_2m_min[0]);
    const dailyCode = data.daily.weather_code[0];
    const precipChance = data.daily.precipitation_probability_max[0];
    const precipAmount = data.daily.precipitation_sum[0];
    const uvIndex = Math.round(data.daily.uv_index_max[0]);
    
    // Format sunrise/sunset times
    const formatTime = (iso: string) => {
      const date = new Date(iso);
      return date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true });
    };
    const sunrise = formatTime(data.daily.sunrise[0]);
    const sunset = formatTime(data.daily.sunset[0]);
    
    const icon = weatherIcons[code] || "🌡️";
    const desc = weatherDescriptions[code] || "Unknown";
    const forecastDesc = weatherDescriptions[dailyCode] || "Unknown";
    
    // UV level description
    let uvLevel = "Low";
    if (uvIndex >= 11) uvLevel = "Extreme";
    else if (uvIndex >= 8) uvLevel = "Very High";
    else if (uvIndex >= 6) uvLevel = "High";
    else if (uvIndex >= 3) uvLevel = "Moderate";
    
    let result = `${icon} *Currently:* ${desc}, ${temp}°F

📅 *Today's Forecast*
• *Conditions:* ${forecastDesc}
• *High/Low:* ${high}°F / ${low}°F
• *Humidity:* ${humidity}%
• *Wind:* ${wind} mph`;
    
    if (precipChance > 0) {
      result += `\n• *Precipitation:* ${precipChance}% chance`;
      if (precipAmount > 0) {
        result += ` (${precipAmount.toFixed(2)}")`;
      }
    }
    
    result += `\n• *UV Index:* ${uvIndex} (${uvLevel})`;
    result += `\n• *Sun:* ☀️ ${sunrise} → 🌙 ${sunset}`;
    
    return result;
  } catch (error) {
    console.error("Weather error:", error);
    return "⚠️ Weather data unavailable";
  }
}

async function getPollen(): Promise<string> {
  try {
    // IQVIA pollen.com API (same data source as pyiqvia)
    const url = `https://www.pollen.com/api/forecast/current/pollen/${ZIP_CODE}`;
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://www.pollen.com/',
      }
    });
    
    if (!res.ok) {
      return "• _Pollen: Check pollen.com_";
    }
    
    const data = await res.json();
    const today = data?.Location?.periods?.[0];
    
    if (!today) {
      return "• _Pollen: Check pollen.com_";
    }
    
    const index = today.Index || 0;
    const triggers = (today.Triggers || [])
      .map((t: { Name: string }) => t.Name)
      .slice(0, 3)
      .join(", ");
    
    // Categorize pollen level
    let level = "Low";
    let emoji = "🟢";
    if (index >= 9.7) { level = "Very High"; emoji = "🔴"; }
    else if (index >= 7.3) { level = "High"; emoji = "🟠"; }
    else if (index >= 4.9) { level = "Medium-High"; emoji = "🟡"; }
    else if (index >= 2.5) { level = "Medium"; emoji = "🟡"; }
    
    let result = `${emoji} *Pollen:* ${level} (${index.toFixed(1)})`;
    if (triggers) {
      result += `\n• *Triggers:* ${triggers}`;
    }
    return result;
  } catch (error) {
    console.error("Pollen error:", error);
    return "• _Pollen: Check pollen.com_";
  }
}

async function sendTelegram(message: string): Promise<void> {
  const token = process.env.TELEGRAM_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID || "7667884018";
  
  if (!token) {
    console.error("TELEGRAM_TOKEN not set");
    return;
  }
  
  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: message,
      parse_mode: "Markdown",
    }),
  });
}

async function main() {
  const timestamp = new Date().toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
    timeZone: "America/Chicago",
  });
  
  const [weather, pollen] = await Promise.all([getWeather(), getPollen()]);
  
  const message = `🌅 *Morning Report - ${LOCATION_NAME}*
━━━━━━━━━━━━━━━
${weather}

🌿 *Allergies*
${pollen}

_${timestamp}_`;

  console.log(message);
  await sendTelegram(message);
  console.log(`[Sent at ${timestamp}]`);
}

main().catch(console.error);
