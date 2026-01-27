#!/bin/bash
SKILL_DIR="$(dirname "$(realpath "$0")")"
SERVER_DIR="$HOME/hytale_server"
DOWNLOADER="$SERVER_DIR/hytale-downloader"
SCREEN_NAME="hytale"
JAR_NAME="hytale-server.jar"
DOWNLOAD_URL="https://downloader.hytale.com/hytale-downloader.zip"

mkdir -p "$SERVER_DIR"

case "$1" in
  start)
    if screen -list | grep -q "$SCREEN_NAME"; then
      echo "Server is already running."
    else
      echo "Starting Hytale server..."
      cd "$SERVER_DIR"
      if [ ! -f "$JAR_NAME" ]; then
        echo "Error: $JAR_NAME not found in $SERVER_DIR."
        echo "Please run 'hytale update' to download server files."
        exit 1
      fi
      # Default 4GB RAM, can be adjusted
      screen -dmS "$SCREEN_NAME" java -Xmx4G -jar "$JAR_NAME"
      echo "Server started in screen session '$SCREEN_NAME'."
    fi
    ;;
  stop)
    if screen -list | grep -q "$SCREEN_NAME"; then
      echo "Stopping server..."
      screen -S "$SCREEN_NAME" -X stuff "stop^M"
      echo "Stop command sent."
    else
      echo "Server is not running."
    fi
    ;;
  update)
    echo "Checking for Hytale Downloader..."
    
    # Check if downloader exists in server dir; if not, check for the linux binary specifically if user unzipped it
    if [ ! -f "$DOWNLOADER" ]; then
        # Try to find the linux binary if the generic name isn't there
        if [ -f "$SERVER_DIR/hytale-downloader-linux-amd64" ]; then
            DOWNLOADER="$SERVER_DIR/hytale-downloader-linux-amd64"
        else
            echo "Error: Hytale Downloader not found in $SERVER_DIR."
            echo "Please download it from: $DOWNLOAD_URL"
            echo "Unzip it and place the binary (hytale-downloader-linux-amd64) in $SERVER_DIR"
            echo "Make sure to mark it executable: chmod +x $SERVER_DIR/hytale-downloader-linux-amd64"
            exit 1
        fi
    fi

    echo "Running Hytale Downloader..."
    cd "$SERVER_DIR"
    
    # Use explicit credentials file if present
    CRED_ARG=""
    if [ -f "hytale-downloader-credentials.json" ]; then
        CRED_ARG="-credentials-path hytale-downloader-credentials.json"
    fi

    chmod +x "$DOWNLOADER"
    "$DOWNLOADER" -download-path "$SERVER_DIR" $CRED_ARG
    ;;
  status)
    if screen -list | grep -q "$SCREEN_NAME"; then
      PID=$(screen -list | grep "$SCREEN_NAME" | cut -d. -f1 | awk '{print $1}')
      echo "Server is ONLINE (PID: $PID)."
    else
      echo "Server is OFFLINE."
    fi
    ;;
  console)
    echo "To attach manually: screen -r $SCREEN_NAME"
    ;;
  *)
    echo "Usage: $0 {start|stop|update|status}"
    exit 1
    ;;
esac
