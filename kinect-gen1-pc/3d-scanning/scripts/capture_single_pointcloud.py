#!/usr/bin/env python3
"""
Capture a single frame from Kinect and convert to point cloud
Saves as PLY file for viewing in CloudCompare, MeshLab, or other 3D software
"""

import freenect
import numpy as np
import argparse
import sys
from pathlib import Path

def get_depth_and_rgb():
    """Capture depth and RGB frames from Kinect"""
    depth, _ = freenect.sync_get_depth()
    rgb, _ = freenect.sync_get_video()
    return depth, rgb

def depth_to_pointcloud(depth, rgb=None):
    """
    Convert depth map to 3D point cloud

    Args:
        depth: numpy array of depth values (480x640)
        rgb: optional RGB image for color mapping

    Returns:
        points: Nx3 array of XYZ coordinates
        colors: Nx3 array of RGB colors (if rgb provided)
    """
    # Kinect Gen 1 depth camera intrinsics (approximate)
    # These values are for 640x480 depth resolution
    fx = 594.21  # focal length x
    fy = 591.04  # focal length y
    cx = 339.5   # principal point x
    cy = 242.7   # principal point y

    # Get image dimensions
    h, w = depth.shape

    # Create mesh grid of pixel coordinates
    u = np.arange(w)
    v = np.arange(h)
    u, v = np.meshgrid(u, v)

    # Filter invalid depth (0 values)
    valid = depth > 0

    # Get valid coordinates
    u_valid = u[valid]
    v_valid = v[valid]
    z_valid = depth[valid].astype(np.float32)

    # Convert to metric (Kinect depth is in mm, convert to meters)
    z_valid = z_valid / 1000.0

    # Calculate 3D coordinates
    x = (u_valid - cx) * z_valid / fx
    y = (v_valid - cy) * z_valid / fy
    z = z_valid

    # Stack into Nx3 array
    points = np.stack([x, y, z], axis=1)

    # Get colors if RGB provided
    colors = None
    if rgb is not None:
        # Extract RGB values at valid depth points
        colors = rgb[valid]

    return points, colors

def save_ply(filename, points, colors=None):
    """
    Save point cloud to PLY file

    Args:
        filename: output file path
        points: Nx3 array of XYZ coordinates
        colors: optional Nx3 array of RGB colors
    """
    n_points = len(points)
    has_color = colors is not None

    with open(filename, 'w') as f:
        # Write header
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {n_points}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")

        if has_color:
            f.write("property uchar red\n")
            f.write("property uchar green\n")
            f.write("property uchar blue\n")

        f.write("end_header\n")

        # Write point data
        for i in range(n_points):
            x, y, z = points[i]
            if has_color:
                r, g, b = colors[i]
                f.write(f"{x} {y} {z} {r} {g} {b}\n")
            else:
                f.write(f"{x} {y} {z}\n")

    print(f"Saved {n_points} points to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Capture point cloud from Kinect Gen 1')
    parser.add_argument('--output', '-o', type=str, default='scan.ply',
                        help='Output PLY filename (default: scan.ply)')
    parser.add_argument('--no-color', action='store_true',
                        help='Save without RGB colors')
    parser.add_argument('--preview', action='store_true',
                        help='Show preview before capturing')
    parser.add_argument('--downsample', type=int, default=1,
                        help='Downsample factor (1=full res, 2=half, etc)')

    args = parser.parse_args()

    print("Kinect Point Cloud Capture")
    print("=" * 50)

    # Test Kinect connection
    try:
        ctx = freenect.init()
        if freenect.num_devices(ctx) < 1:
            print("ERROR: No Kinect found!")
            return 1
        print("✓ Kinect detected")
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    # Preview mode
    if args.preview:
        print("\nPreview mode - press SPACE to capture, 'q' to quit")
        import cv2

        try:
            while True:
                depth, rgb = get_depth_and_rgb()

                # Visualize depth
                depth_display = depth.astype(np.uint8)
                depth_display = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)

                # Convert RGB to BGR
                rgb_display = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

                # Show side by side
                combined = np.hstack([rgb_display, depth_display])
                cv2.imshow('Preview - Press SPACE to capture', combined)

                key = cv2.waitKey(10) & 0xFF
                if key == ord(' '):
                    print("Capturing...")
                    break
                elif key == ord('q'):
                    print("Cancelled")
                    cv2.destroyAllWindows()
                    return 0

            cv2.destroyAllWindows()
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            return 0
    else:
        print("\nCapturing frame...")

    # Capture frame
    try:
        depth, rgb = get_depth_and_rgb()
        print(f"✓ Captured {depth.shape[0]}x{depth.shape[1]} depth frame")
    except Exception as e:
        print(f"ERROR: Capture failed: {e}")
        return 1

    # Downsample if requested
    if args.downsample > 1:
        print(f"Downsampling by factor {args.downsample}...")
        depth = depth[::args.downsample, ::args.downsample]
        rgb = rgb[::args.downsample, ::args.downsample]

    # Convert to point cloud
    print("Converting to point cloud...")
    use_color = not args.no_color
    points, colors = depth_to_pointcloud(depth, rgb if use_color else None)

    print(f"✓ Generated {len(points)} 3D points")

    # Calculate statistics
    print("\nPoint cloud statistics:")
    print(f"  X range: {points[:, 0].min():.2f}m to {points[:, 0].max():.2f}m")
    print(f"  Y range: {points[:, 1].min():.2f}m to {points[:, 1].max():.2f}m")
    print(f"  Z range: {points[:, 2].min():.2f}m to {points[:, 2].max():.2f}m")

    # Save to file
    print(f"\nSaving to {args.output}...")
    save_ply(args.output, points, colors)

    print("\n" + "=" * 50)
    print("Success! View with:")
    print(f"  python view_pointcloud.py {args.output}")
    print("Or open in CloudCompare, MeshLab, or any PLY viewer")
    print("=" * 50)

    freenect.sync_stop()
    return 0

if __name__ == "__main__":
    sys.exit(main())
