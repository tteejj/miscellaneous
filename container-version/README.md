# RPi Chat Server - Container Version (Podman)

**Lighter than Docker, works great on RPi Zero 2 W!**

## Why Podman?

- ✅ **No daemon** - Saves ~100-150MB RAM vs Docker
- ✅ **Rootless** - Better security
- ✅ **Docker-compatible** - Same commands
- ✅ **Perfect for RPi Zero 2 W** (512MB RAM)

## Quick Install

```bash
cd container-version
./install-container.sh
```

This will:
1. Install Podman
2. Build the container image
3. Run the chat server
4. (Optional) Set up systemd auto-start

## Add HTTPS with Tailscale

```bash
./setup-tailscale.sh
```

**Choose your access mode:**

### Mode 1: Private (Recommended for Family/Friends)
- Users install Tailscale on their devices
- Secure zero-trust access
- Works from anywhere

### Mode 2: Public (Tailscale Funnel)
- **No Tailscale needed for users!**
- Anyone with link can access
- Full HTTPS automatically
- Your existing authentication protects the chat

## Access Options Summary

| Method | User Setup | HTTPS | Remote | PWA Features |
|--------|-----------|-------|--------|--------------|
| **Local Network** | None | ❌ | WiFi only | ⚠️ Limited |
| **Tailscale Private** | Install Tailscale | ✅ | ✅ Anywhere | ✅ Full |
| **Tailscale Funnel** | None | ✅ | ✅ Anywhere | ✅ Full |

## Container Commands

```bash
# View logs
podman logs -f rpi-chat

# Stop container
podman stop rpi-chat

# Start container
podman start rpi-chat

# Restart container
podman restart rpi-chat

# Shell into container
podman exec -it rpi-chat /bin/sh

# Remove container
podman rm -f rpi-chat

# Rebuild image
./build-and-run.sh
```

## Systemd Service Commands

If you installed the systemd service:

```bash
# Start
sudo systemctl start rpi-chat-podman

# Stop
sudo systemctl stop rpi-chat-podman

# Restart
sudo systemctl restart rpi-chat-podman

# Status
sudo systemctl status rpi-chat-podman

# View logs
sudo journalctl -u rpi-chat-podman -f

# Disable auto-start
sudo systemctl disable rpi-chat-podman
```

## Data Persistence

All data is stored in `~/rpi-chat-data/`:
```
~/rpi-chat-data/
├── chat.db          # SQLite database
└── uploads/         # Images and files
    ├── thumbnails/
    └── files/
```

**Backup:**
```bash
tar -czf rpi-chat-backup-$(date +%Y%m%d).tar.gz ~/rpi-chat-data/
```

**Restore:**
```bash
tar -xzf rpi-chat-backup-20250110.tar.gz -C ~/
```

## Updating

```bash
cd /home/pi/miscellaneous
git pull

cd container-version
./build-and-run.sh  # Rebuilds and restarts
```

## Memory Usage

**Expected RAM usage:**
```
Podman daemon:     ~50MB (daemonless!)
Container:         ~80MB
Chat server:       ~50MB
Total:            ~180MB / 512MB
```

Compare to Docker: ~400MB total

## Tailscale URLs

After setup, you can access via:

**Private mode:**
```
https://your-hostname.tailnet-name.ts.net:5000
```

**Public mode (Funnel):**
```
https://your-hostname.tailnet-name.ts.net:5000
```

Get your exact URL:
```bash
echo "https://$(sudo tailscale status --json | grep -o '"DNSName":"[^"]*"' | cut -d'"' -f4 | sed 's/\.$//' ):5000"
```

## PWA Installation (with HTTPS)

Once HTTPS is enabled via Tailscale:

**On Mobile:**
1. Visit the HTTPS URL
2. Tap "Share" (iOS) or "⋮" menu (Android)
3. Select "Add to Home Screen"
4. Icon appears like a native app!

**On Desktop:**
1. Visit the HTTPS URL
2. Look for install icon in address bar
3. Click to install
4. App opens in its own window

**PWA Features:**
- ✅ Offline mode
- ✅ Background notifications
- ✅ Camera/microphone access
- ✅ App icon on home screen
- ✅ Full-screen mode

## Troubleshooting

**Container won't start:**
```bash
podman logs rpi-chat
```

**Port already in use:**
```bash
sudo lsof -i :5000
# or
podman ps -a
```

**Permission issues:**
```bash
# Fix SELinux labels (if using Fedora/RHEL)
podman unshare chown -R 1000:1000 ~/rpi-chat-data
```

**Rebuild from scratch:**
```bash
podman rm -f rpi-chat
podman rmi localhost/rpi-chat:latest
./build-and-run.sh
```

**Tailscale not working:**
```bash
sudo tailscale status
sudo tailscale funnel status
```

## Security Best Practices

1. **Use strong passwords** - Chat has built-in authentication
2. **Funnel mode** - Only enable if you want public access
3. **Regular updates** - `git pull && ./build-and-run.sh`
4. **Backup data** - Regular backups of `~/rpi-chat-data/`
5. **Monitor logs** - `podman logs -f rpi-chat`

## Uninstall

**Stop everything:**
```bash
# Stop container
podman stop rpi-chat
podman rm rpi-chat

# Stop systemd service
sudo systemctl stop rpi-chat-podman
sudo systemctl disable rpi-chat-podman
sudo rm /etc/systemd/system/rpi-chat-podman.service
sudo systemctl daemon-reload

# Remove image
podman rmi localhost/rpi-chat:latest

# Optional: Remove Tailscale
sudo tailscale down
sudo apt remove podman
```

**Keep data:**
```bash
# Your data is safe in ~/rpi-chat-data/
```

**Delete data:**
```bash
rm -rf ~/rpi-chat-data/
```

## Comparison: Container vs Non-Container

| Feature | Container Version | Standard Version |
|---------|------------------|------------------|
| **RAM Usage** | ~180MB | ~50-100MB |
| **Installation** | One script | One script |
| **Isolation** | ✅ Full | ❌ None |
| **Updates** | Rebuild image | `git pull + restart` |
| **Portability** | ✅ Run anywhere | ❌ Pi-specific |
| **Backup** | Copy data folder | Copy data folder |
| **Complexity** | Slightly more | Simpler |

**Recommendation:**
- **RPi Zero 2 W:** Use standard version (saves RAM)
- **RPi 4 (4GB+):** Use container version (better isolation)

## Advanced: Custom Port

Edit `build-and-run.sh`:
```bash
PORT=8080  # Change this line
```

Then rebuild:
```bash
./build-and-run.sh
```

## Support

Issues? Check:
1. `podman logs rpi-chat`
2. `sudo journalctl -u rpi-chat-podman -f`
3. `sudo tailscale status`
4. Main README.md in parent directory
