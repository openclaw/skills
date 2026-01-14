#!/bin/bash
# Cron job script for 7am CST weather report
# Sends report to Telegram

cd /Users/sethrose/Developer/Github/Talon

# Load environment variables from .env
if [[ -f .env ]]; then
  export $(grep -v '^#' .env | xargs)
fi

# Validate required env vars
if [[ -z "$TELEGRAM_TOKEN" ]]; then
  echo "Error: TELEGRAM_TOKEN not set in .env"
  exit 1
fi

CHAT_ID="${TELEGRAM_CHAT_ID:-7667884018}"  # Default to Seth's chat ID if not set

# Get weather data from Open-Meteo (free, no API key)
WEATHER=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=33.3506&longitude=-96.3175&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=America/Chicago")

# Parse weather with jq
TEMP=$(echo "$WEATHER" | jq -r '.current.temperature_2m | round // 0')
HUMIDITY=$(echo "$WEATHER" | jq -r '.current.relative_humidity_2m // 0')
WIND=$(echo "$WEATHER" | jq -r '.current.wind_speed_10m // 0')
CONDITION=$(echo "$WEATHER" | jq -r '.current.weather_code // 0')

# Weather condition mapping
get_weather_icon() {
  local code=$1
  case $code in
    0) echo "☀️" ;;
    1) echo "🌤️" ;;
    2) echo "⛅" ;;
    3) echo "☁️" ;;
    45|48) echo "🌫️" ;;
    51|53|55) echo "🌧️" ;;
    61|63|65) echo "🌧️" ;;
    71|73|75) echo "❄️" ;;
    80|81|82) echo "🌦️" ;;
    95|96|99) echo "⛈️" ;;
    *) echo "" ;;
  esac
}

get_weather_desc() {
  local code=$1
  case $code in
    0) echo "Clear sky" ;;
    1) echo "Mainly clear" ;;
    2) echo "Partly cloudy" ;;
    3) echo "Overcast" ;;
    45|48) echo "Foggy" ;;
    51|53|55) echo "Drizzle" ;;
    61|63|65) echo "Rain" ;;
    71|73|75) echo "Snow" ;;
    80|81|82) echo "Showers" ;;
    95|96|99) echo "Thunderstorm" ;;
    *) echo "Unknown" ;;
  esac
}

COND_ICON=$(get_weather_icon "$CONDITION")
COND_DESC=$(get_weather_desc "$CONDITION")

# Build weather message
TIMESTAMP=$(date '+%I:%M %p CST')
MESSAGE="${COND_ICON} *Morning Weather Report - Anna, TX*
━━━━━━━━━━━━━━━
• *Currently:* ${COND_DESC}, ${TEMP}°F
• *Humidity:* ${HUMIDITY}%
• *Wind:* ${WIND} mph

🌿 *Pollen Levels*
• _Pollen: Check pollen.com_

_Report: ${TIMESTAMP}_"

# Send to Telegram
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" \
  -d "text=${MESSAGE}" \
  -d "parse_mode=Markdown" > /dev/null

echo "[Sent at ${TIMESTAMP}]"
