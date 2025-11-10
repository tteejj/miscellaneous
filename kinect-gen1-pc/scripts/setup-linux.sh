#!/bin/bash
# Automated setup script for Kinect Gen 1 on Linux (Ubuntu/Debian)
# Run with: bash setup-linux.sh

set -e  # Exit on error

echo "=========================================="
echo "Kinect Gen 1 Setup for Linux"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root (sudo)"
    echo "The script will ask for sudo when needed"
    exit 1
fi

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "ERROR: Cannot detect Linux distribution"
    exit 1
fi

echo "Detected distribution: $DISTRO"
echo ""

# Install system dependencies
echo "Step 1: Installing system dependencies..."
echo "------------------------------------------"

if [ "$DISTRO" = "ubuntu" ] || [ "$DISTRO" = "debian" ]; then
    sudo apt update
    sudo apt install -y \
        git \
        cmake \
        build-essential \
        libusb-1.0-0-dev \
        python3 \
        python3-pip \
        python3-dev \
        python3-venv \
        freenect \
        libfreenect-dev \
        libfreenect-bin

elif [ "$DISTRO" = "fedora" ] || [ "$DISTRO" = "rhel" ] || [ "$DISTRO" = "centos" ]; then
    sudo dnf install -y \
        git \
        cmake \
        gcc-c++ \
        libusb1-devel \
        python3 \
        python3-pip \
        python3-devel

else
    echo "WARNING: Unsupported distribution. Attempting Ubuntu/Debian packages..."
    sudo apt update
    sudo apt install -y \
        git cmake build-essential libusb-1.0-0-dev \
        python3 python3-pip python3-dev python3-venv \
        freenect libfreenect-dev
fi

echo "✓ System dependencies installed"
echo ""

# Add user to video group
echo "Step 2: Adding user to video group..."
echo "--------------------------------------"
sudo usermod -aG video $USER
echo "✓ User '$USER' added to video group"
echo "  (You may need to logout and login for this to take effect)"
echo ""

# Create udev rules
echo "Step 3: Creating udev rules for Kinect..."
echo "------------------------------------------"
UDEV_RULE_FILE="/etc/udev/rules.d/51-kinect.rules"

if [ -f "$UDEV_RULE_FILE" ]; then
    echo "Udev rules already exist"
else
    sudo tee "$UDEV_RULE_FILE" > /dev/null << 'EOF'
# Xbox 360 Kinect
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666"
EOF

    sudo udevadm control --reload-rules
    sudo udevadm trigger
    echo "✓ Udev rules created and reloaded"
fi
echo ""

# Create Python virtual environment
echo "Step 4: Creating Python virtual environment..."
echo "----------------------------------------------"
VENV_DIR="$HOME/kinect-env"

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
    fi
else
    python3 -m venv "$VENV_DIR"
fi

echo "✓ Virtual environment created at $VENV_DIR"
echo ""

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install Python packages
echo "Step 5: Installing Python packages..."
echo "--------------------------------------"
pip install --upgrade pip

pip install numpy
pip install opencv-python
pip install freenect
pip install open3d
pip install pynput
pip install matplotlib

echo "✓ Python packages installed"
echo ""

# Test Kinect connection
echo "Step 6: Testing Kinect connection..."
echo "-------------------------------------"

KINECT_FOUND=$(lsusb | grep -i "xbox" || true)

if [ -n "$KINECT_FOUND" ]; then
    echo "✓ Kinect detected:"
    echo "$KINECT_FOUND"
    echo ""

    # Test Python import
    echo "Testing Python freenect import..."
    if python3 -c "import freenect; print('✓ freenect module loaded successfully')" 2>/dev/null; then
        echo ""
        echo "Testing Kinect data capture..."
        python3 << 'PYTHON_TEST'
import freenect
try:
    depth, _ = freenect.sync_get_depth()
    rgb, _ = freenect.sync_get_video()
    print(f"✓ Depth capture: {depth.shape}")
    print(f"✓ RGB capture: {rgb.shape}")
    print("")
    print("SUCCESS! Kinect is working perfectly!")
except Exception as e:
    print(f"✗ Error capturing from Kinect: {e}")
    print("")
    print("Possible issues:")
    print("1. Kinect not connected properly")
    print("2. Need to logout/login for video group permissions")
    print("3. USB power issue - try different port")
PYTHON_TEST
    else
        echo "✗ freenect module not found"
        echo "Try: pip install freenect"
    fi
else
    echo "⚠ WARNING: Kinect not detected via USB"
    echo ""
    echo "Please check:"
    echo "1. Kinect is connected to USB port"
    echo "2. Power adapter is plugged in"
    echo "3. Green LED on Kinect is lit"
    echo "4. Try: lsusb | grep -i xbox"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the Python environment:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To test Kinect:"
echo "  freenect-glview"
echo "  OR"
echo "  python3 kinect-gen1-pc/3d-scanning/scripts/test_kinect.py"
echo ""
echo "⚠  IMPORTANT: Logout and login for video group changes to take effect"
echo ""
echo "Next steps:"
echo "  - Read: kinect-gen1-pc/README.md"
echo "  - Head tracking: kinect-gen1-pc/head-tracking/README.md"
echo "  - 3D scanning: kinect-gen1-pc/3d-scanning/README.md"
echo "  - Gestures: kinect-gen1-pc/gesture-control/README.md"
echo "  - CV projects: kinect-gen1-pc/computer-vision/README.md"
echo ""
echo "=========================================="
