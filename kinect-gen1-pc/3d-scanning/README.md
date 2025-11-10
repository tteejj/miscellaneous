# 3D Scanning with Kinect Gen 1

Guide for using Kinect Gen 1 for 3D object scanning, room reconstruction, and point cloud generation.

## Table of Contents
1. [Overview](#overview)
2. [Software Options](#software-options)
3. [Python Setup](#python-setup)
4. [Basic Scanning](#basic-scanning)
5. [Advanced Techniques](#advanced-techniques)
6. [Export Formats](#export-formats)

## Overview

The Kinect Gen 1 can capture depth data to create 3D models. While not as accurate as modern LiDAR scanners, it's excellent for:
- Room mapping and layout
- Object scanning (30cm - 2m size)
- Mesh generation for 3D printing
- Point cloud generation
- Educational projects

**Limitations:**
- Resolution: 640x480 depth (VGA)
- Range: 0.8m - 4m (optimal: 1m - 3m)
- Accuracy: ±1-3cm at 2m distance
- No texture mapping on reflective surfaces

## Software Options

### 1. ReconstructMe (Easiest - Windows)
**Discontinued but still works**

Download archived version and follow setup in `reconstructme-setup.md`

**Pros:**
- Simple GUI
- Real-time preview
- Direct STL export

**Cons:**
- No longer maintained
- Windows only
- Requires old GPU drivers

### 2. Skanect (Professional - Windows/Mac)
**Commercial with free tier**

- Website: http://skanect.occipital.com/
- Free version: 5k faces limit
- Pro version: Unlimited, better post-processing

**Features:**
- Real-time reconstruction
- Color texture mapping
- Watertight mesh generation
- Multiple export formats

### 3. Open Source Solutions

**rtabmap (Recommended for Linux)**
```bash
sudo apt-get install rtabmap
```
- SLAM-based 3D mapping
- Point cloud generation
- Loop closure detection

**PCL (Point Cloud Library)**
- Full control over processing
- Python/C++ bindings
- See scripts in this directory

### 4. Custom Python Scripts (Most Flexible)
See examples in `scripts/` directory

## Python Setup

### Install Dependencies

```bash
# Create virtual environment
python3 -m venv kinect-env
source kinect-env/bin/activate  # Windows: kinect-env\Scripts\activate

# Install required packages
pip install numpy
pip install opencv-python
pip install open3d
pip install freenect
pip install matplotlib
```

### Test Kinect Connection

```python
import freenect
import numpy as np

# Get depth frame
depth, _ = freenect.sync_get_depth()
print(f"Depth array shape: {depth.shape}")
print(f"Depth range: {depth.min()} - {depth.max()}")
```

See `scripts/test_kinect.py` for full test script.

## Basic Scanning

### Method 1: Single Frame Point Cloud

**Quick capture of static scene**

```bash
python scripts/capture_single_pointcloud.py --output my_scan.ply
```

**Process:**
1. Position object/scene in view
2. Run script
3. Capture depth frame
4. Convert to point cloud
5. Save as PLY file

**Viewing:**
```bash
# Use CloudCompare, MeshLab, or Open3D viewer
python scripts/view_pointcloud.py my_scan.ply
```

### Method 2: Multi-Frame Scanning

**Better quality by combining multiple views**

```bash
python scripts/capture_multi_frame.py --frames 30 --output room_scan
```

**Process:**
1. Start capture
2. Slowly move Kinect around object/room
3. Script captures and aligns frames
4. Generates combined point cloud
5. Exports mesh

**Tips:**
- Move slowly (< 5cm/second)
- Maintain overlapping views
- Keep object in center of view
- Consistent lighting

### Method 3: Turntable Scanning

**Best for small objects**

**Hardware:**
- Kinect on tripod (fixed position)
- Rotating turntable (manual or motorized)
- Object on turntable

**Process:**
```bash
python scripts/turntable_scan.py --steps 36 --output object_scan
```

1. Place object on turntable
2. Capture frame
3. Rotate 10° (36 steps = 360°)
4. Repeat
5. Stitch frames into complete model

See `turntable-setup.md` for DIY turntable plans.

## Advanced Techniques

### Improving Scan Quality

**1. Multiple Passes**
Scan from different angles and merge:
```bash
python scripts/merge_scans.py scan1.ply scan2.ply scan3.ply --output merged.ply
```

**2. Noise Filtering**
Remove outliers and smooth surface:
```bash
python scripts/filter_pointcloud.py input.ply --output clean.ply \
  --remove-outliers \
  --smooth \
  --downsample 0.01
```

**3. Mesh Generation**
Convert point cloud to solid mesh:
```bash
python scripts/pointcloud_to_mesh.py input.ply --output model.stl \
  --method poisson \
  --depth 10
```

### Room Scanning

**Large space reconstruction**

```bash
python scripts/scan_room.py --output living_room
```

**Best Practices:**
- Start from corner
- Move in systematic pattern
- Scan walls, floor, ceiling separately
- Merge scans in post-processing

**Applications:**
- Interior design
- VR environment recreation
- Furniture layout planning
- Renovation planning

### Object Scanning for 3D Printing

**Workflow:**
1. Scan object from multiple angles
2. Merge point clouds
3. Generate watertight mesh
4. Fill holes
5. Export STL for slicing

```bash
# Complete pipeline
python scripts/scan_for_3d_print.py \
  --input raw_scans/ \
  --output printable_model.stl \
  --fill-holes \
  --make-watertight \
  --scale 1.0
```

## Export Formats

### Point Cloud Formats

**PLY (Polygon File Format)**
- Most common
- Supports color
- Human-readable ASCII option
```bash
python scripts/export_ply.py --ascii --with-color
```

**PCD (Point Cloud Data)**
- PCL native format
- Efficient binary
```bash
python scripts/export_pcd.py --binary
```

**XYZ**
- Simple text format
- X Y Z coordinates per line
```bash
python scripts/export_xyz.py
```

### Mesh Formats

**STL (Stereolithography)**
- 3D printing standard
- Binary or ASCII
```bash
python scripts/export_stl.py --binary
```

**OBJ (Wavefront)**
- Widely supported
- Supports textures (MTL file)
```bash
python scripts/export_obj.py --with-texture
```

**PLY Mesh**
- Can include color per vertex
```bash
python scripts/export_mesh_ply.py --vertex-colors
```

## Scripts Reference

All scripts are in the `scripts/` directory:

### Basic Capture
- `test_kinect.py` - Test Kinect connection
- `capture_single_pointcloud.py` - Quick single-frame capture
- `capture_multi_frame.py` - Multi-view capture with alignment
- `turntable_scan.py` - Automated turntable scanning

### Processing
- `filter_pointcloud.py` - Noise removal and smoothing
- `merge_scans.py` - Combine multiple scans
- `pointcloud_to_mesh.py` - Surface reconstruction
- `mesh_cleanup.py` - Fill holes, make watertight

### Viewing
- `view_pointcloud.py` - Interactive point cloud viewer
- `view_mesh.py` - Mesh visualization

### Export
- `export_ply.py` - Export PLY format
- `export_stl.py` - Export STL for 3D printing
- `export_obj.py` - Export OBJ with textures

## Performance Tips

1. **Lighting**: Even, diffuse lighting (no direct sunlight)
2. **Surface**: Matte surfaces work best (no mirrors, glass, black objects)
3. **Distance**: Keep objects 1-2m from Kinect
4. **Speed**: Move slowly for multi-frame scans
5. **Processing**: Use downsampling for faster processing
6. **GPU**: Some algorithms can use GPU acceleration

## Calibration

For accurate measurements, calibrate your Kinect:

```bash
python scripts/calibrate_kinect.py --checkerboard 9x6 --square-size 25mm
```

Saves calibration to `calibration.json` for use in other scripts.

## Troubleshooting

### Noisy Point Clouds
- Improve lighting
- Reduce range (closer to Kinect)
- Use statistical outlier removal
- Increase samples per point

### Missing Data / Holes
- Reflective or transparent surfaces (won't scan)
- Outside depth range
- Scan from multiple angles
- Use hole-filling algorithms

### Alignment Issues (Multi-Frame)
- Move more slowly
- Increase frame overlap
- Use markers for reference
- Manual alignment in CloudCompare/MeshLab

### Low Resolution
- Gen 1 is limited to 640x480
- Scan closer for more detail
- Use multiple overlapping scans
- Upsampling can help but doesn't add real detail

## Example Applications

### 1. Room Layout
```bash
python scripts/scan_room.py --output room.ply
python scripts/generate_floorplan.py room.ply --output floorplan.svg
```

### 2. 3D Print Scan
```bash
python scripts/scan_for_3d_print.py \
  --turntable \
  --steps 36 \
  --output figurine.stl
```

### 3. Volume Measurement
```bash
python scripts/measure_volume.py object.ply
# Output: Volume: 1250.3 cm³
```

### 4. Reverse Engineering
```bash
python scripts/extract_dimensions.py part.ply
# Output: Length: 15.3cm, Width: 8.2cm, Height: 4.1cm
```

## Additional Resources

- CloudCompare (free mesh editor): https://www.cloudcompare.org/
- MeshLab (free mesh processing): https://www.meshlab.net/
- Open3D documentation: http://www.open3d.org/docs/
- PCL tutorials: https://pcl.readthedocs.io/

---

**Next Steps:**
1. Test basic capture with `test_kinect.py`
2. Try single-frame point cloud capture
3. Experiment with different objects and distances
4. Move to multi-frame scanning for better quality
