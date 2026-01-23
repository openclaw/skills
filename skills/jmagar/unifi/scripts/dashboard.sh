#!/bin/bash
# UniFi Network Dashboard - Comprehensive overview
# Usage: bash dashboard.sh [json]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/unifi-api.sh"
OUTPUT_FILE="$HOME/clawd/memory/bank/unifi-inventory.md"

# Disable strict mode for dashboard (we handle errors gracefully)
set +e

OUTPUT_JSON="${1:-}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Create shared session for all requests
export UNIFI_COOKIE_FILE=$(mktemp)
trap "rm -f '$UNIFI_COOKIE_FILE'" EXIT
unifi_login "$UNIFI_COOKIE_FILE"

# Fetch all data upfront (using full API path format)
HEALTH=$(unifi_get "/api/s/$UNIFI_SITE/stat/health")
DEVICES=$(unifi_get "/api/s/$UNIFI_SITE/stat/device")
CLIENTS=$(unifi_get "/api/s/$UNIFI_SITE/stat/sta")
PORTFWD=$(unifi_get "/api/s/$UNIFI_SITE/rest/portforward")
FWRULES=$(unifi_get "/api/s/$UNIFI_SITE/rest/firewallrule")
NETWORKS=$(unifi_get "/api/s/$UNIFI_SITE/rest/networkconf")
WLANS=$(unifi_get "/api/s/$UNIFI_SITE/rest/wlanconf")
ALARMS=$(unifi_get "/api/s/$UNIFI_SITE/stat/alarm")
ROUTING=$(unifi_get "/api/s/$UNIFI_SITE/stat/routing")
SYSINFO=$(unifi_get "/api/s/$UNIFI_SITE/stat/sysinfo")

# Debug: Dump all JSON to a file for troubleshooting
jq -n \
    --argjson health "$HEALTH" \
    --argjson devices "$DEVICES" \
    --argjson clients "$CLIENTS" \
    --argjson portforward "$PORTFWD" \
    --argjson networks "$NETWORKS" \
    --argjson wlans "$WLANS" \
    '{health: $health, devices: $devices, clients: $clients, networks: $networks, wlans: $wlans}' \
    > dashboard_debug_dump.json 2>/dev/null

if [ "$OUTPUT_JSON" = "json" ]; then
    jq -n \
        --argjson health "$HEALTH" \
        --argjson devices "$DEVICES" \
        --argjson clients "$CLIENTS" \
        --argjson portforward "$PORTFWD" \
        --argjson firewall "$FWRULES" \
        --argjson networks "$NETWORKS" \
        --argjson wlans "$WLANS" \
        --argjson alarms "$ALARMS" \
        --argjson routing "$ROUTING" \
        --argjson sysinfo "$SYSINFO" \
        '{health: $health, devices: $devices, clients: $clients, portforward: $portforward, firewall: $firewall, networks: $networks, wlans: $wlans, alarms: $alarms, routing: $routing, sysinfo: $sysinfo}'
    exit 0
fi

# Generate dashboard output and save to file
{
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                        UNIFI NETWORK DASHBOARD                               ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""

    # System Info
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ SYSTEM INFO                                                                  │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    echo "$SYSINFO" | jq -r '
        .data[0] | 
        "Version: \(.version // "N/A") | Hostname: \(.hostname // "N/A") | Timezone: \(.timezone // "N/A")"
    ' 2>/dev/null || echo "  Unable to fetch system info"
    echo ""

    # Health Overview
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ HEALTH STATUS                                                                │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    echo "$HEALTH" | jq -r '
        .data[] | 
        "\(.subsystem | ascii_upcase): \(if .status == "ok" then "✅ OK" else "⚠️  \(.status)" end) | Gateways: \(.gw_mac // "N/A") | Clients: \(.num_user // 0)"
    ' 2>/dev/null | head -10
    echo ""

    # Devices
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ UNIFI DEVICES                                                                │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    printf "%-20s %-10s %-15s %-8s %-10s %-8s\n" "NAME" "MODEL" "IP" "STATE" "UPTIME" "CLIENTS"
    printf "%-20s %-10s %-15s %-8s %-10s %-8s\n" "----" "-----" "--" "-----" "------" "-------"
    echo "$DEVICES" | jq -r '
        .data[] | 
        [
            ((.name // .hostname // .mac)[:20]),
            ((.model // "N/A")[:10]),
            ((.ip // "N/A")[:15]),
            (if .state == 1 then "✅" else "❌" end),
            (((.uptime // 0) / 3600 | floor | tostring + "h")),
            ((.num_sta // 0 | tostring))
        ] | @tsv
    ' 2>/dev/null | while IFS=$'\t' read -r name model ip state uptime clients; do
        printf "%-20s %-10s %-15s %-8s %-10s %-8s\n" "$name" "$model" "$ip" "$state" "$uptime" "$clients"
    done
    echo ""

    # Client Summary
    TOTAL_CLIENTS=$(echo "$CLIENTS" | jq '.data | length' 2>/dev/null || echo 0)
    WIRED_CLIENTS=$(echo "$CLIENTS" | jq '[.data[] | select(.is_wired == true)] | length' 2>/dev/null || echo 0)
    WIFI_CLIENTS=$(echo "$CLIENTS" | jq '[.data[] | select(.is_wired == false)] | length' 2>/dev/null || echo 0)

    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ CLIENTS: $TOTAL_CLIENTS total ($WIRED_CLIENTS wired, $WIFI_CLIENTS wireless)                                       │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    printf "%-25s %-15s %-18s %-10s %-12s\n" "HOSTNAME" "IP" "MAC" "TYPE" "TX/RX MB/s"
    printf "%-25s %-15s %-18s %-10s %-12s\n" "--------" "--" "---" "----" "----------"
    echo "$CLIENTS" | jq -r '
        .data | sort_by(-(.["wired-rx_bytes"] // .rx_bytes // 0)) | .[0:15] | .[] |
        [
            ((.name // .hostname // .mac // "Unknown") | tostring | .[:25]),
            ((.ip // .last_ip // "N/A") | tostring | .[:15]),
            ((.mac // "N/A") | tostring | .[:18]),
            (if .is_wired == true then "Wired" else "WiFi" end),
            "\( ((.["tx_bytes-r"] // .["wired-tx_bytes-r"] // 0) / 1000000 * 10 | floor / 10) )/\( ((.["rx_bytes-r"] // .["wired-rx_bytes-r"] // 0) / 1000000 * 10 | floor / 10) )"
        ] | @tsv
    ' 2>/dev/null | while IFS=$'\t' read -r hostname ip mac type rate; do
        printf "%-25s %-15s %-18s %-10s %-12s\n" "$hostname" "$ip" "$mac" "$type" "$rate"
    done || echo "  (error parsing client data)"
    echo "  (showing top 15 by traffic)"
    echo ""

    # Networks
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ NETWORKS                                                                     │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    printf "%-25s %-8s %-18s %-10s %-15s\n" "NAME" "VLAN" "SUBNET" "PURPOSE" "DHCP"
    printf "%-25s %-8s %-18s %-10s %-15s\n" "----" "----" "------" "-------" "----"
    # Check if networks returned an error
    if echo "$NETWORKS" | jq -e '.error' >/dev/null 2>&1; then
        echo "  (API returned 401 - REST endpoints may require additional permissions)"
    else
        echo "$NETWORKS" | jq -r '
        .data[] | 
        [
            ((.name // "N/A") | tostring | .[:25]),
            ((.vlan // "-") | tostring | .[:8]),
            ((.ip_subnet // "N/A") | tostring | .[:18]),
            ((.purpose // "N/A") | tostring | .[:10]),
            (if .dhcpd_enabled == true then "Enabled" else "Disabled" end)
        ] | @tsv
    ' 2>/dev/null | while IFS=$'\t' read -r name vlan subnet purpose dhcp; do
        printf "%-25s %-8s %-18s %-10s %-15s\n" "$name" "$vlan" "$subnet" "$purpose" "$dhcp"
    done
    fi
    echo ""

    # WLANs
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ WIRELESS NETWORKS                                                            │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    printf "%-30s %-10s %-15s %-10s\n" "SSID" "ENABLED" "SECURITY" "BAND"
    printf "%-30s %-10s %-15s %-10s\n" "----" "-------" "--------" "----"
    # Check if wlans returned an error
    if echo "$WLANS" | jq -e '.error' >/dev/null 2>&1; then
        echo "  (API returned 401 - REST endpoints may require additional permissions)"
    else
        echo "$WLANS" | jq -r '
        .data[] | 
        [
            ((.name // "N/A") | tostring | .[:30]),
            (if .enabled == true then "✅" else "❌" end),
            ((.security // "open") | tostring | .[:15]),
            ((if .wlan_band then .wlan_band else "both" end) | tostring | .[:10])
        ] | @tsv
    ' 2>/dev/null | while IFS=$'\t' read -r ssid enabled security band; do
        printf "%-30s %-10s %-15s %-10s\n" "$ssid" "$enabled" "$security" "$band"
    done
    fi
    echo ""

    # Port Forwards
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ PORT FORWARDS                                                                │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    PF_COUNT=$(echo "$PORTFWD" | jq '.data | length' 2>/dev/null || echo 0)
    if [ "$PF_COUNT" -eq 0 ]; then
        echo "  No port forwards configured"
    else
        printf "%-25s %-10s %-8s %-15s %-8s %-10s\n" "NAME" "ENABLED" "PROTO" "FWD TO" "PORT" "SRC PORT"
        printf "%-25s %-10s %-8s %-15s %-8s %-10s\n" "----" "-------" "-----" "------" "----" "--------"
        echo "$PORTFWD" | jq -r '
            .data[] | 
            [
                ((.name // "N/A") | tostring | .[:25]),
                (if .enabled == true then "✅" else "❌" end),
                ((.proto // "tcp") | tostring | .[:8]),
                ((.fwd // "N/A") | tostring | .[:15]),
                ((.fwd_port // "-") | tostring | .[:8]),
                ((.src_port // .dst_port // "-") | tostring | .[:10])
            ] | @tsv
        ' 2>/dev/null | while IFS=$'\t' read -r name enabled proto fwd port srcport; do
            printf "%-25s %-10s %-8s %-15s %-8s %-10s\n" "$name" "$enabled" "$proto" "$fwd" "$port" "$srcport"
        done
    fi
    echo ""

    # Firewall Rules
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ FIREWALL RULES                                                               │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    FW_COUNT=$(echo "$FWRULES" | jq '.data | length' 2>/dev/null || echo 0)
    if [ "$FW_COUNT" -eq 0 ]; then
        echo "  No custom firewall rules configured"
    else
        printf "%-25s %-10s %-10s %-10s %-10s %-10s\n" "NAME" "ENABLED" "ACTION" "PROTO" "RULESET" "INDEX"
        printf "%-25s %-10s %-10s %-10s %-10s %-10s\n" "----" "-------" "------" "-----" "-------" "-----"
        echo "$FWRULES" | jq -r '
            .data | sort_by(.rule_index) | .[] | 
            [
                ((.name // "N/A") | tostring | .[:25]),
                (if .enabled == true then "✅" else "❌" end),
                ((.action // "N/A") | tostring | .[:10]),
                ((.protocol // "all") | tostring | .[:10]),
                ((.ruleset // "N/A") | tostring | .[:10]),
                ((.rule_index // 0) | tostring)
            ] | @tsv
        ' 2>/dev/null | while IFS=$'\t' read -r name enabled action proto ruleset idx; do
            printf "%-25s %-10s %-10s %-10s %-10s %-10s\n" "$name" "$enabled" "$action" "$proto" "$ruleset" "$idx"
        done
    fi
    echo ""

    # Static Routes
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ ROUTES                                                                       │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    ROUTE_COUNT=$(echo "$ROUTING" | jq '.data | length' 2>/dev/null || echo 0)
    if [ "$ROUTE_COUNT" -eq 0 ]; then
        echo "  No static routes (using default)"
    else
        printf "%-20s %-18s %-15s %-12s %-10s\n" "NAME" "DESTINATION" "NEXT HOP" "INTERFACE" "METRIC"
        printf "%-20s %-18s %-15s %-12s %-10s\n" "----" "-----------" "--------" "---------" "------"
        echo "$ROUTING" | jq -r '
            .data[] | 
            [
                ((.name // .pfx // "N/A") | tostring | .[:20]),
                ((.pfx // "N/A") | tostring | .[:18]),
                ((.nh[0].t // .nh[0].gw // "N/A") | tostring | .[:15]),
                ((.nh[0].intf_name // "N/A") | tostring | .[:12]),
                ((.metric // 0) | tostring)
            ] | @tsv
        ' 2>/dev/null | head -10 | while IFS=$'\t' read -r name dest nexthop intf metric; do
            printf "%-20s %-18s %-15s %-12s %-10s\n" "$name" "$dest" "$nexthop" "$intf" "$metric"
        done
    fi
    echo ""

    # Recent Alarms
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ RECENT ALARMS (last 10)                                                      │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    ALARM_COUNT=$(echo "$ALARMS" | jq '.data | length' 2>/dev/null || echo 0)
    if [ "$ALARM_COUNT" -eq 0 ]; then
        echo "  ✅ No recent alarms"
    else
        printf "%-20s %-50s\n" "TIME" "MESSAGE"
        printf "%-20s %-50s\n" "----" "-------"
        echo "$ALARMS" | jq -r '
            .data | sort_by(-.time) | .[0:10] | .[] |
            [
                ((.datetime // (.time | todate? // "N/A"))[:20]),
                ((.msg // .key // "N/A")[:50])
            ] | @tsv
        ' 2>/dev/null | while IFS=$'\t' read -r time msg; do
            printf "%-20s %-50s\n" "$time" "$msg"
        done
    fi
    echo ""

    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║  Dashboard generated at $(date '+%Y-%m-%d %H:%M:%S')                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
} | tee "$OUTPUT_FILE"
