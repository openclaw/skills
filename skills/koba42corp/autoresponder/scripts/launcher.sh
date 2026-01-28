#!/bin/bash

# iMessage Auto-Responder Launcher
# Simplified start/stop/status management

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WATCHER_SCRIPT="$SCRIPT_DIR/watcher.js"
PID_FILE="$HOME/clawd/data/imsg-autoresponder.pid"
LOG_FILE="$HOME/clawd/logs/imsg-autoresponder.log"

case "$1" in
  start)
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      echo "✗ Auto-responder is already running (PID $(cat "$PID_FILE"))"
      exit 1
    fi
    
    echo "Starting iMessage auto-responder..."
    nohup node "$WATCHER_SCRIPT" >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "✓ Auto-responder started (PID $!)"
    echo "  Logs: $LOG_FILE"
    ;;
    
  stop)
    if [ ! -f "$PID_FILE" ]; then
      echo "✗ Auto-responder is not running (no PID file)"
      exit 1
    fi
    
    PID=$(cat "$PID_FILE")
    if ! kill -0 "$PID" 2>/dev/null; then
      echo "✗ Auto-responder is not running (stale PID file)"
      rm "$PID_FILE"
      exit 1
    fi
    
    echo "Stopping iMessage auto-responder (PID $PID)..."
    kill "$PID"
    rm "$PID_FILE"
    echo "✓ Auto-responder stopped"
    ;;
    
  restart)
    "$0" stop
    sleep 2
    "$0" start
    ;;
    
  status)
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      echo "✓ Auto-responder is RUNNING (PID $(cat "$PID_FILE"))"
      echo "  Logs: $LOG_FILE"
      echo ""
      echo "Recent activity:"
      tail -10 "$LOG_FILE" | sed 's/^/  /'
    else
      echo "✗ Auto-responder is NOT running"
      if [ -f "$PID_FILE" ]; then
        rm "$PID_FILE"
      fi
    fi
    ;;
    
  logs)
    if [ -f "$LOG_FILE" ]; then
      tail -f "$LOG_FILE"
    else
      echo "✗ No log file found at $LOG_FILE"
    fi
    ;;
    
  *)
    echo "Usage: $0 {start|stop|restart|status|logs}"
    exit 1
    ;;
esac
