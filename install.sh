#!/bin/bash
set -e

echo "🚀 Installing RPi Chat Server (systemd version)..."
echo ""

# Detect distribution first
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

# Check if DietPi
is_dietpi() {
    [ -f /boot/dietpi/.installed ] || [ -d /boot/dietpi ] || grep -qi "dietpi" /etc/os-release 2>/dev/null
}

detect_distro

# Check if running as root (allow on DietPi, warn on others)
if [ "$EUID" -eq 0 ]; then
    if is_dietpi; then
        echo "📋 Running as root on DietPi (default setup)"
        SUDO=""
        INSTALL_USER="root"
        INSTALL_HOME="/root"
    else
        echo "❌ Please run as regular user (not root/sudo)"
        echo "   The script will ask for sudo when needed"
        echo ""
        echo "   On DietPi, create a user first:"
        echo "   useradd -m -s /bin/bash pi && passwd pi && usermod -aG sudo pi"
        exit 1
    fi
else
    SUDO="sudo"
    INSTALL_USER="$USER"
    INSTALL_HOME="$HOME"
fi

echo "📋 Detected distribution: $DISTRO"
echo "👤 Installing as: $INSTALL_USER"
echo ""

# Install dependencies based on distro
if [[ "$DISTRO" == "void" ]]; then
    echo "📦 Updating system packages (Void Linux)..."
    $SUDO xbps-install -Su

    echo "📦 Installing dependencies..."
    $SUDO xbps-install -y python3 python3-pip python3-Pillow sqlite git

elif [[ "$DISTRO" == "debian" ]] || [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "raspbian" ]] || [[ "$DISTRO" == "dietpi" ]]; then
    echo "📦 Updating system packages (Debian/Ubuntu/DietPi)..."
    $SUDO apt-get update

    echo "📦 Installing dependencies..."
    $SUDO apt-get install -y python3-pip python3-pil sqlite3 git

else
    echo "❌ Unsupported distribution: $DISTRO"
    echo "   Supported: Void Linux, Debian, Ubuntu, Raspbian, DietPi"
    exit 1
fi

# Install Python packages
echo "🐍 Installing Python dependencies..."
if [ "$EUID" -eq 0 ]; then
    pip3 install -r requirements.txt
else
    pip3 install --user -r requirements.txt
fi

# Initialize database
echo "💾 Initializing database..."
python3 database.py

# Install systemd service
echo "⚙️  Installing systemd service..."
WORKING_DIR=$(pwd)

# Create service file with correct paths
cat > /tmp/rpi-chat.service << EOF
[Unit]
Description=RPi Local Chat Server
After=network.target

[Service]
Type=simple
User=$INSTALL_USER
WorkingDirectory=$WORKING_DIR
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 $WORKING_DIR/server.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

$SUDO mv /tmp/rpi-chat.service /etc/systemd/system/
$SUDO systemctl daemon-reload
$SUDO systemctl enable rpi-chat
$SUDO systemctl start rpi-chat

# Check if service started successfully
sleep 2
if $SUDO systemctl is-active --quiet rpi-chat; then
    echo "✅ Chat service started successfully"
else
    echo "⚠️  Warning: Service may not have started. Check: sudo systemctl status rpi-chat"
fi

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
    echo "   $SUDO xbps-install -y tailscale"
    echo "   $SUDO sv up tailscaled  # Enable service"
    echo "   $SUDO tailscale up"
elif [[ "$DISTRO" == "dietpi" ]]; then
    echo "   $SUDO apt-get install -y tailscale"
    echo "   $SUDO systemctl enable --now tailscaled"
    echo "   $SUDO tailscale up"
else
    echo "   curl -fsSL https://tailscale.com/install.sh | sh"
    echo "   $SUDO tailscale up"
fi
echo "   $SUDO tailscale funnel --bg 5000 on"
echo "   Access: https://\$(tailscale status --json | jq -r '.Self.DNSName'):5000"
echo ""
echo "2️⃣  Caddy (Public Internet with Domain)"
if [[ "$DISTRO" == "void" ]]; then
    echo "   $SUDO xbps-install -y caddy"
elif [[ "$DISTRO" == "dietpi" ]]; then
    echo "   $SUDO apt-get install -y caddy"
    echo "   $SUDO systemctl enable --now caddy"
else
    echo "   $SUDO apt install -y debian-keyring debian-archive-keyring apt-transport-https"
    echo "   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | $SUDO gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg"
    echo "   echo 'deb [signed-by=/usr/share/keyrings/caddy-stable-archive-keyring.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main' | $SUDO tee /etc/apt/sources.list.d/caddy-stable.list"
    echo "   $SUDO apt update && $SUDO apt install caddy"
fi
echo "   Edit /etc/caddy/Caddyfile: chat.yourdomain.com { reverse_proxy localhost:5000 }"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛠️  Useful Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View logs:         $SUDO journalctl -u rpi-chat -f"
echo "Restart:           $SUDO systemctl restart rpi-chat"
echo "Stop:              $SUDO systemctl stop rpi-chat"
echo "Status:            $SUDO systemctl status rpi-chat"
echo "Disable autostart: $SUDO systemctl disable rpi-chat"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 First time setup: Visit http://$LOCAL_IP:5000/setup"
echo "   (Only accessible from this device for security)"
echo ""
echo "🔄 Auto-start enabled: Service will start automatically on boot"
echo ""
