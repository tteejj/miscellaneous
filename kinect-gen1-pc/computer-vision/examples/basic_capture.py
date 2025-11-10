#!/usr/bin/env python3
"""
Basic RGB and Depth capture from Kinect Gen 1
Displays both streams side-by-side with depth colorization
"""

import freenect
import cv2
import numpy as np
import sys

def colorize_depth(depth):
    """Convert depth to colored visualization"""
    # Handle invalid depth
    depth_copy = depth.copy()
    depth_copy[depth_copy == 0] = depth_copy.max()

    # Normalize to 0-255
    depth_min = depth_copy.min()
    depth_max = depth_copy.max()

    if depth_max - depth_min > 0:
        normalized = ((depth_copy - depth_min) / (depth_max - depth_min) * 255).astype(np.uint8)
    else:
        normalized = np.zeros_like(depth, dtype=np.uint8)

    # Apply colormap (JET: blue=far, red=close)
    colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)

    # Make invalid pixels black
    colored[depth == 0] = [0, 0, 0]

    return colored

def main():
    print("Kinect Basic Capture")
    print("=" * 50)

    # Test Kinect
    try:
        ctx = freenect.init()
        if freenect.num_devices(ctx) < 1:
            print("ERROR: No Kinect found!")
            print("\nTroubleshooting:")
            print("1. Check USB and power connections")
            print("2. Ensure drivers are installed (libfreenect)")
            print("3. Check permissions (add user to 'video' group on Linux)")
            return 1
        print("✓ Kinect detected")
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    print("\nControls:")
    print("  q - Quit")
    print("  d - Toggle depth colormap")
    print("  r - RGB only")
    print("  s - Save screenshot")
    print("  f - Show FPS")
    print("=" * 50)

    colormap_idx = 0
    colormaps = [
        cv2.COLORMAP_JET,
        cv2.COLORMAP_HOT,
        cv2.COLORMAP_RAINBOW,
        cv2.COLORMAP_VIRIDIS,
        cv2.COLORMAP_PLASMA,
    ]
    colormap_names = ['JET', 'HOT', 'RAINBOW', 'VIRIDIS', 'PLASMA']

    show_depth = True
    show_fps = False
    frame_count = 0
    import time
    start_time = time.time()

    try:
        while True:
            # Capture frames
            rgb, _ = freenect.sync_get_video()
            depth, _ = freenect.sync_get_depth()

            # Convert RGB to BGR for OpenCV
            rgb_bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            # Process depth
            if show_depth:
                depth_colored = colorize_depth(depth)

                # Add info text
                cv2.putText(depth_colored, f"Colormap: {colormap_names[colormap_idx]}",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Add depth info at center
                h, w = depth.shape
                center_depth = depth[h//2, w//2]
                if center_depth > 0:
                    distance_m = center_depth / 1000.0
                    cv2.putText(depth_colored, f"Center: {distance_m:.2f}m",
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Draw center crosshair
                cv2.drawMarker(depth_colored, (w//2, h//2), (0, 255, 0),
                              cv2.MARKER_CROSS, 20, 2)

                # Combine side by side
                combined = np.hstack([rgb_bgr, depth_colored])
                window_title = 'Kinect - RGB (Left) | Depth (Right)'
            else:
                combined = rgb_bgr
                window_title = 'Kinect - RGB Only'

            # Add FPS if enabled
            if show_fps:
                frame_count += 1
                elapsed = time.time() - start_time
                if elapsed > 0:
                    fps = frame_count / elapsed
                    cv2.putText(combined, f"FPS: {fps:.1f}",
                               (10, combined.shape[0] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Display
            cv2.imshow(window_title, combined)

            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print("\nQuitting...")
                break

            elif key == ord('d'):
                # Cycle through colormaps
                colormap_idx = (colormap_idx + 1) % len(colormaps)
                print(f"Colormap: {colormap_names[colormap_idx]}")

            elif key == ord('r'):
                show_depth = not show_depth
                print(f"Depth display: {'ON' if show_depth else 'OFF'}")

            elif key == ord('s'):
                # Save screenshot
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                rgb_filename = f"kinect_rgb_{timestamp}.png"
                depth_filename = f"kinect_depth_{timestamp}.png"

                cv2.imwrite(rgb_filename, rgb_bgr)
                if show_depth:
                    cv2.imwrite(depth_filename, depth_colored)

                print(f"Saved: {rgb_filename}")
                if show_depth:
                    print(f"       {depth_filename}")

            elif key == ord('f'):
                show_fps = not show_fps
                frame_count = 0
                start_time = time.time()
                print(f"FPS display: {'ON' if show_fps else 'OFF'}")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        cv2.destroyAllWindows()
        freenect.sync_stop()

    print("Capture stopped")
    return 0

if __name__ == "__main__":
    sys.exit(main())
