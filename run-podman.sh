#!/bin/bash
# Podman run script optimized for Raspberry Pi Zero 2 W
# This script reduces SD card writes using tmpfs mounts

set -e

CONTAINER_NAME="rpi-chat"
IMAGE_NAME="rpi-chat:latest"
HOST_PORT="${PORT:-5000}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting RPI Chat with Podman${NC}"

# Stop and remove existing container if running
if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}Stopping existing container...${NC}"
    podman stop "$CONTAINER_NAME" 2>/dev/null || true
    podman rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# Create persistent directories if they don't exist
mkdir -p data uploads/thumbnails uploads/files uploads/avatars

# Build image if it doesn't exist
if ! podman image exists "$IMAGE_NAME"; then
    echo -e "${GREEN}Building container image...${NC}"
    podman build -t "$IMAGE_NAME" -f Containerfile .
fi

echo -e "${GREEN}Starting container...${NC}"

# Run container with optimizations for Pi Zero 2 W
podman run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -p "${HOST_PORT}:5000" \
    \
    `# tmpfs mounts to reduce SD card writes` \
    --tmpfs /app/tmp:size=50M,mode=1777 \
    --tmpfs /dev/shm:size=64M \
    \
    `# Persistent volumes` \
    -v "$(pwd)/data:/app/data:Z" \
    -v "$(pwd)/uploads:/app/uploads:Z" \
    \
    `# Resource limits (256MB max for container on 512MB Pi)` \
    --memory=256m \
    --memory-swap=256m \
    --cpus=2 \
    \
    `# Logging - limit to prevent SD wear` \
    --log-driver=json-file \
    --log-opt max-size=1m \
    --log-opt max-file=2 \
    \
    `# Security` \
    --security-opt no-new-privileges \
    --cap-drop ALL \
    --cap-add NET_BIND_SERVICE \
    \
    `# Health check` \
    --health-cmd='python -c "import requests; requests.get(\"http://localhost:5000/api/health\", timeout=5)"' \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    --health-start-period=10s \
    \
    "$IMAGE_NAME"

# Wait for container to be healthy
echo -e "${YELLOW}Waiting for container to be healthy...${NC}"
sleep 5

# Check container status
if podman ps --filter "name=${CONTAINER_NAME}" --filter "status=running" | grep -q "$CONTAINER_NAME"; then
    echo -e "${GREEN}✅ RPI Chat is running!${NC}"
    echo -e "${GREEN}Access it at: http://localhost:${HOST_PORT}${NC}"
    echo ""
    echo "Useful commands:"
    echo "  podman logs -f $CONTAINER_NAME     # View logs"
    echo "  podman stop $CONTAINER_NAME        # Stop container"
    echo "  podman restart $CONTAINER_NAME     # Restart container"
    echo "  podman exec -it $CONTAINER_NAME sh # Access container shell"
else
    echo -e "${RED}❌ Failed to start container${NC}"
    echo "Check logs with: podman logs $CONTAINER_NAME"
    exit 1
fi
