# AviationStack API Setup

## Getting Started

AviationStack provides a free tier with 100 API requests per month, which is perfect for occasional flight tracking.

### 1. Get Your Free API Key

1. Visit: https://aviationstack.com/signup/free
2. Sign up for a free account
3. Get your API access key from the dashboard

### 2. Set Up Environment Variable

Add your API key to your environment:

```bash
export AVIATIONSTACK_API_KEY='your-api-key-here'
```

To make it permanent, add this line to your shell profile:

**Bash/Zsh:**
```bash
echo "export AVIATIONSTACK_API_KEY='your-api-key-here'" >> ~/.zshrc
source ~/.zshrc
```

**Fish:**
```fish
set -Ux AVIATIONSTACK_API_KEY 'your-api-key-here'
```

### 3. Install Python Dependencies

The script requires the `requests` library:

```bash
pip3 install requests
```

## API Limits

**Free Tier:**
- 100 requests/month
- Real-time flight data
- Historical flights
- Airport/airline lookup
- HTTP only (no HTTPS)

**Paid Tiers:** (Starting at $49.99/month)
- Up to 500,000 requests/month
- HTTPS support
- Priority support
- Historical data access

## Supported Flight Number Formats

The API accepts IATA flight codes:
- `AA100` - American Airlines 100
- `UA2402` - United 2402
- `BA123` - British Airways 123
- `DL456` - Delta 456

## API Response Data

The API returns comprehensive flight information:

- **Flight Status**: Scheduled, Active, Landed, Cancelled, Delayed
- **Departure Data**: Airport, terminal, gate, scheduled/estimated/actual times
- **Arrival Data**: Airport, terminal, gate, scheduled/estimated/actual times
- **Live Tracking**: Current position (lat/lon), altitude, speed
- **Aircraft Info**: Registration, type (IATA/ICAO codes)
- **Airline Info**: Name, IATA/ICAO codes

## Alternative APIs

If you need more requests or different features, consider:

- **FlightAware AeroAPI**: Enterprise-grade, excellent historical data
- **OpenSky Network**: Free, open-source, community-driven
- **AeroDataBox**: Good pricing, comprehensive data
- **Flightradar24 API**: Real-time tracking, visual data

## Troubleshooting

**Error: "AVIATIONSTACK_API_KEY environment variable not set"**
- Make sure you've exported the environment variable
- Restart your terminal after adding to shell profile

**Error: "No flight found with that number"**
- Verify the flight number is correct (use IATA code)
- Some flights may not be in the system yet (check scheduled flights)
- Try searching on aviationstack.com first to confirm the flight exists

**API Rate Limit Exceeded:**
- Free tier allows 100 requests/month
- Track your usage or upgrade to paid tier
