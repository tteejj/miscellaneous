#!/bin/bash
set -e

# Determine user and home directory
if [ "$EUID" -eq 0 ]; then
    USER_HOME="/root"
else
    USER_HOME="$HOME"
fi

# Configuration
CONTAINER_NAME="rpi-chat"
IMAGE_NAME="localhost/rpi-chat:latest"
PORT=5000
DATA_PATH="$USER_HOME/rpi-chat-data"
UPLOADS_PATH="$DATA_PATH/uploads"

echo "🐋 RPi Chat Server - Podman Container"
echo ""

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman not found. Please run install-container.sh first."
    exit 1
fi

# Create data directories with proper ownership
echo "📁 Creating data directories..."
mkdir -p "$DATA_PATH"
mkdir -p "$UPLOADS_PATH"
mkdir -p "$UPLOADS_PATH/thumbnails"
mkdir -p "$UPLOADS_PATH/files"

# Ensure proper permissions (writable by container user UID 1000)
if [ "$EUID" -eq 0 ]; then
    chown -R 1000:1000 "$DATA_PATH"
fi
chmod -R 755 "$DATA_PATH"

# Copy source files to build context
echo "📦 Preparing build context..."
BUILD_DIR=$(mktemp -d)
cp -r ../database.py ../server.py ../templates ../requirements.txt "$BUILD_DIR/"

# Build image
echo "🔨 Building container image..."
podman build -t "$IMAGE_NAME" -f Containerfile "$BUILD_DIR"
rm -rf "$BUILD_DIR"

# Stop existing container if running
if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "🛑 Stopping existing container..."
    podman stop "$CONTAINER_NAME" 2>/dev/null || true
    podman rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# Run container with proper volume mounts
echo "🚀 Starting container..."
podman run -d \
    --name "$CONTAINER_NAME" \
    -p "${PORT}:5000" \
    -v "${DATA_PATH}:/app/data:Z" \
    "$IMAGE_NAME"

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 3

# Check if container is running
if podman ps | grep -q "$CONTAINER_NAME"; then
    echo "✅ Container started successfully!"
else
    echo "❌ Container failed to start. Checking logs..."
    podman logs "$CONTAINER_NAME"
    exit 1
fi

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 Access:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Local: http://$LOCAL_IP:$PORT"
echo "Setup: http://$LOCAL_IP:$PORT/setup"
echo ""
echo "Data stored in: $DATA_PATH"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛠️  Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Logs:    podman logs -f $CONTAINER_NAME"
echo "Stop:    podman stop $CONTAINER_NAME"
echo "Start:   podman start $CONTAINER_NAME"
echo "Shell:   podman exec -it $CONTAINER_NAME /bin/sh"
echo "Remove:  podman rm -f $CONTAINER_NAME"
echo ""
echo "Note: Container will NOT auto-restart on boot."
echo "      Use install-container.sh to enable auto-start with systemd."
echo ""
