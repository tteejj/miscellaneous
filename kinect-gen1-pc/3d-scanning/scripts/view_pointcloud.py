#!/usr/bin/env python3
"""
Simple point cloud viewer using Open3D
Displays PLY files with interactive controls
"""

import argparse
import sys

try:
    import open3d as o3d
except ImportError:
    print("ERROR: open3d not installed")
    print("Install with: pip install open3d")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='View point cloud PLY files')
    parser.add_argument('file', type=str, help='PLY file to view')
    parser.add_argument('--downsample', type=float, default=0,
                        help='Voxel size for downsampling (0=no downsample)')
    parser.add_argument('--estimate-normals', action='store_true',
                        help='Estimate surface normals for better visualization')

    args = parser.parse_args()

    print(f"Loading {args.file}...")

    # Load point cloud
    try:
        pcd = o3d.io.read_point_cloud(args.file)
    except Exception as e:
        print(f"ERROR: Failed to load file: {e}")
        return 1

    print(f"✓ Loaded {len(pcd.points)} points")

    # Downsample if requested
    if args.downsample > 0:
        print(f"Downsampling with voxel size {args.downsample}...")
        pcd = pcd.voxel_down_sample(voxel_size=args.downsample)
        print(f"✓ Downsampled to {len(pcd.points)} points")

    # Estimate normals if requested
    if args.estimate_normals:
        print("Estimating normals...")
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
        )
        print("✓ Normals estimated")

    # Display statistics
    print("\nPoint cloud info:")
    print(f"  Points: {len(pcd.points)}")
    print(f"  Has colors: {pcd.has_colors()}")
    print(f"  Has normals: {pcd.has_normals()}")

    if len(pcd.points) > 0:
        bbox = pcd.get_axis_aligned_bounding_box()
        extent = bbox.get_extent()
        print(f"  Bounding box: {extent[0]:.2f} x {extent[1]:.2f} x {extent[2]:.2f} m")

    # Visualize
    print("\nControls:")
    print("  - Mouse drag: Rotate")
    print("  - Mouse wheel: Zoom")
    print("  - Shift + mouse: Pan")
    print("  - Press 'H' in viewer for more help")
    print("\nOpening viewer...")

    o3d.visualization.draw_geometries(
        [pcd],
        window_name=f"Point Cloud Viewer - {args.file}",
        width=1280,
        height=720,
        point_show_normal=args.estimate_normals
    )

    return 0

if __name__ == "__main__":
    sys.exit(main())
