#!/bin/bash

# RPi Local Chat Server - Setup Script
# Works on both Debian/Ubuntu and Void Linux

set -e

echo "========================================"
echo "RPi Local Chat Server - Setup"
echo "========================================"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS. Exiting."
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Initialize database
echo ""
echo "Initializing database..."
python3 database.py
echo "✓ Database initialized"

# Create systemd or runit service based on OS
echo ""
echo "Setting up system service..."

if command -v systemctl &> /dev/null; then
    # Systemd (Debian, Ubuntu, etc.)
    echo "Configuring systemd service..."

    sudo tee /etc/systemd/system/rpi-chat.service > /dev/null <<EOF
[Unit]
Description=RPi Local Chat Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$SCRIPT_DIR/venv/bin"
ExecStart=$SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    echo "✓ Systemd service created"
    echo ""
    echo "To enable auto-start on boot:"
    echo "  sudo systemctl enable rpi-chat"
    echo "To start now:"
    echo "  sudo systemctl start rpi-chat"

elif [ "$OS" = "void" ]; then
    # Runit (Void Linux)
    echo "Configuring runit service..."

    sudo mkdir -p /etc/sv/rpi-chat
    sudo tee /etc/sv/rpi-chat/run > /dev/null <<EOF
#!/bin/sh
exec 2>&1
cd $SCRIPT_DIR
exec chpst -u $USER $SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/server.py
EOF

    sudo chmod +x /etc/sv/rpi-chat/run
    echo "✓ Runit service created"
    echo ""
    echo "To enable and start the service:"
    echo "  sudo ln -s /etc/sv/rpi-chat /var/service/"
    echo "To stop the service:"
    echo "  sudo rm /var/service/rpi-chat"
fi

# Create start/stop helper scripts
echo ""
echo "Creating helper scripts..."

cat > start-chat.sh <<'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run setup.sh first."
    exit 1
fi

source venv/bin/activate
python3 server.py
EOF

cat > stop-chat.sh <<'EOF'
#!/bin/bash
pkill -f "python3.*server.py" || echo "No running server found"
EOF

chmod +x start-chat.sh stop-chat.sh

echo "✓ Helper scripts created"
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Quick Start:"
echo "  ./start-chat.sh      - Start the server manually"
echo "  ./stop-chat.sh       - Stop the server"
echo ""
echo "Server will be available at:"
echo "  http://localhost:5000"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "First time? Visit /setup to create your admin account"
echo ""
