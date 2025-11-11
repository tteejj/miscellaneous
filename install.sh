#!/bin/bash
set -e

echo "🚀 Installing RPi Chat Server (systemd version)..."
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

# Install dependencies based on distro
if [[ "$DISTRO" == "void" ]]; then
    echo "📦 Updating system packages (Void Linux)..."
    sudo xbps-install -Su

    echo "📦 Installing dependencies..."
    sudo xbps-install -y python3 python3-pip python3-Pillow sqlite git

elif [[ "$DISTRO" == "debian" ]] || [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "raspbian" ]]; then
    echo "📦 Updating system packages (Debian/Ubuntu)..."
    sudo apt-get update

    echo "📦 Installing dependencies..."
    sudo apt-get install -y python3-pip python3-pil sqlite3 git

else
    echo "❌ Unsupported distribution: $DISTRO"
    echo "   Supported: Void Linux, Debian, Ubuntu, Raspbian"
    exit 1
fi

# Install Python packages (works on all distros)
echo "🐍 Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Initialize database
echo "💾 Initializing database..."
python3 database.py

# Install systemd service
echo "⚙️  Installing systemd service..."
WORKING_DIR=$(pwd)
sed "s|WorkingDirectory=.*|WorkingDirectory=$WORKING_DIR|g" rpi-chat.service > /tmp/rpi-chat.service
sed -i "s|User=.*|User=$USER|g" /tmp/rpi-chat.service
sudo mv /tmp/rpi-chat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rpi-chat
sudo systemctl start rpi-chat

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 Access Options:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🏠 Local Network (HTTP):"
echo "   http://$LOCAL_IP:5000"
echo ""
echo "🔐 For HTTPS (choose one):"
echo ""
echo "1️⃣  Tailscale Funnel (Easiest - Public HTTPS)"
if [[ "$DISTRO" == "void" ]]; then
    echo "   sudo xbps-install -y tailscale"
    echo "   sudo sv up tailscaled  # Enable service"
    echo "   sudo tailscale up"
else
    echo "   curl -fsSL https://tailscale.com/install.sh | sh"
    echo "   sudo tailscale up"
fi
echo "   tailscale funnel --bg 5000 on"
echo "   Access: https://\$(tailscale status --json | jq -r '.Self.DNSName'):5000"
echo ""
echo "2️⃣  Caddy (Public Internet with Domain)"
if [[ "$DISTRO" == "void" ]]; then
    echo "   sudo xbps-install -y caddy"
else
    echo "   sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https"
    echo "   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg"
    echo "   echo 'deb [signed-by=/usr/share/keyrings/caddy-stable-archive-keyring.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main' | sudo tee /etc/apt/sources.list.d/caddy-stable.list"
    echo "   sudo apt update && sudo apt install caddy"
fi
echo "   Edit /etc/caddy/Caddyfile: chat.yourdomain.com { reverse_proxy localhost:5000 }"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛠️  Useful Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View logs:         sudo journalctl -u rpi-chat -f"
echo "Restart:           sudo systemctl restart rpi-chat"
echo "Stop:              sudo systemctl stop rpi-chat"
echo "Status:            sudo systemctl status rpi-chat"
echo "Disable autostart: sudo systemctl disable rpi-chat"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 First time setup: Visit http://$LOCAL_IP:5000/setup"
echo "   (Only accessible from this device for security)"
echo ""
