#!/bin/bash
set -e

echo "🐋 Installing RPi Chat Server (Podman Container Version)"
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

detect_distro

# Check if running as root (allow on DietPi, warn on others)
if [ "$EUID" -eq 0 ]; then
    if [[ "$DISTRO" == "dietpi" ]]; then
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

# Install Podman based on distro
if [[ "$DISTRO" == "void" ]]; then
    echo "📦 Installing Podman (Void Linux)..."
    $SUDO xbps-install -Su
    $SUDO xbps-install -y podman

elif [[ "$DISTRO" == "debian" ]] || [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "raspbian" ]] || [[ "$DISTRO" == "dietpi" ]]; then
    echo "📦 Installing Podman (Debian/Ubuntu/DietPi)..."
    $SUDO apt-get update
    $SUDO apt-get install -y podman

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
mkdir -p "$INSTALL_HOME/rpi-chat-data/uploads"
touch "$INSTALL_HOME/rpi-chat-data/chat.db"

# Build and run container
echo "🔨 Building container..."
./build-and-run.sh

# Check if container is running
sleep 2
if podman ps | grep -q rpi-chat; then
    echo "✅ Container started successfully"
else
    echo "⚠️  Warning: Container may not have started. Check: podman ps -a"
fi

# Install systemd service for auto-start
echo ""
echo "⚙️  Installing systemd service for auto-start..."

# Create service file with correct user
cat > /tmp/rpi-chat-podman.service << EOF
[Unit]
Description=RPi Chat Server (Podman)
After=network.target

[Service]
Type=simple
User=$INSTALL_USER
Restart=always
RestartSec=10
ExecStartPre=-/usr/bin/podman stop rpi-chat
ExecStartPre=-/usr/bin/podman rm rpi-chat
ExecStart=/usr/bin/podman run --rm --name rpi-chat -p 5000:5000 -v $INSTALL_HOME/rpi-chat-data:/app/data:Z rpi-chat:latest
ExecStop=/usr/bin/podman stop -t 10 rpi-chat

[Install]
WantedBy=multi-user.target
EOF

$SUDO mv /tmp/rpi-chat-podman.service /etc/systemd/system/
$SUDO systemctl daemon-reload
$SUDO systemctl enable rpi-chat-podman

echo "✅ Systemd service installed and enabled"
echo "   Service will start automatically on boot"
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
echo "     (Includes auto-start configuration)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛠️  Useful Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Service status:   $SUDO systemctl status rpi-chat-podman"
echo "View logs:        $SUDO journalctl -u rpi-chat-podman -f"
echo "Restart:          $SUDO systemctl restart rpi-chat-podman"
echo "Stop:             $SUDO systemctl stop rpi-chat-podman"
echo "Container logs:   podman logs -f rpi-chat"
echo "Rebuild:          ./build-and-run.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 First time setup: Visit http://$LOCAL_IP:5000/setup"
echo ""
echo "🔄 Auto-start enabled: Container will start automatically on boot"
echo ""
