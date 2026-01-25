#!/bin/bash
# IBKR Trading Setup Script
# Run this to set up the complete IBKR trading environment

set -e

TRADING_DIR="${1:-$HOME/trading}"

echo "🏦 IBKR Trading Setup"
echo "====================="
echo "Installing to: $TRADING_DIR"
echo ""

# Create directory
mkdir -p "$TRADING_DIR"
cd "$TRADING_DIR"

# Check for Java
if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Install with:"
    echo "   sudo apt-get install -y openjdk-17-jre-headless"
    exit 1
fi
echo "✅ Java found: $(java -version 2>&1 | head -1)"

# Check for Chrome/Chromium
if ! command -v chromium-browser &> /dev/null && ! command -v google-chrome &> /dev/null; then
    echo "❌ Chrome/Chromium not found. Install with:"
    echo "   sudo apt-get install -y chromium-browser chromium-chromedriver"
    exit 1
fi
echo "✅ Chrome found"

# Check for Xvfb
if ! command -v Xvfb &> /dev/null; then
    echo "❌ Xvfb not found. Install with:"
    echo "   sudo apt-get install -y xvfb"
    exit 1
fi
echo "✅ Xvfb found"

# Download Client Portal Gateway if not exists
if [ ! -d "clientportal" ]; then
    echo ""
    echo "📥 Downloading IBKR Client Portal Gateway..."
    wget -q https://download2.interactivebrokers.com/portal/clientportal.gw.zip
    unzip -q clientportal.gw.zip -d clientportal
    rm clientportal.gw.zip
    echo "✅ Client Portal Gateway installed"
else
    echo "✅ Client Portal Gateway already exists"
fi

# Create Python venv
if [ ! -d "venv" ]; then
    echo ""
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q ibeam requests urllib3
    echo "✅ Python environment ready"
else
    echo "✅ Python venv already exists"
fi

# Create .env template if not exists
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# IBKR Credentials - EDIT THESE
IBEAM_ACCOUNT=your_username
IBEAM_PASSWORD='your_password'

# Paths (auto-configured)
IBEAM_GATEWAY_DIR=${TRADING_DIR}/clientportal
IBEAM_CHROME_DRIVER_PATH=/usr/bin/chromedriver

# 2FA Settings
IBEAM_TWO_FA_SELECT_TARGET="IB Key"
IBEAM_OAUTH_TIMEOUT=180
IBEAM_PAGE_LOAD_TIMEOUT=60
EOF
    sed -i "s|\${TRADING_DIR}|$TRADING_DIR|g" .env
    echo "✅ Created .env template - EDIT WITH YOUR CREDENTIALS"
else
    echo "✅ .env already exists"
fi

# Create start script
cat > start-gateway.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/clientportal"
if pgrep -f "GatewayStart" > /dev/null; then
    echo "Gateway already running"
else
    bash bin/run.sh root/conf.yaml &
    echo "Gateway starting on https://localhost:5000"
fi
EOF
chmod +x start-gateway.sh

# Create auth script
cat > authenticate.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
source .env

# Start Xvfb if not running
if ! pgrep -x Xvfb > /dev/null; then
    Xvfb :99 -screen 0 1024x768x24 &
    sleep 2
fi

export DISPLAY=:99
export IBEAM_ACCOUNT
export IBEAM_PASSWORD
export IBEAM_GATEWAY_DIR
export IBEAM_CHROME_DRIVER_PATH
export IBEAM_TWO_FA_SELECT_TARGET
export IBEAM_OAUTH_TIMEOUT
export IBEAM_PAGE_LOAD_TIMEOUT

echo "📱 Starting authentication - CHECK YOUR PHONE for IBKR Key!"
python -m ibeam --authenticate
EOF
chmod +x authenticate.sh

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your IBKR credentials"
echo "2. Run: ./start-gateway.sh"
echo "3. Wait 20 seconds"
echo "4. Run: ./authenticate.sh"
echo "5. Approve IBKR Key notification on your phone"
echo "=========================================="
