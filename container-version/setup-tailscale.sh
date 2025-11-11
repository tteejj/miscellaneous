#!/bin/bash
set -e

echo "🔐 Setting up Tailscale HTTPS for RPi Chat"
echo ""

# Detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif command -v xbps-install &> /dev/null; then
        DISTRO="void"
    elif command -v apt-get &> /dev/null; then
        DISTRO="debian"
    else
        DISTRO="unknown"
    fi
}

detect_distro

# Check if Tailscale is installed
if ! command -v tailscale &> /dev/null; then
    echo "📦 Installing Tailscale..."

    if [[ "$DISTRO" == "void" ]]; then
        echo "📋 Detected: Void Linux"
        sudo xbps-install -y tailscale
        # Enable and start tailscaled service on Void
        sudo ln -sf /etc/sv/tailscaled /var/service/
        sudo sv up tailscaled
    else
        echo "📋 Detected: $DISTRO (using official installer)"
        curl -fsSL https://tailscale.com/install.sh | sh
    fi

    echo "✅ Tailscale installed"
else
    echo "✅ Tailscale already installed: $(tailscale version)"
fi

# Check if already logged in
if ! sudo tailscale status &> /dev/null; then
    echo ""
    echo "🔑 Please authenticate with Tailscale..."
    echo "   A browser window will open to complete authentication"
    echo ""
    sudo tailscale up
else
    echo "✅ Already logged into Tailscale"
fi

# Get Tailscale hostname
TAILSCALE_HOSTNAME=$(sudo tailscale status --json | grep -o '"DNSName":"[^"]*"' | cut -d'"' -f4 | sed 's/\.$//')

if [ -z "$TAILSCALE_HOSTNAME" ]; then
    echo "❌ Could not get Tailscale hostname"
    exit 1
fi

echo ""
echo "✅ Tailscale hostname: $TAILSCALE_HOSTNAME"
echo ""

# Ask about Funnel (public access)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Choose Access Mode:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1) Private (Tailscale users only - more secure)"
echo "   Users need Tailscale installed"
echo "   Access: https://$TAILSCALE_HOSTNAME:5000"
echo ""
echo "2) Public (Tailscale Funnel - anyone with link)"
echo "   No Tailscale needed for users"
echo "   Access: https://$TAILSCALE_HOSTNAME:5000"
echo ""
read -p "Select mode (1 or 2): " -n 1 -r MODE
echo ""

if [ "$MODE" = "2" ]; then
    echo ""
    echo "🌐 Enabling Tailscale Funnel (public HTTPS)..."
    sudo tailscale funnel --bg 5000 on

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Public HTTPS Enabled!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🌍 Share this link with anyone:"
    echo "   https://$TAILSCALE_HOSTNAME:5000"
    echo ""
    echo "⚠️  Security Notes:"
    echo "   - Anyone with the link can access"
    echo "   - Your chat has login authentication ✅"
    echo "   - Consider setting strong passwords"
    echo ""
    echo "To disable public access:"
    echo "   sudo tailscale funnel --bg 5000 off"
    echo ""
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Private Tailscale Access Configured!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🔒 Users need to:"
    echo "   1. Install Tailscale on their device"
    echo "   2. Join your Tailscale network"
    echo "   3. Access: https://$TAILSCALE_HOSTNAME:5000"
    echo ""
    echo "📱 Get Tailscale:"
    echo "   https://tailscale.com/download"
    echo ""
    echo "To enable public access later:"
    echo "   sudo tailscale funnel --bg 5000 on"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Tailscale Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
sudo tailscale status
echo ""
