import type { ToolDef } from '../../../src/types';
import { z } from 'zod';

// Load weather config from environment (with defaults for Anna, TX)
const WEATHER_LAT = parseFloat(process.env.WEATHER_LAT || '33.3506');
const WEATHER_LON = parseFloat(process.env.WEATHER_LON || '-96.3175');
const WEATHER_LOCATION = process.env.WEATHER_LOCATION || 'Anna, TX';

// Pollen API using current endpoint which includes trigger types
async function getPollenData(): Promise<string> {
  try {
    // First, get a session by visiting the main pollen page
    const sessionResponse = await fetch('https://www.pollen.com/forecast/current/pollen/75409', {
      headers: {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
      },
    });

    // Extract cookies from the response
    const setCookie = sessionResponse.headers.get('set-cookie') || '';
    const sessionId = setCookie.match(/ASP\.NET_SessionId=([^;]+)/)?.[1] || '';

    const response = await fetch(
      'https://www.pollen.com/api/forecast/current/pollen/75409',
      {
        headers: {
          'accept': 'application/json, text/plain, */*',
          'accept-language': 'en-US,en;q=0.9',
          'cache-control': 'no-cache',
          'pragma': 'no-cache',
          'referer': 'https://www.pollen.com/forecast/current/pollen/75409',
          'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
          'cookie': `ASP.NET_SessionId=${sessionId}; search=75409; geo=75409`,
        },
      }
    );

    if (!response.ok) {
      const text = await response.text();
      console.log('[Pollen] Error response:', text.slice(0, 500));
      return "Pollen data unavailable";
    }

    const text = await response.text();
    const data = JSON.parse(text);

    // Pollen API response structure
    const location = data?.Location;
    const periods = location?.periods;
    if (!periods || !Array.isArray(periods) || periods.length === 0) {
      return "Pollen data unavailable";
    }

    // Pollen index levels with cleaner emojis
    const getLevel = (index: number): string => {
      if (index >= 9.7) return "🟥 Extremely High";
      if (index >= 7.3) return "🟧 High";
      if (index >= 4.7) return "🟨 Medium-High";
      if (index >= 2.4) return "🟩 Medium";
      if (index >= 0.1) return "🟦 Low";
      return "⚪ None";
    };

    let report = `📊 **Pollen Forecast - ${location?.DisplayLocation || 'Anna, TX'}**\n\n`;

    // Show Yesterday, Today, Tomorrow
    periods.forEach((period: any) => {
      const type = period.Type || period.Period;
      const index = period.Index;
      const level = getLevel(index);

      // Extract trigger names (pollen types)
      const triggers = period.Triggers || [];
      const triggerNames = triggers.map((t: any) => t.Name).join(', ');

      report += `**${type}**: ${level} (${index}/12)`;
      if (triggerNames) {
        report += ` - ${triggerNames}`;
      }
      report += `\n`;
    });

    return report;
  } catch (error) {
    console.error('Pollen fetch error:', error);
    return "Pollen data unavailable";
  }
}

// Weather codes with emojis
const WEATHER_EMOJIS: Record<number, string> = {
  0: "☀️",  // Clear sky
  1: "🌤️",  // Mainly clear
  2: "⛅",  // Partly cloudy
  3: "☁️",  // Overcast
  45: "🌫️", // Fog
  48: "🌫️", // Depositing rime fog
  51: "🌧️", // Light drizzle
  53: "🌧️", // Moderate drizzle
  55: "🌧️", // Dense drizzle
  61: "🌧️", // Slight rain
  63: "🌧️", // Moderate rain
  65: "🌧️", // Heavy rain
  71: "❄️", // Slight snow
  73: "❄️", // Moderate snow
  75: "❄️", // Heavy snow
  80: "🌦️", // Slight showers
  81: "🌦️", // Moderate showers
  82: "🌦️", // Violent showers
  95: "⛈️", // Thunderstorm
  96: "⛈️", // Thunderstorm with hail
  99: "⛈️", // Thunderstorm with heavy hail
};

// WMO Weather interpretation codes
function getWeatherDesc(code: number): string {
  const codes: Record<number, string> = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail"
  };
  return codes[code] || "Unknown";
}

// Get weather for a specific location (uses env defaults for coordinates)
async function getWeatherReport(locationOverride?: string): Promise<string> {
  try {
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${WEATHER_LAT}&longitude=${WEATHER_LON}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=America/Chicago`,
    );

    if (!response.ok) {
      throw new Error('Weather fetch failed');
    }

    const data = await response.json();
    const current = data.current;
    const daily = data.daily;

    const tempC = current.temperature_2m;
    const tempF = Math.round(tempC * 9 / 5 + 32);
    const humidity = current.relative_humidity_2m;
    const wind = current.wind_speed_10m;
    const emoji = WEATHER_EMOJIS[current.weather_code] || "";
    const condition = emoji ? `${emoji} ${getWeatherDesc(current.weather_code)}` : getWeatherDesc(current.weather_code);

    // Today's forecast (convert C to F)
    const todayMaxC = daily.temperature_2m_max[0];
    const todayMinC = daily.temperature_2m_min[0];
    const todayMax = Math.round(todayMaxC * 9 / 5 + 32);
    const todayMin = Math.round(todayMinC * 9 / 5 + 32);
    const precip = daily.precipitation_sum[0];

    const location = locationOverride || WEATHER_LOCATION;
    return `🌤️ **Weather Report for ${location}**

${condition}, ${tempF}°F
💧 Humidity: ${humidity}% | 💨 Wind: ${wind} mph
📈 Today: High ${todayMax}°F | Low ${todayMin}°F
🌧️ Precipitation: ${precip} in`;
  } catch (error) {
    console.error('Weather error:', error);
    return "Weather data unavailable";
  }
}

export const weatherReport: ToolDef = {
  name: 'weather_report',
  description: `Get weather and pollen report for any location (configurable via env)`,
  schema: z.object({
    includePollen: z.boolean().default(true),
    location: z.string().optional().describe('Location name to display (coordinates from env)'),
  }),
  execute: async (args: unknown) => {
    const { includePollen = true, location } = args as { includePollen?: boolean; location?: string };
    const weather = await getWeatherReport(location);
    if (includePollen) {
      const pollen = await getPollenData();
      return `${weather}\n\n${pollen}`;
    }
    return weather;
  },
};

export const tools = [weatherReport];
