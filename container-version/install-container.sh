#!/bin/bash
set -e

echo "🐋 Installing RPi Chat Server (Podman Container Version)"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run as regular user (not root/sudo)"
    echo "   The script will ask for sudo when needed"
    exit 1
fi

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
        echo "❌ Unable to detect distribution"
        exit 1
    fi
}

detect_distro

echo "📋 Detected distribution: $DISTRO"
echo ""

# Install Podman based on distro
if [[ "$DISTRO" == "void" ]]; then
    echo "📦 Installing Podman (Void Linux)..."
    sudo xbps-install -Su
    sudo xbps-install -y podman

elif [[ "$DISTRO" == "debian" ]] || [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "raspbian" ]] || [[ "$DISTRO" == "dietpi" ]]; then
    echo "📦 Installing Podman (Debian/Ubuntu/DietPi)..."
    sudo apt-get update
    sudo apt-get install -y podman

else
    echo "❌ Unsupported distribution: $DISTRO"
    echo "   Supported: Void Linux, Debian, Ubuntu, Raspbian, DietPi"
    exit 1
fi

# Verify Podman installation
if ! command -v podman &> /dev/null; then
    echo "❌ Podman installation failed"
    exit 1
fi

echo "✅ Podman installed: $(podman --version)"
echo ""

# Create data directories
echo "📁 Creating data directories..."
mkdir -p "$HOME/rpi-chat-data/uploads"
touch "$HOME/rpi-chat-data/chat.db"

# Build and run container
echo "🔨 Building container..."
./build-and-run.sh

# Ask about systemd service
echo ""
read -p "📋 Install systemd service for auto-start? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "⚙️  Installing systemd service..."

    # Update service file with current user
    sed "s|User=.*|User=$USER|g" rpi-chat-podman.service > /tmp/rpi-chat-podman.service

    # Install service
    sudo mv /tmp/rpi-chat-podman.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable rpi-chat-podman

    echo "✅ Systemd service installed"
    echo "   Start: sudo systemctl start rpi-chat-podman"
    echo "   Stop:  sudo systemctl stop rpi-chat-podman"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Installation Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")

echo "📱 Access: http://$LOCAL_IP:5000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 Add HTTPS with Tailscale (Recommended):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Run: ./setup-tailscale.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛠️  Useful Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View logs:    podman logs -f rpi-chat"
echo "Restart:      podman restart rpi-chat"
echo "Stop:         podman stop rpi-chat"
echo "Start:        podman start rpi-chat"
echo "Rebuild:      ./build-and-run.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
