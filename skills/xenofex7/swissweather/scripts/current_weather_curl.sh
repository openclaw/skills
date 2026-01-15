#!/bin/bash
# Get current weather from Swiss MeteoSwiss measurement stations using curl
# No dependencies required - uses curl which is available on most systems

CURRENT_WEATHER_URL="https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Get current weather from Swiss MeteoSwiss stations

OPTIONS:
    -s, --station CODE    Show weather for specific station (e.g., RAG, BER, ZRH)
    -l, --list            List all available stations
    -a, --all             Show all stations with data
    -h, --help            Show this help message

EXAMPLES:
    $(basename "$0") --station RAG        # Rapperswil weather
    $(basename "$0") --station ZRH        # Zurich Airport
    $(basename "$0") --list                # List all stations

POPULAR STATIONS:
    BER - Bern, ZRH - Zurich Airport, BAS - Basel, GVE - Geneva,
    LUG - Lugano, RAG - Rapperswil, SMA - Säntis, KLO - Kloten
EOF
}

# Fetch weather data
fetch_data() {
    curl -s "$CURRENT_WEATHER_URL"
}

# List all stations
list_stations() {
    echo ""
    echo "Available MeteoSwiss stations:"
    echo "=============================="
    fetch_data | awk -F';' 'NR>1 {printf "%-8s %s\n", $1, $2}' | head -50
    echo ""
    echo "Use --station CODE to see detailed weather data"
}

# Show specific station
show_station() {
    local station="$1"
    local data=$(fetch_data | awk -F';' -v st="$station" 'toupper($1) == toupper(st) {print}')
    
    if [ -z "$data" ]; then
        echo "Error: Station '$station' not found. Use --list to see available stations." >&2
        exit 1
    fi
    
    # Parse CSV line
    IFS=';' read -ra FIELDS <<< "$data"
    
    echo ""
    echo "============================================================"
    echo "Station: ${FIELDS[0]}"
    
    # Parse date (format: YYYYMMDDHHMM)
    local date="${FIELDS[1]}"
    local year="${date:0:4}"
    local month="${date:4:2}"
    local day="${date:6:2}"
    local hour="${date:8:2}"
    local min="${date:10:2}"
    echo "Time: $year-$month-$day $hour:$min UTC"
    echo "============================================================"
    
    # Display weather data
    format_value() {
        [ "$1" = "-" ] && echo "N/A" || echo "$1"
    }
    
    printf "%-40s %s\n" "Temperature (°C)" "$(format_value ${FIELDS[2]})"
    printf "%-40s %s\n" "Precipitation (mm)" "$(format_value ${FIELDS[3]})"
    printf "%-40s %s\n" "Sunshine duration (min)" "$(format_value ${FIELDS[4]})"
    printf "%-40s %s\n" "Global radiation (W/m²)" "$(format_value ${FIELDS[5]})"
    printf "%-40s %s\n" "Rel. humidity (%)" "$(format_value ${FIELDS[6]})"
    printf "%-40s %s\n" "Dew point (°C)" "$(format_value ${FIELDS[7]})"
    printf "%-40s %s\n" "Wind direction (°)" "$(format_value ${FIELDS[8]})"
    printf "%-40s %s\n" "Wind speed (km/h)" "$(format_value ${FIELDS[9]})"
    printf "%-40s %s\n" "Wind gust (km/h)" "$(format_value ${FIELDS[10]})"
    printf "%-40s %s\n" "Pressure station (hPa)" "$(format_value ${FIELDS[11]})"
    printf "%-40s %s\n" "Pressure sea level QFF (hPa)" "$(format_value ${FIELDS[12]})"
    printf "%-40s %s\n" "Pressure sea level QNH (hPa)" "$(format_value ${FIELDS[13]})"
    echo ""
}

# Show all stations
show_all() {
    local data=$(fetch_data)
    echo "$data" | awk -F';' 'NR>1 {print $1}' | while read -r station; do
        show_station "$station"
    done
}

# Parse arguments
if [ $# -eq 0 ]; then
    usage
    exit 0
fi

while [ $# -gt 0 ]; do
    case "$1" in
        -s|--station)
            shift
            show_station "$1"
            exit 0
            ;;
        -l|--list)
            list_stations
            exit 0
            ;;
        -a|--all)
            show_all
            exit 0
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: Unknown option '$1'" >&2
            usage
            exit 1
            ;;
    esac
    shift
done
