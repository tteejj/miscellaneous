# 🐳 RPI Chat - Container Deployment Guide

Quick and easy deployment using Podman or Docker, optimized for Raspberry Pi Zero 2 W.

## 📋 Table of Contents

- [Quick Start (Recommended)](#quick-start-recommended)
- [Using Docker Compose](#using-docker-compose)
- [Using Podman Compose](#using-podman-compose)
- [Manual Container Run](#manual-container-run)
- [Pi Zero Optimizations](#pi-zero-optimizations)
- [Troubleshooting](#troubleshooting)
- [Performance Tuning](#performance-tuning)

---

## 🚀 Quick Start (Recommended)

### For Podman (Recommended for Pi)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd miscellaneous

# 2. Run with optimized settings
./run-podman.sh

# 3. Access the chat
# Open http://your-pi-ip:5000 in your browser
```

### For Docker

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd miscellaneous

# 2. Run with optimized settings
./run-docker.sh

# 3. Access the chat
# Open http://your-pi-ip:5000 in your browser
```

That's it! The script handles everything:
- ✅ Builds the optimized container image
- ✅ Sets up tmpfs mounts to reduce SD card writes
- ✅ Configures resource limits for Pi Zero
- ✅ Enables automatic restart
- ✅ Sets up health checks

---

## 🔧 Using Docker Compose

### Production Deployment

```bash
# Start the chat server
docker compose up -d

# View logs
docker compose logs -f

# Stop the server
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

### Development Mode

```bash
# Use development compose file (live code reloading)
docker compose -f compose.dev.yaml up

# The source code is mounted, so changes appear immediately
# (You'll need to refresh your browser)
```

---

## 🔧 Using Podman Compose

```bash
# Install podman-compose if not already installed
pip3 install podman-compose

# Start the chat server
podman-compose up -d

# View logs
podman-compose logs -f

# Stop the server
podman-compose down
```

---

## 🛠️ Manual Container Run

### Build the Image

```bash
# Production build (multi-stage, optimized)
podman build -t rpi-chat:latest -f Containerfile .

# Development build (faster, includes dev tools)
podman build -t rpi-chat:dev -f Containerfile.dev .
```

### Run the Container

```bash
podman run -d \
  --name rpi-chat \
  --restart unless-stopped \
  -p 5000:5000 \
  \
  --tmpfs /app/tmp:size=50M,mode=1777 \
  --tmpfs /dev/shm:size=64M \
  \
  -v $(pwd)/data:/app/data:Z \
  -v $(pwd)/uploads:/app/uploads:Z \
  \
  --memory=256m \
  --memory-swap=256m \
  --cpus=2 \
  \
  --log-driver=json-file \
  --log-opt max-size=1m \
  --log-opt max-file=2 \
  \
  rpi-chat:latest
```

---

## 🎯 Pi Zero Optimizations

### Why These Settings Matter

The Raspberry Pi Zero 2 W has **only 512MB RAM** and a **limited SD card lifespan**. Our configuration is specifically tuned for this:

#### 1. **tmpfs Mounts** (Critical!)

```yaml
tmpfs:
  - /app/tmp:size=50M,mode=1777      # Temporary files in RAM
  - /dev/shm:size=64M                 # Shared memory for gunicorn workers
```

**Why?** Writes to tmpfs go to RAM, not the SD card. This:
- Prevents SD card wear
- Is 100x faster than SD card writes
- Reduces latency

#### 2. **Memory Limits**

```yaml
deploy:
  resources:
    limits:
      memory: 256M      # Max 256MB for the container
      cpus: '2.0'       # Use both CPU cores
```

**Why?** Prevents the container from consuming all 512MB and causing system swapping.

#### 3. **Log Rotation**

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "1m"      # Max 1MB per log file
    max-file: "2"       # Keep only 2 log files
```

**Why?** Limits log files to 2MB total, preventing SD card fills.

#### 4. **Gunicorn Workers**

```bash
CMD ["gunicorn", "--workers", "2", "--threads", "2", "--worker-tmp-dir", "/dev/shm", ...]
```

**Why?**
- 2 workers = optimal for dual-core Pi Zero 2 W
- `--worker-tmp-dir=/dev/shm` = worker temp files go to RAM, not SD card

---

## 🏗️ Advanced Configuration

### Environment Variables

You can customize the deployment by setting these environment variables:

```bash
# In compose.yaml or via -e flag
environment:
  - DATABASE_PATH=/app/data/chat.db
  - UPLOAD_FOLDER=/app/uploads
  - TMP_FOLDER=/app/tmp
  - FLASK_ENV=production

  # Security (if using HTTPS)
  - SESSION_COOKIE_SECURE=true
  - SESSION_COOKIE_HTTPONLY=true
```

### Persistent Data

Data is stored in two directories:

```
./data/          # SQLite database
./uploads/       # User-uploaded images and files
```

**Backup regularly!**

```bash
# Backup
tar -czf rpi-chat-backup-$(date +%Y%m%d).tar.gz data/ uploads/

# Restore
tar -xzf rpi-chat-backup-20250101.tar.gz
```

### Using Named Volumes

Instead of bind mounts, you can use Docker/Podman volumes:

```yaml
volumes:
  - chat-data:/app/data
  - chat-uploads:/app/uploads

volumes:
  chat-data:
  chat-uploads:
```

**Pros:** Better performance, automatic management
**Cons:** Harder to manually inspect/backup

---

## 🔍 Monitoring

### Health Checks

The container includes automatic health checks:

```bash
# Check container health
podman ps

# If unhealthy, check logs
podman logs rpi-chat
```

Health check endpoint: `http://localhost:5000/api/health`

### Resource Usage

```bash
# Real-time stats
podman stats rpi-chat

# Or use docker stats
docker stats rpi-chat
```

### System Monitoring

On the Pi itself:

```bash
# Install the monitoring script (from bare-metal setup)
sudo ./config/optimize-pi-zero.sh

# Then run
rpi-chat-monitor
```

Shows:
- Temperature
- Memory usage
- Disk usage
- Throttling status
- Top processes

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
podman logs rpi-chat

# Common issues:
# 1. Port 5000 already in use
podman ps -a | grep 5000
# Solution: Stop the conflicting container or use a different port

# 2. Permission denied on volumes
# Solution: Add :Z to volume mounts for SELinux
-v $(pwd)/data:/app/data:Z
```

### Out of Memory

```bash
# Check container memory usage
podman stats rpi-chat

# If using >256MB, reduce workers
# Edit compose.yaml:
CMD ["gunicorn", "--workers", "1", ...]  # Reduce from 2 to 1
```

### Slow Performance

```bash
# 1. Check if swapping
free -h

# 2. Check temperature
vcgencmd measure_temp

# 3. Check throttling
vcgencmd get_throttled

# If throttled (not 0x0):
# - Add a heatsink
# - Improve ventilation
# - Reduce worker count
```

### Database Locked Errors

```bash
# This means multiple processes trying to write simultaneously
# Check WAL mode is enabled
sqlite3 data/chat.db "PRAGMA journal_mode;"
# Should return: wal

# If not, fix it:
sqlite3 data/chat.db "PRAGMA journal_mode=WAL;"
```

---

## 📊 Performance Tuning

### For Very Light Usage (1-3 users)

```yaml
# compose.yaml
CMD ["gunicorn", "--workers", "1", "--threads", "2", ...]

deploy:
  resources:
    limits:
      memory: 128M  # Reduce from 256M
```

### For Heavier Usage (5-10 users)

```yaml
# Use standard settings (2 workers, 256M)
# But consider upgrading to Pi 3/4
```

### Custom Port

```yaml
ports:
  - "8080:5000"  # Access on port 8080 instead of 5000
```

### HTTPS with Reverse Proxy

Use nginx or Caddy in front:

```yaml
# docker-compose.yaml
services:
  rpi-chat:
    # ... existing config
    expose:
      - "5000"  # Don't expose to host

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
```

---

## 🔐 Security Best Practices

1. **Change Default Secrets**
   - First user created becomes admin
   - Use strong passwords (8+ characters)

2. **Use HTTPS**
   - Set up reverse proxy with SSL
   - Set `SESSION_COOKIE_SECURE=true`

3. **Firewall**
   ```bash
   # Only allow access from local network
   sudo ufw allow from 192.168.1.0/24 to any port 5000
   ```

4. **Regular Updates**
   ```bash
   # Update base image
   podman pull python:3.11-slim-bookworm

   # Rebuild
   podman build -t rpi-chat:latest -f Containerfile .
   ```

5. **Backup Database**
   ```bash
   # Automated daily backup
   (crontab -l 2>/dev/null; echo "0 2 * * * tar -czf ~/backups/rpi-chat-\$(date +\%Y\%m\%d).tar.gz ~/rpi-chat/data ~/rpi-chat/uploads") | crontab -
   ```

---

## 📦 Container Management Commands

### Podman

```bash
# Start container
podman start rpi-chat

# Stop container
podman stop rpi-chat

# Restart container
podman restart rpi-chat

# View logs (follow)
podman logs -f rpi-chat

# Execute commands inside container
podman exec -it rpi-chat sh

# Remove container
podman rm -f rpi-chat

# Remove image
podman rmi rpi-chat:latest

# Prune unused images/containers
podman system prune -a
```

### Docker

Same commands, just replace `podman` with `docker`.

---

## 🔄 Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
./run-podman.sh  # This stops old container and starts new one

# Or with compose
podman-compose up -d --build
```

---

## 💡 Tips & Tricks

1. **Faster Builds**
   ```bash
   # Use build cache
   podman build --layers -t rpi-chat:latest -f Containerfile .
   ```

2. **Multi-Architecture Builds**
   ```bash
   # If building on x86 for ARM
   podman build --platform linux/arm/v7 -t rpi-chat:latest -f Containerfile .
   ```

3. **Development Workflow**
   ```bash
   # Use dev compose for live reloading
   podman-compose -f compose.dev.yaml up
   # Edit code, refresh browser, see changes
   ```

4. **Network Troubleshooting**
   ```bash
   # Access from host browser
   curl http://localhost:5000/api/health

   # Access from network
   curl http://192.168.1.X:5000/api/health
   ```

---

## 📚 Additional Resources

- [Podman Documentation](https://docs.podman.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Optimizing Pi for Long-Term Use](https://www.raspberrypi.org/)
- [SQLite WAL Mode](https://www.sqlite.org/wal.html)

---

## 🆘 Getting Help

1. **Check logs first:**
   ```bash
   podman logs rpi-chat | tail -50
   ```

2. **Enable debug mode:**
   ```bash
   podman run ... -e FLASK_DEBUG=1 ... rpi-chat:latest
   ```

3. **Test database:**
   ```bash
   podman exec -it rpi-chat sqlite3 /app/data/chat.db "SELECT COUNT(*) FROM users;"
   ```

---

**Enjoy your self-hosted chat server! 🎉**

**Remember:** This setup is optimized for Raspberry Pi Zero 2 W with SD card longevity in mind. All temporary data goes to RAM, not your SD card!
