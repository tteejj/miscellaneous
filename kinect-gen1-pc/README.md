# Kinect Gen 1 (Xbox 360) PC Project

Comprehensive guide and toolset for using the Xbox 360 Kinect sensor on PC for head tracking, 3D scanning, gesture control, and computer vision applications.

## Hardware Requirements

- **Kinect for Xbox 360** (Gen 1 sensor)
- **Kinect to USB adapter** with power supply (~$8 on Amazon)
- USB 2.0 or 3.0 port
- Windows 10/11 or Linux

## Project Structure

```
kinect-gen1-pc/
├── head-tracking/          # Opentrack setup and configuration for seated use
├── 3d-scanning/            # 3D reconstruction and scanning tools
├── gesture-control/        # Gesture recognition and control systems
├── computer-vision/        # OpenCV and CV experiments
├── llm-integration/        # AI-powered vision with LLM models (NEW!)
├── scripts/                # Installation and utility scripts
└── docs/                   # Additional documentation
```

## Quick Start

### 1. Driver Installation
See [scripts/setup-drivers.md](scripts/setup-drivers.md) for detailed installation instructions.

### 2. Choose Your Application
- **Head Tracking** → [head-tracking/README.md](head-tracking/README.md)
- **3D Scanning** → [3d-scanning/README.md](3d-scanning/README.md)
- **Gesture Control** → [gesture-control/README.md](gesture-control/README.md)
- **Computer Vision** → [computer-vision/README.md](computer-vision/README.md)
- **🆕 LLM Integration** → [llm-integration/README.md](llm-integration/README.md) - AI-powered vision!

## Use Cases

### Head Tracking (Opentrack)
- Elite Dangerous, DCS World, racing simulators
- FPS games for leaning/looking mechanics
- Flight simulators
- **Optimized for seated positions**

### 3D Scanning
- Object reconstruction
- Room mapping
- 3D model creation for 3D printing

### Gesture Control
- Hands-free PC control
- Custom gesture interfaces
- Interactive applications

### Computer Vision
- Depth mapping
- Object detection
- Motion tracking
- Skeleton tracking
- Research and experimentation

### 🆕 LLM Integration (AI-Powered Vision)
- **Scene understanding** - "What do you see?"
- **Object finding** - "Where are my keys?"
- **Natural language gestures** - Define gestures with words, not code
- **Visual Q&A** - Ask questions about what Kinect sees
- **Smart automation** - Context-aware home control
- **Accessibility** - Describe surroundings for visually impaired

## System Requirements

### Software Dependencies
- Python 3.8+ (for scripts)
- OpenCV (for computer vision)
- libfreenect (Kinect drivers)
- Opentrack (for head tracking)

### Operating Systems
- Windows 10/11 (recommended for gaming)
- Linux (Ubuntu/Debian for development)
- macOS (limited support)

## Safety & Setup Tips

1. **Lighting**: Avoid direct sunlight or IR interference
2. **Distance**: Optimal range 1.2m - 3.5m (seated: 1.2m - 2m)
3. **Height**: Position Kinect at head level or slightly above
4. **Angle**: Tilt down 5-15° for seated positions
5. **Background**: Clear background improves tracking

## Contributing

This is a personal project but feel free to adapt and extend for your own use.

## Resources

- [OpenKinect/libfreenect](https://github.com/OpenKinect/libfreenect)
- [Opentrack](https://github.com/opentrack/opentrack)
- [OpenCV Documentation](https://docs.opencv.org/)

## License

Documentation and scripts provided as-is for educational purposes.
