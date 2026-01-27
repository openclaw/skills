#!/bin/bash
# Install WHOOP skill dependencies
set -e

echo "Installing WHOOP skill dependencies..."
pip3 install requests
echo ""
echo "✅ Dependencies installed."
echo ""
echo "Next steps:"
echo "  1. Register an app at https://developer.whoop.com"
echo "  2. Create credentials file:"
echo "     mkdir -p ~/.whoop"
echo '     echo '"'"'{"client_id": "YOUR_ID", "client_secret": "YOUR_SECRET"}'"'"' > ~/.whoop/credentials.json'
echo "     chmod 600 ~/.whoop/credentials.json"
echo ""
echo "  3. Complete OAuth authorization (see references/oauth.md)"
