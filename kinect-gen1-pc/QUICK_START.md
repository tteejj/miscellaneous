# Quick Start Guide - Kinect Gen 1

Get up and running with your Kinect in 15 minutes!

## What You Need

- ✅ Kinect for Xbox 360 (Gen 1)
- ✅ Kinect to PC USB adapter (~$8 on Amazon)
- ✅ Computer with USB 2.0 port
- ✅ Windows 10/11 OR Linux (Ubuntu/Debian recommended)

## 5-Minute Hardware Setup

1. **Connect the adapter:**
   - Plug Kinect into adapter cable
   - Connect USB to computer
   - Plug in power supply

2. **Check the LED:**
   - Green LED on Kinect should light up
   - If not: check power connection

3. **Verify connection:**

   **Windows:** Check Device Manager for "Kinect" or "Xbox NUI"

   **Linux:**
   ```bash
   lsusb | grep -i xbox
   # Should show 3 Xbox NUI devices (camera, audio, motor)
   ```

## Quick Software Install

### Windows (Option 1 - Gaming Focus)

**For head tracking in games (Elite Dangerous, DCS, etc.):**

1. Download **Kinect SDK 1.8**:
   https://www.microsoft.com/en-us/download/details.aspx?id=40278

2. Install SDK (follow wizard)

3. Download **Opentrack**:
   https://github.com/opentrack/opentrack/releases

4. Install Opentrack

5. **You're ready!** → See [head-tracking/README.md](head-tracking/README.md)

### Linux (Quick Install)

```bash
# Run the automated setup script
cd kinect-gen1-pc/scripts
bash setup-linux.sh

# This will:
# - Install libfreenect drivers
# - Create Python environment
# - Install all dependencies
# - Test Kinect connection
```

**Manual install:**
```bash
# Install drivers
sudo apt install freenect libfreenect-dev

# Install Python packages
pip install numpy opencv-python freenect open3d pynput

# Add user to video group
sudo usermod -aG video $USER

# Logout and login
```

### Windows (Option 2 - Development Focus)

```powershell
# Install Python 3.8+ from python.org

# Install dependencies
pip install numpy opencv-python freenect open3d pynput

# Install Kinect SDK 1.8 (link above)
```

## First Test - Does It Work?

### Test 1: Command Line

**Linux:**
```bash
freenect-glview
# Should show RGB and depth windows
```

**Windows with SDK:**
- Run "Kinect Studio" from Start Menu
- Should see video streams

### Test 2: Python Test

```bash
cd kinect-gen1-pc/3d-scanning/scripts
python test_kinect.py
```

Should display RGB and depth side-by-side. Press 'q' to quit.

**Success?** ✅ Your Kinect is working!

**Not working?** → See [scripts/setup-drivers.md](scripts/setup-drivers.md) troubleshooting section

## What Can I Do Now?

### 1. Head Tracking (Easiest Start)

**Perfect for:** Gaming while seated

**Time:** 10 minutes to setup

**What:** Control in-game camera with head movement

**Start here:** [head-tracking/README.md](head-tracking/README.md)

**Quick setup:**
1. Launch Opentrack
2. Input: "Kinect Face API"
3. Output: "freetrack 2.0 Enhanced"
4. Enable "Seated Mode"
5. Click "Start"
6. Launch game (Elite Dangerous, DCS, etc.)

### 2. Media Control Gestures (Most Fun)

**Perfect for:** Controlling media from couch

**Time:** 2 minutes

**What:** Control music/videos with hand gestures

**Try it:**
```bash
cd kinect-gen1-pc/gesture-control/examples
python gesture_media_player.py
```

**Gestures:**
- Raise hand → Play/Pause
- Swipe right → Next track
- Swipe left → Previous track

### 3. 3D Scanning (Show Off to Friends)

**Perfect for:** Creating 3D models for printing

**Time:** 5 minutes

**What:** Scan objects into 3D point clouds

**Try it:**
```bash
cd kinect-gen1-pc/3d-scanning/scripts
python capture_single_pointcloud.py --preview --output my_scan.ply
```

Press SPACE to capture, then view with:
```bash
python view_pointcloud.py my_scan.ply
```

### 4. Virtual Green Screen (Coolest Demo)

**Perfect for:** Video calls, streaming

**Time:** 1 minute

**What:** Remove your background without a green screen!

**Try it:**
```bash
cd kinect-gen1-pc/computer-vision/examples
python virtual_green_screen.py
```

Adjust threshold with +/- keys until you're isolated from background.

## Common Issues & Quick Fixes

### "No Kinect found"
1. Check USB connection and power
2. Try different USB port (prefer USB 2.0)
3. Windows: Install Kinect SDK 1.8
4. Linux: Add to video group and logout/login

### "Permission denied" (Linux)
```bash
sudo usermod -aG video $USER
# Logout and login
```

### "Import freenect failed"
```bash
pip install --upgrade freenect
# OR
pip install --force-reinstall freenect
```

### Jittery tracking
- Improve room lighting
- Move away from windows (IR interference)
- Enable smoothing in software
- Use seated mode for head tracking

### Poor depth quality
- Clean Kinect lenses
- Optimal distance: 1-2m for seated, 1.5-3.5m for standing
- Avoid reflective surfaces (mirrors, glass, black objects)
- Even lighting (no direct sunlight)

## Recommended First Project

**For gamers:**
→ Head tracking for Elite Dangerous
→ Read: [head-tracking/README.md](head-tracking/README.md)

**For makers:**
→ 3D scanning for 3D printing
→ Read: [3d-scanning/README.md](3d-scanning/README.md)

**For automation enthusiasts:**
→ Gesture-controlled smart home
→ Read: [gesture-control/README.md](gesture-control/README.md)

**For developers:**
→ Computer vision experiments
→ Read: [computer-vision/README.md](computer-vision/README.md)

## Learning Path

**Week 1:**
- Get hardware working
- Try all example scripts
- Pick your favorite application

**Week 2:**
- Deep dive into chosen application
- Customize settings for your setup
- Create your own variations

**Week 3:**
- Combine multiple features
- Build custom project
- Share your creation!

## Getting Help

**Check documentation:**
- Main README: [README.md](README.md)
- Driver setup: [scripts/setup-drivers.md](scripts/setup-drivers.md)
- Each subfolder has detailed README

**Common resources:**
- libfreenect: https://github.com/OpenKinect/libfreenect
- Opentrack: https://github.com/opentrack/opentrack
- OpenCV tutorials: https://docs.opencv.org/

**Troubleshooting checklist:**
1. ✅ Green LED on Kinect lit?
2. ✅ USB connection secure?
3. ✅ Drivers installed?
4. ✅ Python packages installed?
5. ✅ User in video group? (Linux)
6. ✅ Logged out and back in? (Linux)

## What's Next?

Once you're comfortable with the basics:

1. **Optimize for your setup**
   - Calibrate Kinect for accurate measurements
   - Tune head tracking sensitivity
   - Create custom gesture sets

2. **Combine features**
   - Head tracking + gesture controls
   - 3D scanning + virtual try-on
   - Motion detection + home automation

3. **Build something unique**
   - Virtual drum kit
   - Fitness form checker
   - Interactive art installation
   - Your own creative idea!

## Pro Tips

1. **Lighting matters:** Even, indirect lighting works best
2. **Distance matters:** 1-2m for seated, 1.5-3.5m for standing
3. **USB matters:** Use USB 2.0 port, avoid hubs
4. **Smoothing matters:** All applications benefit from filtering
5. **Calibration matters:** Take time to calibrate for best results

## Ready to Go!

You now have:
- ✅ Kinect connected and working
- ✅ Drivers installed
- ✅ Example scripts ready to run
- ✅ Multiple project paths to explore

**Pick an application and dive in!**

The detailed README in each directory has everything you need:
- `head-tracking/` - For gaming
- `3d-scanning/` - For 3D capture
- `gesture-control/` - For hands-free control
- `computer-vision/` - For CV experiments

**Have fun exploring what your Kinect can do! 🎮📹🎨**
