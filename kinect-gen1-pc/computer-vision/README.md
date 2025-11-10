# Computer Vision with Kinect Gen 1

Explore depth sensing, object detection, motion tracking, and computer vision experiments using Kinect's RGB and depth cameras.

## Table of Contents
1. [Overview](#overview)
2. [Basic CV Operations](#basic-cv-operations)
3. [Depth-Based Applications](#depth-based-applications)
4. [Object Detection & Tracking](#object-detection--tracking)
5. [Background Subtraction](#background-subtraction)
6. [Motion Detection](#motion-detection)
7. [Advanced Projects](#advanced-projects)

## Overview

Kinect Gen 1 provides unique capabilities for computer vision:

**RGB Camera:**
- Resolution: 640x480 @ 30fps
- Standard computer vision (OpenCV)

**Depth Camera:**
- Resolution: 640x480 depth map
- Range: 0.8m - 4m
- Accuracy: ~1cm at 2m
- Works in darkness (IR-based)

**Advantages over standard webcams:**
- 3D position data
- Depth segmentation
- Works in low light
- Background removal
- Distance measurement

## Basic CV Operations

### Capture RGB and Depth

```python
import freenect
import cv2
import numpy as np

# Get frames
rgb, _ = freenect.sync_get_video()  # RGB: 640x480x3
depth, _ = freenect.sync_get_depth()  # Depth: 640x480

# Convert RGB to BGR for OpenCV
rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

# Display
cv2.imshow('RGB', rgb)
cv2.imshow('Depth', depth.astype(np.uint8))
cv2.waitKey(1)
```

See `examples/basic_capture.py`

### Depth Colorization

```python
def colorize_depth(depth):
    """Apply colormap to depth for visualization"""
    # Normalize to 0-255
    depth_normalized = ((depth - depth.min()) /
                       (depth.max() - depth.min()) * 255).astype(np.uint8)

    # Apply colormap
    depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)

    return depth_colored
```

See `examples/depth_visualization.py`

### Aligned RGB-D

Align RGB and depth images for per-pixel depth:

```python
def align_rgb_depth(rgb, depth):
    """
    Align RGB and depth (requires calibration)
    Returns RGB image with depth channel
    """
    # Simple alignment (works if cameras are close)
    # For better results, use camera calibration

    rgbd = np.dstack([rgb, depth])
    return rgbd
```

See `examples/rgbd_alignment.py`

## Depth-Based Applications

### Distance Measurement

Measure real-world distance to objects:

```python
def measure_distance(depth, x, y, radius=5):
    """
    Measure distance at pixel (x, y)
    Averages over small region for stability
    """
    region = depth[y-radius:y+radius, x-radius:x+radius]
    valid = region[region > 0]

    if len(valid) == 0:
        return None

    # Kinect depth is in mm
    distance_mm = np.median(valid)
    distance_m = distance_mm / 1000.0

    return distance_m
```

**Use cases:**
- Room dimensions
- Object sizing
- Collision avoidance
- Parking assist

See `examples/distance_measurement.py`

### Depth Filtering

Remove objects by distance:

```python
def filter_by_depth(rgb, depth, min_depth, max_depth):
    """Keep only pixels within depth range"""
    mask = (depth >= min_depth) & (depth <= max_depth)

    # Create 3-channel mask
    mask_3ch = np.stack([mask, mask, mask], axis=2)

    # Apply mask
    filtered = rgb * mask_3ch

    return filtered
```

**Applications:**
- Isolate person from background
- Remove background objects
- Focus on specific depth plane

See `examples/depth_filtering.py`

### 3D Histogram

Visualize depth distribution:

```python
def depth_histogram(depth):
    """Create histogram of depth values"""
    valid = depth[depth > 0]

    plt.hist(valid, bins=50, range=(500, 4000))
    plt.xlabel('Depth (mm)')
    plt.ylabel('Pixel count')
    plt.title('Depth Distribution')
    plt.show()
```

See `examples/depth_histogram.py`

## Object Detection & Tracking

### Nearest Object Detection

Find closest object (likely a hand or person):

```python
def find_nearest_object(depth, min_size=100):
    """
    Find largest blob at minimum depth
    Returns bounding box and center point
    """
    # Get minimum depth
    valid = depth[depth > 0]
    if len(valid) == 0:
        return None

    min_depth = valid.min()

    # Threshold near minimum
    mask = (depth > 0) & (depth < min_depth + 100)
    mask = mask.astype(np.uint8) * 255

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Get largest contour
    largest = max(contours, key=cv2.contourArea)

    if cv2.contourArea(largest) < min_size:
        return None

    # Get bounding box
    x, y, w, h = cv2.boundingRect(largest)

    # Get center
    cx = x + w // 2
    cy = y + h // 2

    return {
        'bbox': (x, y, w, h),
        'center': (cx, cy),
        'depth': min_depth
    }
```

See `examples/nearest_object_detection.py`

### Multi-Object Detection

Segment multiple objects by depth:

```python
def segment_objects(depth, num_layers=5):
    """
    Segment depth into layers
    Returns list of binary masks for each layer
    """
    valid = depth[depth > 0]
    min_d = valid.min()
    max_d = valid.max()

    # Create depth layers
    layers = []
    step = (max_d - min_d) / num_layers

    for i in range(num_layers):
        d_min = min_d + i * step
        d_max = d_min + step

        mask = (depth >= d_min) & (depth < d_max)
        layers.append(mask)

    return layers
```

See `examples/depth_segmentation.py`

### Color + Depth Tracking

Combine color detection with depth filtering:

```python
def track_red_object(rgb, depth, max_distance=2000):
    """
    Track red objects within certain distance
    Combines color segmentation with depth filtering
    """
    # Convert to HSV
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)

    # Red color range
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)

    # Depth mask
    mask_depth = (depth > 0) & (depth < max_distance)

    # Combine masks
    mask_combined = mask_red & mask_depth.astype(np.uint8)

    # Find contours
    contours, _ = cv2.findContours(mask_combined, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)

    return contours
```

See `examples/color_depth_tracking.py`

## Background Subtraction

Remove static background using depth:

### Simple Background Removal

```python
class DepthBackgroundSubtractor:
    def __init__(self):
        self.background = None

    def learn_background(self, depth, frames=30):
        """Capture background depth"""
        depths = []

        for i in range(frames):
            d, _ = freenect.sync_get_depth()
            depths.append(d)
            time.sleep(0.033)  # ~30 fps

        # Use median to handle noise
        self.background = np.median(depths, axis=0)

    def subtract(self, depth, threshold=100):
        """Remove background, keep foreground objects"""
        if self.background is None:
            return depth

        # Find pixels significantly closer than background
        diff = self.background - depth
        foreground_mask = diff > threshold

        return foreground_mask
```

**Applications:**
- Green screen effect (without green screen!)
- Person detection
- Object appearance detection
- Privacy (blur background)

See `examples/background_removal.py`

### Virtual Green Screen

```python
def virtual_green_screen(rgb, depth, background_image, threshold=1500):
    """
    Replace background with custom image
    No physical green screen needed!
    """
    # Create mask for foreground (close objects)
    foreground_mask = depth < threshold
    background_mask = ~foreground_mask

    # Ensure 3 channels
    fg_mask_3ch = np.stack([foreground_mask]*3, axis=2)
    bg_mask_3ch = np.stack([background_mask]*3, axis=2)

    # Resize background image
    background_resized = cv2.resize(background_image, (rgb.shape[1], rgb.shape[0]))

    # Composite
    result = (rgb * fg_mask_3ch + background_resized * bg_mask_3ch).astype(np.uint8)

    return result
```

See `examples/virtual_green_screen.py`

## Motion Detection

### Depth-Based Motion Detection

Detect motion using depth changes:

```python
class DepthMotionDetector:
    def __init__(self, threshold=50, min_area=500):
        self.prev_depth = None
        self.threshold = threshold
        self.min_area = min_area

    def detect(self, depth):
        """Detect moving regions"""
        if self.prev_depth is None:
            self.prev_depth = depth.copy()
            return None

        # Calculate difference
        diff = cv2.absdiff(depth, self.prev_depth)

        # Threshold
        _, motion_mask = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)
        motion_mask = motion_mask.astype(np.uint8)

        # Find contours
        contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        # Filter by size
        motion_regions = [c for c in contours if cv2.contourArea(c) > self.min_area]

        # Update
        self.prev_depth = depth.copy()

        return motion_regions
```

See `examples/motion_detection.py`

### Intrusion Detection

Detect objects entering a zone:

```python
def intrusion_detection(depth, zone_depth_min, zone_depth_max, zone_rect):
    """
    Detect intrusion into defined 3D zone
    zone_rect: (x, y, w, h) in image coordinates
    zone_depth_min/max: depth range in mm
    """
    x, y, w, h = zone_rect

    # Extract zone
    zone_depth = depth[y:y+h, x:x+w]

    # Check if anything in depth range
    intrusion = ((zone_depth >= zone_depth_min) &
                 (zone_depth <= zone_depth_max))

    intrusion_pixels = np.sum(intrusion)

    return intrusion_pixels > 0, intrusion_pixels
```

**Use cases:**
- Security system
- Parking sensor
- Safety zone monitoring
- Touchless interfaces

See `examples/intrusion_detection.py`

## Advanced Projects

### 1. People Counter

Count people entering/exiting:

```bash
python examples/people_counter.py --line-position 320
```

- Draw virtual line across doorway
- Track objects crossing line
- Distinguish entry vs exit by direction
- Count total occupancy

### 2. Gesture Recognition

Recognize hand gestures from depth:

```bash
python examples/depth_gesture_recognition.py
```

- Extract hand shape from depth
- Calculate features (area, perimeter, convexity)
- Classify gestures (rock, paper, scissors, etc.)
- Train custom gestures

### 3. Touchless Interface

Create virtual touch screen in air:

```bash
python examples/touchless_interface.py
```

- Define interaction plane at certain depth
- Detect "touches" when hand crosses plane
- Create buttons, sliders, etc. in 3D space
- No physical contact needed

### 4. Augmented Reality

Add virtual objects aligned with real world:

```bash
python examples/simple_ar.py
```

- Detect planes (floor, walls, tables)
- Place virtual objects on surfaces
- Proper depth occlusion
- Simple AR without markers

### 5. Body Measurement

Estimate body dimensions:

```bash
python examples/body_measurement.py
```

- Detect person silhouette
- Calculate height, width
- Estimate body volume
- Fitness/health tracking

### 6. Fall Detection

Detect when person falls:

```bash
python examples/fall_detection.py
```

- Track person's vertical position
- Detect sudden drops
- Alert system for elderly care
- Privacy-preserving (no actual image saved)

## Performance Tips

1. **Use depth only when possible**: Faster than RGB processing
2. **Downsample**: 320x240 often sufficient for many tasks
3. **Vectorize operations**: Use numpy, avoid loops
4. **Multi-threading**: Separate capture and processing
5. **GPU acceleration**: Use cv2.cuda for supported operations

## Example Code Structure

```python
import freenect
import cv2
import numpy as np

class KinectApp:
    def __init__(self):
        self.running = True

    def process_frame(self, rgb, depth):
        """Override this with your processing"""
        pass

    def run(self):
        while self.running:
            # Capture
            rgb, _ = freenect.sync_get_video()
            depth, _ = freenect.sync_get_depth()

            # Convert
            rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            # Process
            result = self.process_frame(rgb, depth)

            # Display
            cv2.imshow('Result', result)

            # Handle input
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False

        cv2.destroyAllWindows()
        freenect.sync_stop()

# Use:
class MyApp(KinectApp):
    def process_frame(self, rgb, depth):
        # Your code here
        return rgb

app = MyApp()
app.run()
```

See `examples/app_template.py`

## Calibration

For accurate measurements, calibrate camera:

```bash
python scripts/calibrate_cameras.py
```

Generates calibration file with:
- RGB camera intrinsics
- Depth camera intrinsics
- RGB-D extrinsics (alignment)

Use calibration in your applications for:
- Accurate distance measurement
- Proper RGB-D alignment
- Undistortion
- 3D reconstruction

## Datasets

Capture your own datasets:

```bash
python scripts/capture_dataset.py --output ./my_dataset --frames 1000
```

Useful for:
- Machine learning training
- Testing algorithms
- Benchmarking
- Sharing examples

## Example Scripts

All in `examples/` directory:

**Basic:**
- `basic_capture.py` - Simple RGB + depth capture
- `depth_visualization.py` - Various depth colorization
- `rgbd_alignment.py` - Align RGB and depth

**Measurement:**
- `distance_measurement.py` - Click to measure distance
- `depth_histogram.py` - Visualize depth distribution
- `depth_filtering.py` - Filter by depth range

**Detection:**
- `nearest_object_detection.py` - Find closest object
- `depth_segmentation.py` - Segment by depth layers
- `color_depth_tracking.py` - Combined color/depth tracking

**Background:**
- `background_removal.py` - Remove static background
- `virtual_green_screen.py` - Replace background

**Motion:**
- `motion_detection.py` - Depth-based motion detect
- `intrusion_detection.py` - Zone intrusion alarm

**Advanced:**
- `people_counter.py` - Count people crossing line
- `depth_gesture_recognition.py` - Gesture classifier
- `touchless_interface.py` - Virtual touch screen
- `simple_ar.py` - Augmented reality
- `body_measurement.py` - Body dimension estimation
- `fall_detection.py` - Elderly fall detection

## Resources

- OpenCV documentation: https://docs.opencv.org/
- Kinect for Windows SDK: https://developer.microsoft.com/en-us/windows/kinect
- Computer vision tutorials: https://www.pyimagesearch.com/
- Academic papers on depth sensing

---

**Next Steps:**
1. Try basic capture to familiarize yourself with data
2. Experiment with depth filtering and segmentation
3. Build a simple motion detector
4. Combine depth with color for robust tracking
5. Create your own custom application!
