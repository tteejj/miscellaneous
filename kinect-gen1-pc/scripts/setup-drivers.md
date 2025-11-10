# Kinect Gen 1 Driver Installation Guide

Comprehensive guide for installing Kinect drivers on Windows and Linux.

## Identifying Your Kinect

**Kinect Gen 1 (Xbox 360 Kinect):**
- Model: 1414
- Released: 2010
- Connection: Proprietary Xbox 360 connector
- Requires: Special USB adapter with power supply

**Kinect Gen 2 (Xbox One Kinect):**
- Model: 1520
- Released: 2013
- Connection: Proprietary Xbox One connector
- This guide is for Gen 1 - Gen 2 requires different drivers

## Hardware Setup

### 1. Kinect to USB Adapter

**Required:** Xbox 360 Kinect to PC USB adapter

**Where to buy:**
- Amazon: ~$8-15 (search "Xbox 360 Kinect PC adapter")
- eBay: Used adapters available

**Includes:**
- USB 2.0 connector
- Power supply (12V)
- Adapter cable

**Setup:**
1. Connect Kinect to adapter
2. Connect adapter to PC USB port
3. Plug in power supply
4. Green LED on Kinect should illuminate

### 2. USB Requirements

- USB 2.0 port (USB 3.0 works but may have compatibility issues)
- Dedicated USB controller recommended (not USB hub)
- Some laptops may not provide enough power - use powered hub if needed

## Windows Installation

### Option 1: Official Kinect SDK (Recommended for Windows)

**Kinect for Windows SDK 1.8** (official Microsoft driver)

**Download:**
https://www.microsoft.com/en-us/download/details.aspx?id=40278

**Requirements:**
- Windows 7, 8, 10, or 11 (64-bit)
- Visual C++ 2010 Redistributable
- .NET Framework 4.0 or higher

**Installation:**
1. Download SDK installer (KinectSDK-v1.8-Setup.exe)
2. Run installer as administrator
3. Follow installation wizard
4. Restart computer
5. Connect Kinect
6. Check Device Manager → "Kinect for Windows"

**Includes:**
- Drivers
- SDK libraries
- Developer tools
- Sample applications
- Documentation

**Test Installation:**
- Run "Kinect Studio" from Start Menu
- Should show RGB and depth streams

### Option 2: libfreenect (Open Source)

**For advanced users or if SDK doesn't work**

**Requirements:**
- Python 3.7+
- Microsoft Visual C++ Build Tools
- CMake

**Installation:**

```powershell
# Install Python dependencies
pip install numpy
pip install opencv-python

# Install libfreenect via pip (easiest)
pip install freenect

# OR build from source:
git clone https://github.com/OpenKinect/libfreenect
cd libfreenect
mkdir build
cd build
cmake .. -G "Visual Studio 16 2019"
cmake --build . --config Release
cmake --install .
```

**Add to PATH:**
Add libfreenect binary directory to system PATH

**Test:**
```powershell
# Test with Python
python -c "import freenect; print('Success!')"
```

## Linux Installation

### Ubuntu / Debian

**Method 1: Package Manager (Easiest)**

```bash
# Update package list
sudo apt update

# Install libfreenect
sudo apt install -y freenect
sudo apt install -y libfreenect-dev

# Install Python bindings
sudo apt install -y python3-freenect

# Install additional tools
sudo apt install -y freenect-bin  # Command-line tools
```

**Method 2: Build from Source (Latest Version)**

```bash
# Install dependencies
sudo apt install -y git cmake build-essential
sudo apt install -y libusb-1.0-0-dev
sudo apt install -y python3-dev python3-pip
sudo apt install -y libglut-dev

# Clone repository
git clone https://github.com/OpenKinect/libfreenect.git
cd libfreenect

# Build
mkdir build
cd build
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_PYTHON3=ON \
  -DBUILD_OPENNI2_DRIVER=ON

make -j$(nproc)

# Install
sudo make install
sudo ldconfig
```

**Python Bindings:**

```bash
# Install Python wrapper
cd ../wrappers/python
sudo python3 setup.py install

# Verify
python3 -c "import freenect; print('Success!')"
```

### Add User to Video Group

Required for non-root access:

```bash
# Add your user to video group
sudo usermod -aG video $USER

# Create udev rule for Kinect
sudo nano /etc/udev/rules.d/51-kinect.rules
```

Add these lines:

```
# Xbox 360 Kinect
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666"
```

Reload udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**Logout and login** for group changes to take effect.

### Fedora / RHEL / CentOS

```bash
# Install dependencies
sudo dnf install -y git cmake gcc-c++
sudo dnf install -y libusb1-devel
sudo dnf install -y python3-devel
sudo dnf install -y freeglut-devel

# Follow build from source steps above
```

### Arch Linux

```bash
# Install from AUR
yay -S libfreenect

# Or from official repos
sudo pacman -S libfreenect

# Python bindings
pip install freenect
```

## macOS Installation

**Using Homebrew:**

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install libfreenect
brew install libfreenect

# Python bindings
pip3 install freenect
```

**Build from Source:**

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install dependencies
brew install cmake libusb

# Clone and build (same as Linux instructions)
git clone https://github.com/OpenKinect/libfreenect.git
cd libfreenect
mkdir build && cd build
cmake ..
make
sudo make install
```

## Verification

### Test Kinect Connection

**Check USB:**

**Windows:**
```powershell
# Device Manager → "Kinect for Windows" or "Xbox NUI Camera"
```

**Linux:**
```bash
# Should show Microsoft Xbox NUI devices
lsusb | grep -i xbox
```

Expected output:
```
Bus 001 Device 005: ID 045e:02ae Microsoft Corp. Xbox NUI Camera
Bus 001 Device 005: ID 045e:02ad Microsoft Corp. Xbox NUI Audio
Bus 001 Device 005: ID 045e:02b0 Microsoft Corp. Xbox NUI Motor
```

### Test Depth and RGB Streams

**Using freenect tools:**

```bash
# Display RGB and depth (Linux/Mac)
freenect-glview

# Capture single frame
freenect-camtest

# Tilt motor test
freenect-tiltdemo
```

**Using Python:**

```python
import freenect
import cv2
import numpy as np

# Test depth capture
depth, timestamp = freenect.sync_get_depth()
print(f"Depth shape: {depth.shape}")
print(f"Depth range: {depth.min()} - {depth.max()}")

# Test RGB capture
rgb, timestamp = freenect.sync_get_video()
print(f"RGB shape: {rgb.shape}")

# Display
cv2.imshow('Depth', depth.astype(np.uint8))
cv2.imshow('RGB', cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
cv2.waitKey(5000)
cv2.destroyAllWindows()

print("Success! Kinect is working.")
```

## Python Environment Setup

### Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv kinect-env

# Activate (Linux/Mac)
source kinect-env/bin/activate

# Activate (Windows)
kinect-env\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install numpy
pip install opencv-python
pip install freenect
pip install open3d  # For 3D scanning
pip install pynput  # For gesture control
pip install matplotlib  # For visualization
```

### Requirements File

Save as `requirements.txt`:

```
numpy>=1.19.0
opencv-python>=4.5.0
freenect>=0.2.0
open3d>=0.13.0
pynput>=1.7.0
matplotlib>=3.3.0
```

Install:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### Windows Issues

**"Device not recognized"**
- Install Kinect SDK 1.8
- Update USB drivers
- Try different USB port (USB 2.0)
- Check power supply connection

**"Access denied"**
- Run application as Administrator
- Check Windows Device Manager for driver issues

**Python can't find freenect**
- Ensure libfreenect is in PATH
- Reinstall: `pip install --force-reinstall freenect`

### Linux Issues

**"Permission denied"**
```bash
# Add user to video group
sudo usermod -aG video $USER
# Logout and login

# Check udev rules
ls /etc/udev/rules.d/51-kinect.rules

# Reconnect Kinect
```

**"USB device not found"**
```bash
# Check USB connection
lsusb | grep -i xbox

# Check dmesg for errors
dmesg | grep -i kinect

# Try different USB port
# Avoid USB hubs, use direct connection
```

**"Import freenect failed"**
```bash
# Reinstall Python bindings
cd libfreenect/wrappers/python
sudo python3 setup.py install

# Check library path
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

### General Issues

**Kinect LED not green**
- Check power supply
- Try different power outlet
- Adapter may be faulty

**No depth stream**
- Cover IR emitter (right side) - should see depth fail
- Uncover - depth should return
- If not, IR emitter may be broken

**Jittery/noisy depth**
- Normal behavior to some extent
- Improve lighting
- Move away from IR interference (sunlight, other Kinects)
- Use software filtering

**High CPU usage**
- Normal for real-time processing
- Lower resolution if needed
- Optimize code
- Use GPU acceleration where possible

## Additional Resources

**Official Documentation:**
- Kinect SDK: https://docs.microsoft.com/en-us/previous-versions/windows/kinect/
- libfreenect: https://github.com/OpenKinect/libfreenect

**Community:**
- OpenKinect forum: https://groups.google.com/g/openkinect
- Stack Overflow: Tag `kinect`

**Alternative Drivers:**
- OpenNI2 (for skeleton tracking)
- Processing library (for creative coding)

## Next Steps

After successful installation:

1. **Test with examples:**
   - `kinect-gen1-pc/3d-scanning/scripts/test_kinect.py`

2. **Try applications:**
   - Head tracking → `head-tracking/README.md`
   - 3D scanning → `3d-scanning/README.md`
   - Gesture control → `gesture-control/README.md`
   - Computer vision → `computer-vision/README.md`

3. **Calibrate:**
   - Run calibration scripts for accurate measurements
   - Save calibration profile

---

**Installation complete! Your Kinect Gen 1 is ready to use.**
