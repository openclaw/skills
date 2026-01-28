#!/bin/bash
# PRISM Fear & Greed Widget
# Usage: ./fear-greed.sh [--json]

PRISM_URL="${PRISM_URL:-https://strykr-prism.up.railway.app}"

# Fetch data
DATA=$(curl -s "$PRISM_URL/market/fear-greed")
VALUE=$(echo "$DATA" | jq -r '.value // 50')
LABEL=$(echo "$DATA" | jq -r '.label // "Neutral"')

# JSON output
if [ "$1" == "--json" ]; then
  echo "$DATA"
  exit 0
fi

# Calculate bar
BAR_FILLED=$((VALUE / 5))
BAR_EMPTY=$((20 - BAR_FILLED))
BAR=$(printf '█%.0s' $(seq 1 $BAR_FILLED))$(printf '░%.0s' $(seq 1 $BAR_EMPTY))

# Emoji based on value
if [ "$VALUE" -le 25 ]; then
  EMOJI="😱"
  COLOR="Extreme Fear"
elif [ "$VALUE" -le 45 ]; then
  EMOJI="😰"
  COLOR="Fear"
elif [ "$VALUE" -le 55 ]; then
  EMOJI="😐"
  COLOR="Neutral"
elif [ "$VALUE" -le 75 ]; then
  EMOJI="😀"
  COLOR="Greed"
else
  EMOJI="🤑"
  COLOR="Extreme Greed"
fi

# Pretty print
cat << EOF

📊 Crypto Fear & Greed Index

   ┌─────────────────────┐
   │                     │
   │         $VALUE          │
   │       $LABEL       │
   │         $EMOJI          │
   │                     │
   │  $BAR │
   │                     │
   └─────────────────────┘

   Sentiment: $COLOR
   Updated: $(date -u +"%Y-%m-%d %H:%M UTC")

EOF
