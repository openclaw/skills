#!/bin/bash
# Hetzner Cloud CLI wrapper for Clawdbot
# Usage: ./hetzner.sh <command> [args]

set -e

# Load .env if exists
if [ -f "$(dirname "$0")/.env" ]; then
    export $(cat "$(dirname "$0")/.env" | xargs)
fi

if [ -z "$HCLOUD_TOKEN" ]; then
    echo "Error: HCLOUD_TOKEN not set. Run 'export HCLOUD_TOKEN=your_token'"
    exit 1
fi

# Export token for hcloud
export HCLOUD_TOKEN

COMMAND="$1"
shift || true

case "$COMMAND" in
    servers|server)
        SUBCOMMAND="$1"
        shift || true
        case "$SUBCOMMAND" in
            list|ls)
                hcloud server list --output json 2>/dev/null | jq -r '.[] | "\(.id): \(.name) - \(.status) @ \(.public_net.ipv4.ip // "none")"' || hcloud server list
                ;;
            get)
                hcloud server describe "$1"
                ;;
            create)
                NAME="$1"; TYPE="$2"; IMAGE="$3"; LOCATION="${4:-fsn1}"
                hcloud server create --name "$NAME" --server-type "$TYPE" --image "$IMAGE" --location "$LOCATION" --ssh-key default 2>/dev/null || \
                hcloud server create --name "$NAME" --server-type "$TYPE" --image "$IMAGE" --location "$LOCATION"
                ;;
            delete|rm)
                echo "Deleting server $1..."
                hcloud server delete "$1"
                ;;
            start)
                hcloud server poweron "$1"
                ;;
            stop|shutdown)
                hcloud server shutdown "$1"
                ;;
            reboot|reboot)
                hcloud server reboot "$1"
                ;;
            ssh)
                SERVER_IP=$(hcloud server describe "$1" -o json | jq -r '.public_net.ipv4.ip')
                if [ -n "$SERVER_IP" ] && [ "$SERVER_IP" != "null" ]; then
                    echo "Connecting to $1 at $SERVER_IP..."
                    ssh -o StrictHostKeyChecking=no root@"$SERVER_IP"
                else
                    echo "No public IP found for server $1"
                fi
                ;;
            metrics)
                hcloud server metrics --hostname "$1" --type cpu 2>/dev/null || echo "Metrics not available"
                ;;
            *)
                echo "Usage: hetzner servers <list|get|create|delete|start|stop|reboot|ssh|metrics>"
                ;;
        esac
        ;;
    
    networks|network)
        SUBCOMMAND="$1"
        shift || true
        case "$SUBCOMMAND" in
            list|ls)
                hcloud network list
                ;;
            get)
                hcloud network describe "$1"
                ;;
            create)
                hcloud network create --name "$1" --ip-range "$2"
                ;;
            delete)
                hcloud network delete "$1"
                ;;
            *)
                echo "Usage: hetzner networks <list|get|create|delete>"
                ;;
        esac
        ;;
    
    floating-ips|floating-ip|fip)
        SUBCOMMAND="$1"
        shift || true
        case "$SUBCOMMAND" in
            list|ls)
                hcloud floating-ip list
                ;;
            get)
                hcloud floating-ip describe "$1"
                ;;
            create)
                hcloud floating-ip create --type ipv4 --home-location "$1"
                ;;
            assign)
                hcloud floating-ip assign "$1" "$2"
                ;;
            unassign)
                hcloud floating-ip unassign "$1"
                ;;
            *)
                echo "Usage: hetzner floating-ips <list|get|create|assign|unassign>"
                ;;
        esac
        ;;
    
    ssh-keys|sshkey)
        SUBCOMMAND="$1"
        shift || true
        case "$SUBCOMMAND" in
            list|ls)
                hcloud ssh-key list
                ;;
            get)
                hcloud ssh-key describe "$1"
                ;;
            create)
                hcloud ssh-key create --name "$1" --public-key "$2"
                ;;
            delete)
                hcloud ssh-key delete "$1"
                ;;
            *)
                echo "Usage: hetzner ssh-keys <list|get|create|delete>"
                ;;
        esac
        ;;
    
    volumes|volume)
        SUBCOMMAND="$1"
        shift || true
        case "$SUBCOMMAND" in
            list|ls)
                hcloud volume list
                ;;
            get)
                hcloud volume describe "$1"
                ;;
            create)
                hcloud volume create --name "$1" --size "$2" --location "$3"
                ;;
            delete)
                hcloud volume delete "$1"
                ;;
            attach)
                hcloud volume attach "$1" --server "$2"
                ;;
            detach)
                hcloud volume detach "$1"
                ;;
            *)
                echo "Usage: hetzner volumes <list|get|create|delete|attach|detach>"
                ;;
        esac
        ;;
    
    firewalls|firewall|fw)
        SUBCOMMAND="$1"
        shift || true
        case "$SUBCOMMAND" in
            list|ls)
                hcloud firewall list
                ;;
            get)
                hcloud firewall describe "$1"
                ;;
            rules)
                hcloud firewall rules "$1"
                ;;
            *)
                echo "Usage: hetzner firewalls <list|get|rules>"
                ;;
        esac
        ;;
    
    locations|location)
        hcloud location list
        ;;
    
    server-types|stypes)
        hcloud server-type list
        ;;
    
    images|image)
        SUBCOMMAND="$1"
        shift || true
        case "$SUBCOMMAND" in
            list|ls)
                hcloud image list
                ;;
            *)
                hcloud image list
                ;;
        esac
        ;;
    
    help|--help|-h)
        echo "Hetzner Cloud CLI Wrapper"
        echo ""
        echo "Commands:"
        echo "  servers <subcommand>    - Manage servers"
        echo "  networks <subcommand>   - Manage networks"
        echo "  floating-ips <subcmd>   - Manage floating IPs"
        echo "  ssh-keys <subcommand>   - Manage SSH keys"
        echo "  volumes <subcommand>    - Manage volumes"
        echo "  firewalls <subcommand>  - List firewalls"
        echo "  locations               - List locations"
        echo "  server-types            - List server types"
        echo "  images                  - List images"
        echo ""
        echo "Examples:"
        echo "  hetzner servers list"
        echo "  hetzner servers get 123"
        echo "  hetzner networks list"
        echo ""
        echo "Set HCLOUD_TOKEN env var before use."
        ;;
    
    *)
        echo "Unknown command: $COMMAND"
        echo "Run 'hetzner help' for usage"
        exit 1
        ;;
esac
