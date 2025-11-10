# Gesture Control with Kinect Gen 1

Use Kinect's skeleton tracking and depth sensing for hands-free computer control and custom gesture interfaces.

## Table of Contents
1. [Overview](#overview)
2. [Skeleton Tracking](#skeleton-tracking)
3. [Hand Gesture Recognition](#hand-gesture-recognition)
4. [Mouse/Keyboard Control](#mousekeyboard-control)
5. [Custom Applications](#custom-applications)
6. [Example Projects](#example-projects)

## Overview

The Kinect Gen 1 can track:
- **Full body skeleton** (20 joints)
- **Hand positions** (open/closed state)
- **Gestures** (wave, swipe, push, etc.)
- **Distance** (depth for interaction zones)

**Applications:**
- Hands-free PC control
- Presentations
- Media player control
- Gaming input
- Custom interfaces

## Skeleton Tracking

### Available Joints (20 total)

```
         HEAD
          |
      SHOULDER_CENTER
       /      \
   SHOULDER  SHOULDER
    L           R
    |           |
   ELBOW       ELBOW
    L           R
    |           |
   WRIST       WRIST
    L           R
    |           |
   HAND        HAND
    L           R

    SPINE
      |
    HIP_CENTER
    /         \
  HIP_L      HIP_R
   |           |
  KNEE_L     KNEE_R
   |           |
  ANKLE_L    ANKLE_R
   |           |
  FOOT_L     FOOT_R
```

### Basic Skeleton Tracking

**Windows (Kinect SDK):**
See `examples/skeleton_tracking_windows.py`

**Linux (OpenNI + NITE):**
See `examples/skeleton_tracking_linux.py`

### Tracking Quality

**Best results:**
- Standing 1.5m - 3.5m from Kinect
- Full body visible
- No obstructions
- Even lighting

**Seated mode:**
- Enable "seated mode" in SDK
- Tracks upper body only (head, shoulders, arms, hands)
- Distance: 0.8m - 2.5m
- **Perfect for desk-based gesture control!**

## Hand Gesture Recognition

### Built-in Gestures (Kinect SDK)

**Wave:**
- Raise hand above shoulder
- Move left-right or up-down rapidly
- **Use case:** Start/stop tracking, attention getter

**Swipe:**
- Hand moves across body horizontally
- Left or right direction
- **Use case:** Navigate slides, switch windows

**Push:**
- Hand extends forward quickly
- **Use case:** Click, select, confirm

**Grip:**
- Hand closes (fist)
- **Use case:** Grab, drag, hold

### Custom Gesture Recognition

Build your own gesture vocabulary using hand position tracking.

**Example gestures:**
```python
# Raise hand = Volume up
if hand_y > shoulder_y + 0.2:
    volume_up()

# Lower hand = Volume down
if hand_y < hip_y:
    volume_down()

# Hands apart = Play/Pause
if abs(hand_left_x - hand_right_x) > 0.5:
    media_play_pause()

# Cross arms = Stop
if hand_left_x > shoulder_right_x and hand_right_x < shoulder_left_x:
    media_stop()
```

See `examples/custom_gestures.py` for complete implementation.

### Hand State Detection

**Open vs Closed:**
```python
# Kinect SDK provides hand state
if hand.state == HandState.OPEN:
    # Hand is open (pointing, waving)
elif hand.state == HandState.CLOSED:
    # Hand is closed (fist, gripping)
elif hand.state == HandState.LASSO:
    # Pointing (index finger extended)
```

**Use cases:**
- Closed fist = Click and drag
- Open hand = Hover
- Lasso = Point and select

## Mouse/Keyboard Control

### Virtual Mouse

Control mouse cursor with hand position:

```bash
python examples/gesture_mouse.py
```

**Features:**
- Right hand controls cursor
- Left hand closed = Left click
- Right hand closed = Right click
- Both hands closed = Drag mode
- Push gesture = Click

**Smoothing:**
- Raw hand tracking is jittery
- Apply smoothing filter (moving average or Kalman)
- Adjustable sensitivity zones

### Virtual Keyboard

```bash
python examples/gesture_keyboard.py
```

**Gestures:**
- Swipe left = Previous window
- Swipe right = Next window
- Swipe up = Volume up
- Swipe down = Volume down
- Wave = Minimize all windows
- Push = Enter/Select

### Media Control

Perfect for watching videos from couch:

```bash
python examples/gesture_media_player.py
```

**Controls:**
- Raise right hand = Play/Pause
- Swipe right = Skip forward
- Swipe left = Skip backward
- Raise both hands = Volume up
- Lower both hands = Volume down
- Cross arms = Stop

Works with VLC, Windows Media Player, Spotify, etc. using system media keys.

## Custom Applications

### Presentation Control

**Use case:** Control PowerPoint/LibreOffice without remote clicker

```bash
python examples/gesture_presentation.py
```

**Gestures:**
- Swipe right = Next slide
- Swipe left = Previous slide
- Push = Laser pointer mode
- Wave = Start/end presentation
- Raise hand = Show slide notes

### Gaming Input

**Simple game controls:**

```bash
python examples/gesture_game_controller.py
```

**Map gestures to keyboard/gamepad:**
- Lean left/right = Arrow keys or joystick
- Jump = Raise both hands
- Crouch = Lower both hands
- Punch = Push gesture
- Action = Hand grip

**Supported games:**
- Any game accepting keyboard input
- Configure mapping per game

### Sign Language Recognition

**Basic implementation:**

```bash
python examples/sign_language_basic.py
```

**Features:**
- Recognize common signs (hello, yes, no, etc.)
- Train custom gesture sets
- Real-time translation
- Educational tool

## Example Projects

### 1. Smart Home Control

Control lights, music, thermostats with gestures:

```python
# Gesture → Action mapping
gestures = {
    'wave': toggle_lights,
    'swipe_up': increase_brightness,
    'swipe_down': decrease_brightness,
    'push': play_music,
    'cross_arms': all_off,
}
```

Integration with:
- Home Assistant
- Phillips Hue
- MQTT
- HTTP APIs

See `examples/smart_home_control.py`

### 2. Virtual Drum Kit

Play drums in the air:

```bash
python examples/virtual_drums.py
```

- Track hand positions
- Detect hitting motions (velocity + direction)
- Play drum samples
- Different heights = Different drums

### 3. Air Drawing

Draw in 3D space:

```bash
python examples/air_drawing.py
```

- Track hand position in 3D
- Record path
- Export as SVG or 3D model
- Virtual whiteboard

### 4. Fitness Tracker

Count exercises and check form:

```bash
python examples/fitness_tracker.py
```

- Count squats, jumping jacks, arm raises
- Detect incorrect form
- Track workout stats
- Voice feedback

## Implementation Details

### Python Libraries

**pykinect2** (Windows only):
```bash
pip install pykinect2
```

**PyOpenNI** (Linux/Windows):
```bash
# Requires OpenNI and NITE installed
pip install primesense
```

**Control libraries:**
```bash
pip install pyautogui  # Mouse/keyboard control
pip install pynput     # Input monitoring
pip install keyboard   # Keyboard hooks
```

### Basic Template

```python
import freenect
import numpy as np
from pynput.mouse import Controller, Button
from pynput.keyboard import Key, Controller as KeyboardController

mouse = Controller()
keyboard = KeyboardController()

def get_hand_position():
    """Get normalized hand position from skeleton tracking"""
    # Implementation depends on library
    # Returns (x, y, z) in range 0-1
    pass

def detect_gesture(hand_history):
    """Detect gesture from hand position history"""
    # Analyze movement pattern
    # Return gesture name or None
    pass

def main():
    while True:
        # Get skeleton data
        hand_pos = get_hand_position()

        # Detect gestures
        gesture = detect_gesture(hand_history)

        # Execute action
        if gesture == 'swipe_right':
            keyboard.press(Key.right)
            keyboard.release(Key.right)
        elif gesture == 'push':
            mouse.click(Button.left)

        # Update display
        render_skeleton()
```

See `examples/gesture_template.py` for complete template.

### Gesture Recognition Algorithm

**1. Collect samples:**
Record hand positions during gesture performance

**2. Extract features:**
- Start/end positions
- Path length
- Velocity
- Direction changes
- Duration

**3. Train classifier:**
- K-Nearest Neighbors (simple, fast)
- Hidden Markov Models (temporal patterns)
- Neural networks (high accuracy)

**4. Real-time recognition:**
- Sliding window
- Gesture spotting
- Confidence threshold

See `examples/gesture_classifier.py`

## Performance Optimization

### Reduce Latency

1. **Lower skeleton resolution:** Track upper body only
2. **Increase frame rate:** 30 FPS is sufficient
3. **Disable unused features:** RGB camera if not needed
4. **Optimize processing:** Use numpy vectorization
5. **Multi-threading:** Separate capture and processing

### Improve Accuracy

1. **Calibration:** Tune for your room setup
2. **Smoothing:** Kalman filter or moving average
3. **Dead zones:** Ignore micro-movements
4. **Hysteresis:** Require sustained gesture
5. **User training:** Let users practice gestures

## Troubleshooting

### Skeleton Not Tracking

**Check:**
- Full body visible (or upper body in seated mode)
- Distance 1.5-3.5m (standing) or 0.8-2.5m (seated)
- Even lighting (not backlit)
- Clear background
- Enable "seated mode" for desk use

### Jittery Hand Position

**Solutions:**
- Implement smoothing filter
- Increase averaging window
- Use Kalman filter
- Reduce sensitivity
- Add dead zone

### Gestures Not Recognized

**Debug:**
- Visualize hand tracking (see `debug_tracking.py`)
- Check gesture templates
- Adjust sensitivity thresholds
- Verify gesture timing
- Retrain classifier

### High CPU Usage

**Optimize:**
- Lower frame rate
- Disable RGB processing
- Use lighter gesture detection
- Profile code for bottlenecks
- Consider using C++ for critical sections

## Safety Considerations

**Ergonomics:**
- Short sessions (fatigue from "gorilla arm")
- Take breaks
- Don't overextend arms
- Alternate hands

**Accessibility:**
- Provide keyboard fallbacks
- Adjustable sensitivity
- Simple gestures
- Visual feedback

## Example Scripts

All in `examples/` directory:

**Basic:**
- `skeleton_display.py` - Visualize skeleton tracking
- `hand_tracking.py` - Track hands only
- `depth_interaction.py` - Use depth for zones

**Control:**
- `gesture_mouse.py` - Mouse control
- `gesture_keyboard.py` - Keyboard shortcuts
- `gesture_media_player.py` - Media control

**Applications:**
- `gesture_presentation.py` - Presentation remote
- `smart_home_control.py` - Home automation
- `virtual_drums.py` - Musical instrument
- `air_drawing.py` - 3D drawing
- `fitness_tracker.py` - Exercise counter

**Advanced:**
- `gesture_classifier.py` - Custom gesture recognition
- `gesture_template.py` - Starter template
- `debug_tracking.py` - Debugging tools

## Next Steps

1. Test skeleton tracking with `skeleton_display.py`
2. Try media control for immediate usefulness
3. Build custom gesture set for your workflow
4. Integrate with your smart home or applications
5. Share your gesture mappings!

---

**Resources:**
- Kinect SDK documentation
- OpenNI/NITE documentation
- Gesture recognition papers
- Community gesture databases
