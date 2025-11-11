#!/bin/bash
# Quick container rebuild script

echo "🔄 Rebuilding container with latest code..."

cd ~/miscellaneous/container-version

echo "1️⃣ Stopping old container..."
podman stop rpi-chat 2>/dev/null || true
podman rm rpi-chat 2>/dev/null || true

echo "2️⃣ Removing old image..."
podman rmi localhost/rpi-chat:latest 2>/dev/null || true

echo "3️⃣ Rebuilding with new code..."
./build-and-run.sh

echo "✅ Done! Try accessing setup now."
