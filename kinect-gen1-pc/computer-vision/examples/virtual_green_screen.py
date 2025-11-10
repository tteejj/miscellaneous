#!/usr/bin/env python3
"""
Virtual Green Screen using Kinect depth data
Replace background without a physical green screen!
"""

import freenect
import cv2
import numpy as np
import argparse
import sys

class VirtualGreenScreen:
    def __init__(self, background_image=None):
        self.background = background_image
        self.threshold = 1500  # mm - objects closer than this are foreground
        self.blur_edges = True
        self.blur_kernel = 15

    def set_threshold(self, threshold):
        """Set foreground/background depth threshold in mm"""
        self.threshold = threshold

    def process(self, rgb, depth):
        """Apply virtual green screen effect"""

        # Create foreground mask (objects closer than threshold)
        foreground_mask = (depth > 0) & (depth < self.threshold)

        # Optional: blur edges for smoother transition
        if self.blur_edges:
            foreground_mask = foreground_mask.astype(np.uint8) * 255
            foreground_mask = cv2.GaussianBlur(foreground_mask,
                                               (self.blur_kernel, self.blur_kernel), 0)
            foreground_mask = foreground_mask.astype(np.float32) / 255.0
        else:
            foreground_mask = foreground_mask.astype(np.float32)

        # Create 3-channel mask
        fg_mask_3ch = np.stack([foreground_mask] * 3, axis=2)

        # If no background image, use solid color
        if self.background is None:
            # Solid color background (green)
            background = np.zeros_like(rgb)
            background[:, :, 1] = 255  # Green channel
        else:
            # Use provided background image
            h, w = rgb.shape[:2]
            background = cv2.resize(self.background, (w, h))

        # Composite: foreground * mask + background * (1 - mask)
        result = (rgb * fg_mask_3ch + background * (1 - fg_mask_3ch)).astype(np.uint8)

        return result, foreground_mask

def main():
    parser = argparse.ArgumentParser(
        description='Virtual green screen using Kinect depth'
    )
    parser.add_argument('--background', '-b', type=str,
                       help='Background image file (default: solid green)')
    parser.add_argument('--threshold', '-t', type=int, default=1500,
                       help='Foreground depth threshold in mm (default: 1500)')
    parser.add_argument('--no-blur', action='store_true',
                       help='Disable edge blurring')

    args = parser.parse_args()

    print("Kinect Virtual Green Screen")
    print("=" * 50)

    # Load background image if provided
    background = None
    if args.background:
        background = cv2.imread(args.background)
        if background is None:
            print(f"ERROR: Could not load background image: {args.background}")
            return 1
        print(f"✓ Loaded background: {args.background}")
    else:
        print("Using solid green background")

    # Test Kinect
    try:
        ctx = freenect.init()
        if freenect.num_devices(ctx) < 1:
            print("ERROR: No Kinect found!")
            return 1
        print("✓ Kinect detected")
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    print("\nControls:")
    print("  q - Quit")
    print("  +/- - Adjust depth threshold")
    print("  b - Toggle edge blur")
    print("  m - Show/hide mask")
    print("  s - Save screenshot")
    print("  r - Reset to default settings")
    print("\nPosition yourself in front of the Kinect")
    print("Objects closer than threshold appear in foreground")
    print("=" * 50)

    # Initialize processor
    vgs = VirtualGreenScreen(background)
    vgs.set_threshold(args.threshold)
    vgs.blur_edges = not args.no_blur

    show_mask = False

    try:
        while True:
            # Capture
            rgb, _ = freenect.sync_get_video()
            depth, _ = freenect.sync_get_depth()

            # Convert to BGR
            rgb_bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            # Process
            result, mask = vgs.process(rgb_bgr, depth)

            # Display
            if show_mask:
                # Show mask visualization
                mask_vis = (mask * 255).astype(np.uint8)
                mask_vis = cv2.cvtColor(mask_vis, cv2.COLOR_GRAY2BGR)
                display = np.hstack([result, mask_vis])
                window_name = 'Virtual Green Screen | Foreground Mask'
            else:
                display = result
                window_name = 'Virtual Green Screen'

            # Add info overlay
            info_text = f"Threshold: {vgs.threshold}mm | Blur: {'ON' if vgs.blur_edges else 'OFF'}"
            cv2.putText(display, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow(window_name, display)

            # Keyboard handling
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

            elif key == ord('+') or key == ord('='):
                vgs.threshold += 100
                print(f"Threshold: {vgs.threshold}mm")

            elif key == ord('-') or key == ord('_'):
                vgs.threshold = max(500, vgs.threshold - 100)
                print(f"Threshold: {vgs.threshold}mm")

            elif key == ord('b'):
                vgs.blur_edges = not vgs.blur_edges
                print(f"Edge blur: {'ON' if vgs.blur_edges else 'OFF'}")

            elif key == ord('m'):
                show_mask = not show_mask

            elif key == ord('s'):
                import time
                filename = f"greenscreen_{time.strftime('%Y%m%d_%H%M%S')}.png"
                cv2.imwrite(filename, result)
                print(f"Saved: {filename}")

            elif key == ord('r'):
                vgs.threshold = args.threshold
                vgs.blur_edges = not args.no_blur
                print("Reset to defaults")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        cv2.destroyAllWindows()
        freenect.sync_stop()

    print("\nVirtual green screen stopped")
    return 0

if __name__ == "__main__":
    sys.exit(main())
