#!/bin/bash
set -e

# Configuration
CONTAINER_NAME="rpi-chat"
IMAGE_NAME="localhost/rpi-chat:latest"
PORT=5000
DB_PATH="$HOME/rpi-chat-data/chat.db"
UPLOADS_PATH="$HOME/rpi-chat-data/uploads"

echo "🐋 RPi Chat Server - Podman Container"
echo ""

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman not found. Please run install-container.sh first."
    exit 1
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p "$HOME/rpi-chat-data"
mkdir -p "$UPLOADS_PATH"

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

# Run container
echo "🚀 Starting container..."
podman run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -p "${PORT}:5000" \
    -v "${UPLOADS_PATH}:/app/uploads:Z" \
    -v "${DB_PATH}:/app/chat.db:Z" \
    "$IMAGE_NAME"

# Wait for container to be healthy
echo "⏳ Waiting for container to start..."
sleep 3

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "✅ Container started successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 Access:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Local: http://$LOCAL_IP:$PORT"
echo "Setup: http://localhost:$PORT/setup"
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
