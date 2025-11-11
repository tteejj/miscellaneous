# RPi Local Chat Server - Installation Guide

## Quick Install (systemd version)

```bash
./install.sh
```

That's it! The script will:
- Install all dependencies
- Initialize the database
- Set up systemd service
- Start the server automatically

## Access

**Local Network (HTTP):**
```
http://YOUR_PI_IP:5000
```

**First Time Setup:**
```
http://localhost:5000/setup  (from the Pi)
```

## Service Management

```bash
# View logs
sudo journalctl -u rpi-chat -f

# Restart server
sudo systemctl restart rpi-chat

# Stop server
sudo systemctl stop rpi-chat

# Check status
sudo systemctl status rpi-chat

# Disable auto-start
sudo systemctl disable rpi-chat
```

## Adding HTTPS

### Option 1: Tailscale Funnel (Recommended)

**Best for**: Remote access, no domain needed, zero config

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Enable public HTTPS
tailscale funnel --bg 5000 on
```

**Access**: `https://your-pi.tailnet.ts.net:5000`

**Features:**
- ✅ Automatic HTTPS
- ✅ Works from anywhere
- ✅ No router configuration
- ✅ Users don't need Tailscale installed
- ✅ PWA with full features

### Option 2: Caddy (For Custom Domain)

**Best for**: Public website with your own domain

```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | \
  sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/caddy-stable-archive-keyring.gpg] \
  https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main" | \
  sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy

# Configure Caddy
sudo nano /etc/caddy/Caddyfile
```

**Add to Caddyfile:**
```
chat.yourdomain.com {
    reverse_proxy localhost:5000
}
```

```bash
sudo systemctl reload caddy
```

## Updating

```bash
cd /home/pi/miscellaneous  # or your install location
git pull
sudo systemctl restart rpi-chat
```

## Troubleshooting

**Server not starting:**
```bash
sudo journalctl -u rpi-chat -n 50
```

**Port already in use:**
```bash
sudo lsof -i :5000
# Kill the process or change port in server.py
```

**Permission issues:**
```bash
# Check ownership
ls -la /home/pi/miscellaneous

# Fix if needed
sudo chown -R pi:pi /home/pi/miscellaneous
```

## Uninstall

```bash
sudo systemctl stop rpi-chat
sudo systemctl disable rpi-chat
sudo rm /etc/systemd/system/rpi-chat.service
sudo systemctl daemon-reload
```

## Next Steps

For a containerized version with Podman + Tailscale integration, see `container-version/README.md`
