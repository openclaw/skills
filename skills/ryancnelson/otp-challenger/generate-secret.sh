#!/bin/bash
# Generate a new TOTP secret
#
# Usage: generate-secret.sh [account] [issuer]

ACCOUNT="${1:-user@example.com}"
ISSUER="${2:-OpenClaw}"

# Check if oathtool is available
if ! command -v oathtool &> /dev/null; then
  echo "ERROR: oathtool not found. Install with:" >&2
  echo "  macOS:  brew install oath-toolkit" >&2
  echo "  Fedora: sudo dnf install oathtool" >&2
  echo "  Ubuntu: sudo apt-get install oathtool" >&2
  exit 1
fi

# Check if qrencode is available for QR codes
if ! command -v qrencode &> /dev/null; then
  echo "WARNING: qrencode not found. Install for QR codes:" >&2
  echo "  macOS:  brew install qrencode" >&2
  echo "  Fedora: sudo dnf install qrencode" >&2
  echo "  Ubuntu: sudo apt-get install qrencode" >&2
fi

# Generate a random base32 secret (160 bits = 32 base32 chars)
SECRET=$(head -c 20 /dev/urandom | base32 | tr -d '=' | head -c 32)

echo "========================================="
echo "TOTP Secret Generated"
echo "========================================="
echo ""
echo "Account: $ACCOUNT"
echo "Issuer: $ISSUER"
echo "Secret: $SECRET"
echo ""
echo "Manual Entry Instructions:"
echo "1. Open your authenticator app"
echo "2. Choose 'Manual Entry' or 'Enter a Setup Key'"
echo "3. Enter the secret above"
echo "4. Set Time Based (TOTP)"
echo ""

# Generate otpauth:// URI
URI="otpauth://totp/$ISSUER:$ACCOUNT?secret=$SECRET&issuer=$ISSUER"
echo "URI: $URI"
echo ""

# Generate QR code if qrencode is available
if command -v qrencode &> /dev/null; then
  echo "QR Code (scan with authenticator app):"
  echo ""
  qrencode -t ANSI256 "$URI"
  echo ""
fi

echo "========================================="
echo "Configuration"
echo "========================================="
echo ""
echo "Add to ~/.openclaw/config.yaml:"
echo ""
echo "security:"
echo "  otp:"
echo "    secret: \"$SECRET\""
echo "    accountName: \"$ACCOUNT\""
echo "    issuer: \"$ISSUER\""
echo "    intervalHours: 24"
echo ""
echo "Or set environment variable:"
echo "  export OTP_SECRET=\"$SECRET\""
echo ""
