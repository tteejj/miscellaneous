#!/usr/bin/env python3
"""
Test Kinect Gen 1 connection and display RGB + Depth streams
Verifies that libfreenect is working correctly
"""

import freenect
import cv2
import numpy as np
import sys

def get_depth():
    """Get depth frame from Kinect"""
    array, _ = freenect.sync_get_depth()
    array = array.astype(np.uint8)
    return array

def get_video():
    """Get RGB frame from Kinect"""
    array, _ = freenect.sync_get_video()
    return array

def display_depth(depth):
    """Convert depth to displayable format"""
    # Normalize to 0-255 range
    np.clip(depth, 0, 2**10 - 1, depth)
    depth >>= 2
    depth = depth.astype(np.uint8)

    # Apply colormap for better visualization
    depth_color = cv2.applyColorMap(depth, cv2.COLORMAP_JET)
    return depth_color

def main():
    print("Kinect Gen 1 Test Script")
    print("=" * 50)

    # Test if Kinect is connected
    try:
        ctx = freenect.init()
        if freenect.num_devices(ctx) < 1:
            print("ERROR: No Kinect devices found!")
            print("\nTroubleshooting:")
            print("1. Check USB connection and power adapter")
            print("2. On Linux, ensure user is in 'video' group:")
            print("   sudo usermod -aG video $USER")
            print("3. Check device with: lsusb | grep Xbox")
            return 1

        print(f"✓ Found {freenect.num_devices(ctx)} Kinect device(s)")

    except Exception as e:
        print(f"ERROR: Failed to initialize Kinect: {e}")
        return 1

    # Test depth capture
    try:
        depth, _ = freenect.sync_get_depth()
        print(f"✓ Depth capture working")
        print(f"  - Resolution: {depth.shape}")
        print(f"  - Depth range: {depth.min()} - {depth.max()}")
        print(f"  - Data type: {depth.dtype}")
    except Exception as e:
        print(f"✗ Depth capture failed: {e}")
        return 1

    # Test RGB capture
    try:
        rgb, _ = freenect.sync_get_video()
        print(f"✓ RGB capture working")
        print(f"  - Resolution: {rgb.shape}")
        print(f"  - Data type: {rgb.dtype}")
    except Exception as e:
        print(f"✗ RGB capture failed: {e}")
        return 1

    print("\n" + "=" * 50)
    print("Opening live view...")
    print("Press 'q' to quit, 'd' to toggle depth, 'r' for RGB only")
    print("=" * 50)

    show_depth = True

    try:
        while True:
            # Get frames
            depth = get_depth()
            rgb = get_video()

            # Convert RGB from RGB to BGR for OpenCV
            rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            # Display
            if show_depth:
                depth_display = display_depth(depth)
                # Resize to match RGB for side-by-side display
                depth_display = cv2.resize(depth_display, (640, 480))
                combined = np.hstack([rgb, depth_display])
                cv2.imshow('Kinect Test - RGB (Left) | Depth (Right)', combined)
            else:
                cv2.imshow('Kinect Test - RGB', rgb)

            # Handle keyboard
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                show_depth = True
            elif key == ord('r'):
                show_depth = False

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        cv2.destroyAllWindows()
        freenect.sync_stop()

    print("\nTest completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
