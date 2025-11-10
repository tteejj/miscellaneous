# Head Tracking with Opentrack - Optimized for Seated Use

Complete guide for setting up Kinect Gen 1 with Opentrack for head tracking in games, optimized for seated gaming positions.

## Table of Contents
1. [Installation](#installation)
2. [Hardware Setup (Critical for Seated Use)](#hardware-setup-critical-for-seated-use)
3. [Opentrack Configuration](#opentrack-configuration)
4. [Seated Position Optimization](#seated-position-optimization)
5. [Game Integration](#game-integration)
6. [Troubleshooting](#troubleshooting)

## Installation

### Step 1: Install Kinect Drivers

**Windows:**
1. Install Kinect SDK 1.8 from Microsoft (official support)
   - Download: https://www.microsoft.com/en-us/download/details.aspx?id=40278

   OR

2. Use libfreenect (open source alternative)
   - See [../scripts/windows-driver-setup.md](../scripts/windows-driver-setup.md)

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install libfreenect-dev freenect

# Build from source (latest version)
git clone https://github.com/OpenKinect/libfreenect.git
cd libfreenect
mkdir build && cd build
cmake -L ..
make
sudo make install
```

### Step 2: Install Opentrack

**Windows:**
1. Download latest release from: https://github.com/opentrack/opentrack/releases
2. Run installer
3. No additional configuration needed

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install opentrack

# Or build from source for latest features
git clone https://github.com/opentrack/opentrack.git
cd opentrack
mkdir build && cd build
cmake ..
make
sudo make install
```

### Step 3: Verify Kinect Connection

**Test the sensor:**
```bash
# Linux
freenect-glview

# Windows - use Kinect SDK Browser or freenect viewer
```

You should see RGB and depth streams if everything is connected properly.

## Hardware Setup (Critical for Seated Use)

The Kinect Gen 1 was designed primarily for standing full-body tracking, so seated optimization is crucial.

### Physical Positioning

```
     [Kinect Sensor]
       /         \
      /  5-15° tilt \
     /      down      \
    /                  \
[You seated at desk]
```

**Optimal Setup:**
1. **Distance**: 1.2m - 2.0m (4-6.5 feet) from your head
2. **Height**: Mount at forehead level or slightly above (10-30cm above eye level)
3. **Tilt**: Angle down 5-15° to capture seated position
4. **Lateral**: Center the sensor on your face when looking forward

### Mounting Options

**Option 1: Monitor Mount**
- Clip or mount on top of monitor
- Pros: Always aligned with screen
- Cons: May be too low for optimal tracking

**Option 2: Desk Stand**
- Use tripod or custom stand behind monitor
- Pros: Adjustable height and angle
- Cons: Takes desk space

**Option 3: Wall Mount**
- Mount on wall above/behind monitor
- Pros: Perfect angle control
- Cons: Permanent installation

**DIY Mount:**
- 3D print adapter or use adjustable camera mount
- See `hardware-mounts.md` for designs

### Lighting Optimization

The Kinect uses infrared for depth sensing, which helps in low light:

**Good:**
- Consistent ambient lighting
- Indirect lighting
- LED desk lamps (most don't interfere with IR)

**Bad:**
- Direct sunlight (saturates IR sensor)
- Bright backlighting (windows behind you)
- Other IR sources (some remotes, other Kinects)

**Testing:**
- Cover the RGB camera with tape and use only IR depth
- This forces pure depth tracking which works better in varied lighting

## Opentrack Configuration

### Input Configuration

1. **Launch Opentrack**
2. **Input dropdown** → Select **"Kinect Face API"** or **"Microsoft Kinect Face Tracker"**
   - If not available, install Kinect SDK 1.8

   Alternative for libfreenect users:
   - Use **"PointTracker"** with IR LED setup (see `ir-led-tracking.md`)

3. **Click Hammer icon** next to Input to configure

### Kinect-Specific Input Settings

**Face Tracking Settings:**
```
Enable face tracking: ✓
Enable shape model: ✓ (improves accuracy but needs more processing)
Sensor angle: 0° (adjust sensor physically instead)
Elevation angle: Auto (or set to match your physical tilt)
Seated mode: ✓ ENABLE THIS! (Critical for gaming)
Near mode: ✓ ENABLE (for distances < 3m)
```

### Output Configuration

**For Games Supporting TrackIR:**
1. **Output dropdown** → Select **"freetrack 2.0 Enhanced"**
2. This emulates TrackIR protocol

**For Games with Native Support:**
1. **Output dropdown** → Select **"freetrack 2.0"** or **"UDP over network"**
2. Configure game to listen on appropriate port

### Filter Configuration

Critical for smooth movement and preventing jitter:

1. **Filter dropdown** → Select **"Accela"** (recommended for gaming)

**Settings:**
```
Smoothing: 0.5 - 1.0 (higher = smoother but more lag)
Deadzone: 0.5° - 2.0° (prevents micro-movements)
Responsiveness: 0.3 - 0.5 (balance between smooth and responsive)
```

Alternative filters:
- **"Kalman"**: Very smooth, good for flight sims
- **"EWMA"**: Fast response, slight jitter
- **"None"**: Raw data, very responsive but jittery

## Seated Position Optimization

### Mapping Configuration

The mapping curves control how your head movement translates to in-game camera movement. Seated gaming needs different curves than standing VR.

**Recommended Mapping Curves:**

**Yaw (Left/Right):**
```
Input → Output
0°   → 0°
10°  → 25°
20°  → 60°
30°  → 90°
```
- Exponential curve for natural feel
- Max input: 30-40° (comfortable head turn)
- Max output: 90-120° (full game camera)

**Pitch (Up/Down):**
```
Input → Output
0°   → 0°
10°  → 20°
20°  → 45°
```
- Less aggressive than yaw
- Max input: 20° (comfortable looking range)
- Max output: 45-60°

**Roll (Head Tilt):**
```
Input → Output
0°   → 0°
5°   → 5°
10°  → 10°
```
- Usually 1:1 or disabled
- Most people don't tilt head much while gaming

**Translation (X/Y/Z movement):**
- **X (Left/Right lean)**: 5cm input → 15cm output
- **Y (Up/Down)**: 5cm input → 10cm output
- **Z (Forward/Back)**: 5cm input → 15cm output

### In Opentrack UI:

1. Click **"Mapping"** tab
2. For each axis, click to add points on the curve
3. Drag points to create smooth exponential curves
4. Check **"Asymmetric mapping"** if you want different curves for left/right or up/down

### Center Key Binding

**Essential for seated use:**
1. **Options** → **Keyboard Shortcuts**
2. Bind **"Center"** to easily accessible key (e.g., `Home`, `Numpad 5`, or mouse button)
3. Press this whenever you need to reset neutral position

## Game Integration

### Elite Dangerous

1. **In Opentrack:**
   - Output: "freetrack 2.0 Enhanced"
   - Start tracking

2. **In Elite Dangerous:**
   - Options → Controls → Mouse/Headlook
   - Enable "Mouse Headlook"
   - Or bind TrackIR controls under "Headlook" section

3. **Test:**
   - Move head slowly
   - Should see smooth camera movement
   - Adjust mapping if too sensitive/slow

### DCS World / Flight Simulators

1. **In Opentrack:**
   - Output: "freetrack 2.0 Enhanced"
   - Use Kalman filter for smoothest experience
   - Enable all 6DOF (translation + rotation)

2. **In DCS:**
   - Options → Controls → View
   - TrackIR should be auto-detected
   - Adjust "View" axis curves in-game if needed

### Racing Simulators (Assetto Corsa, iRacing, etc.)

1. **In Opentrack:**
   - Output: "freetrack 2.0"
   - Reduce yaw sensitivity (don't need full 180°)
   - Increase translation X (leaning into corners)

2. **In Game:**
   - Enable TrackIR/head tracking in options
   - May need to disable mouse look

### FPS Games (Arma 3, etc.)

1. **In Opentrack:**
   - Output: "freetrack 2.0 Enhanced"
   - More aggressive yaw curve for quick peeks
   - Enable translation X for leaning

2. **In Game:**
   - Bind "Free Look" or TrackIR controls
   - Some games need "Alt+Free Look" toggle

## Troubleshooting

### Kinect Not Detected

**Check:**
1. USB adapter has power connected
2. Green LED on Kinect is lit
3. Device Manager shows "Kinect" devices (Windows)
4. `lsusb | grep Xbox` shows device (Linux)

**Fix:**
```bash
# Linux: Add user to video group
sudo usermod -aG video $USER
# Logout and login

# Linux: Reset USB device
sudo rmmod usb_storage && sudo modprobe usb_storage
```

### Tracking Loss When Seated

**Common Issue:** Kinect loses face when you lean or look down

**Solutions:**
1. **Enable "Near Mode"** in Kinect settings
2. **Raise sensor height** so it looks down at you
3. **Increase lighting** on your face
4. **Reduce max pitch** in mapping (don't look down as much in-game)
5. **Disable "Shape Model"** for faster but less accurate tracking

### Jittery/Shaky Tracking

**Causes:**
- Low light
- IR interference
- Processing lag
- Poor USB connection

**Solutions:**
1. Increase filter smoothing (0.7-1.0)
2. Add deadzone (1-2°)
3. Use Kalman or Accela filter
4. Close background applications
5. Use USB 2.0 port (3.0 can cause issues with Gen 1)

### Tracking Offset/Drift

**Solution:**
1. Press center key to reset
2. Ensure Kinect is stable (not vibrating)
3. Calibrate in Opentrack settings
4. Check sensor isn't moving on monitor

### Games Don't Respond

**Check:**
1. Opentrack "Start" button is active
2. Output protocol matches game expectation
3. Game has head tracking enabled in settings
4. No other TrackIR software running (e.g., official TrackIR)
5. Run game and Opentrack as administrator (Windows)

## Advanced: IR LED Tracking

For even better seated performance, you can add IR LEDs to a headset:

**Benefits:**
- More reliable than face tracking
- Works in complete darkness
- Lower CPU usage
- Better precision

**See:** `ir-led-tracking.md` for complete guide

## Performance Tips

1. **Close RGB stream** if only using depth (saves CPU)
2. **Lower Kinect resolution** to 320x240 for faster processing
3. **Disable shape model** if CPU is struggling
4. **Use USB 2.0 port** (better compatibility than 3.0 for Gen 1)
5. **Overclock refresh rate** in Kinect settings (15fps → 30fps)

## Recommended Settings Summary

**For Seated Gaming:**
```
Input: Kinect Face API
  ├─ Seated mode: ON
  ├─ Near mode: ON
  └─ Shape model: OFF (for performance) or ON (for accuracy)

Filter: Accela
  ├─ Smoothing: 0.7
  ├─ Deadzone: 1.0°
  └─ Responsiveness: 0.4

Output: freetrack 2.0 Enhanced

Mapping:
  ├─ Yaw: Exponential, max 30° → 90°
  ├─ Pitch: Moderate, max 20° → 45°
  ├─ Roll: Minimal or disabled
  └─ Translation: 5cm → 15cm
```

## Testing Procedure

1. Start Opentrack
2. Click "Start" button
3. Check **"Octopus"** visualization
   - Should show head position updating
   - Should be smooth, not jumpy
4. Move head slowly left/right
   - Octopus should follow smoothly
5. Test in game
6. Adjust mapping curves as needed
7. Save profile: File → Save Profile As → "seated-gaming"

## Additional Resources

- Sample profiles: See `profiles/` directory
- Video guides: See `video-guides.md`
- Community profiles: https://github.com/opentrack/opentrack/wiki/Profiles

---

**Next Steps:**
- Try it out and adjust sensitivity to your preference
- Save multiple profiles for different game types
- Explore IR LED tracking for even better performance
