#!/usr/bin/env python3
"""
Gesture-based media player control using Kinect Gen 1
Control any media player (VLC, Spotify, etc.) from across the room

Gestures:
- Raise right hand: Play/Pause
- Swipe right: Next track/Skip forward
- Swipe left: Previous track/Skip backward
- Both hands up: Volume up
- Both hands down: Volume down
- Cross arms: Stop
"""

import freenect
import numpy as np
import time
import cv2
from collections import deque

try:
    from pynput.keyboard import Key, Controller as KeyboardController
except ImportError:
    print("ERROR: pynput not installed")
    print("Install with: pip install pynput")
    exit(1)

# Initialize keyboard controller
keyboard = KeyboardController()

class GestureDetector:
    """Simple gesture detection using depth and motion"""

    def __init__(self):
        self.prev_depth = None
        self.hand_history = deque(maxlen=10)  # Track last 10 positions
        self.gesture_cooldown = 0
        self.cooldown_time = 30  # Frames to wait between gestures

    def get_hand_position(self, depth):
        """
        Estimate hand position from depth map
        Returns (x, y, depth) of closest point (assumes hand is closest to camera)
        """
        # Get closest point (likely the hand reaching toward camera)
        valid_depth = depth[depth > 0]
        if len(valid_depth) == 0:
            return None

        min_depth = valid_depth.min()

        # Find region near minimum depth (tolerance for noise)
        hand_mask = (depth > 0) & (depth < min_depth + 100)

        if not hand_mask.any():
            return None

        # Get centroid of hand region
        y_coords, x_coords = np.where(hand_mask)
        if len(x_coords) == 0:
            return None

        x = np.mean(x_coords)
        y = np.mean(y_coords)

        return (x, y, min_depth)

    def detect_gesture(self, depth):
        """Detect gestures from depth changes"""

        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1
            return None

        hand = self.get_hand_position(depth)

        if hand is None:
            return None

        x, y, d = hand
        self.hand_history.append((x, y, d))

        # Need some history for gesture detection
        if len(self.hand_history) < 5:
            return None

        # Get recent history
        recent = list(self.hand_history)[-5:]

        # Calculate motion
        x_motion = recent[-1][0] - recent[0][0]
        y_motion = recent[-1][1] - recent[0][1]
        d_motion = recent[-1][2] - recent[0][2]

        # Gesture thresholds
        SWIPE_THRESHOLD = 100  # pixels
        RAISE_THRESHOLD = 80   # pixels
        PUSH_THRESHOLD = 200   # depth units

        gesture = None

        # Horizontal swipe
        if abs(x_motion) > SWIPE_THRESHOLD and abs(y_motion) < 50:
            if x_motion > 0:
                gesture = 'swipe_right'
            else:
                gesture = 'swipe_left'

        # Vertical motion
        elif abs(y_motion) > RAISE_THRESHOLD and abs(x_motion) < 50:
            if y_motion < 0:  # Moving up in image = raising hand
                gesture = 'raise_hand'
            else:
                gesture = 'lower_hand'

        # Push gesture (toward camera)
        elif d_motion < -PUSH_THRESHOLD:
            gesture = 'push'

        if gesture:
            self.gesture_cooldown = self.cooldown_time
            print(f"Gesture detected: {gesture}")

        return gesture

def execute_media_command(gesture):
    """Execute media control based on gesture"""

    if gesture == 'raise_hand':
        # Play/Pause
        print("▶️  Play/Pause")
        keyboard.press(Key.media_play_pause)
        keyboard.release(Key.media_play_pause)

    elif gesture == 'swipe_right':
        # Next track
        print("⏭️  Next track")
        keyboard.press(Key.media_next)
        keyboard.release(Key.media_next)

    elif gesture == 'swipe_left':
        # Previous track
        print("⏮️  Previous track")
        keyboard.press(Key.media_previous)
        keyboard.release(Key.media_previous)

    elif gesture == 'lower_hand':
        # Volume down
        print("🔉 Volume down")
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)

    elif gesture == 'push':
        # Stop
        print("⏹️  Stop")
        # Stop is not always available, use pause instead
        keyboard.press(Key.media_play_pause)
        keyboard.release(Key.media_play_pause)

def visualize_depth(depth):
    """Create visualization of depth with hand detection overlay"""
    # Normalize depth for display
    depth_display = depth.copy().astype(np.float32)
    depth_display[depth_display == 0] = depth_display.max()
    depth_display = (depth_display - depth_display.min()) / (depth_display.max() - depth_display.min())
    depth_display = (depth_display * 255).astype(np.uint8)

    # Apply colormap
    depth_colored = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)

    # Highlight closest region (hand)
    valid = depth[depth > 0]
    if len(valid) > 0:
        min_depth = valid.min()
        hand_mask = (depth > 0) & (depth < min_depth + 100)

        # Draw hand region in white
        depth_colored[hand_mask] = [255, 255, 255]

    return depth_colored

def main():
    print("Kinect Gesture Media Controller")
    print("=" * 50)
    print("\nGestures:")
    print("  Raise hand high      → Play/Pause")
    print("  Swipe right          → Next track")
    print("  Swipe left           → Previous track")
    print("  Lower hand           → Volume down")
    print("  Push toward camera   → Stop")
    print("\nPress 'q' to quit, 'v' to toggle visualization")
    print("=" * 50)

    # Check Kinect
    try:
        ctx = freenect.init()
        if freenect.num_devices(ctx) < 1:
            print("ERROR: No Kinect found!")
            return 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    detector = GestureDetector()
    show_viz = True

    try:
        while True:
            # Get depth frame
            depth, _ = freenect.sync_get_depth()

            # Detect gesture
            gesture = detector.detect_gesture(depth)

            # Execute command
            if gesture:
                execute_media_command(gesture)

            # Visualization
            if show_viz:
                viz = visualize_depth(depth)

                # Add instructions
                cv2.putText(viz, "Raise hand for Play/Pause", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(viz, "Swipe left/right for Prev/Next", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Show cooldown
                if detector.gesture_cooldown > 0:
                    cv2.putText(viz, f"Cooldown: {detector.gesture_cooldown}", (10, 450),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                cv2.imshow('Gesture Control - White = Hand', viz)

            # Handle keyboard
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('v'):
                show_viz = not show_viz
                if not show_viz:
                    cv2.destroyAllWindows()

    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        cv2.destroyAllWindows()
        freenect.sync_stop()

    print("\nGesture control stopped")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
