# DietPi Quick Start Guide

**RPi Chat Server on DietPi** - Complete installation in 3 commands!

## Prerequisites

DietPi comes with git already installed. If not:
```bash
sudo apt-get update && sudo apt-get install -y git
```

## Installation Steps

### 1. Clone the Repository
```bash
cd ~
git clone https://github.com/tteejj/miscellaneous.git
cd miscellaneous
```

### 2. Choose Your Version

#### Option A: Standard Version (Recommended for beginners)
```bash
./install.sh
```

#### Option B: Container Version (Podman + Tailscale)
```bash
cd container-version
./install-container.sh
./setup-tailscale.sh  # Optional: Add HTTPS
```

### 3. Access Your Chat Server

The installer will show you the access URL. Default:
```
http://YOUR_RPI_IP:5000
```

First-time setup page:
```
http://YOUR_RPI_IP:5000/setup
```

## DietPi-Specific Notes

✅ **Fully Supported** - DietPi is detected automatically
✅ **Lightweight** - Perfect for RPi Zero 2 W or RPi 3/4
✅ **Uses systemd** - Service auto-starts on boot
✅ **apt-get** - Standard Debian package manager

### Memory Usage
- **Standard version**: ~50-80 MB RAM
- **Container version**: ~120-150 MB RAM

DietPi's minimal footprint leaves plenty of resources for the chat server!

## Post-Installation

### Check Service Status
```bash
sudo systemctl status rpi-chat
```

### View Logs
```bash
sudo journalctl -u rpi-chat -f
```

### Restart Service
```bash
sudo systemctl restart rpi-chat
```

## Optional: Add HTTPS

### Option 1: Tailscale Funnel (Easiest)
```bash
sudo apt-get install -y tailscale
sudo tailscale up
sudo tailscale funnel --bg 5000 on
```
Access: `https://YOUR-TAILSCALE-HOSTNAME:5000`

### Option 2: Standard Tailscale (Private)
Same as above, but skip the `funnel` command. Users need Tailscale installed.

## Troubleshooting

### Port 5000 Already in Use?
```bash
sudo netstat -tulpn | grep :5000
# Kill the process or change port in server.py
```

### Can't Access from Other Devices?
Check DietPi firewall (if enabled):
```bash
sudo iptables -L
# Allow port 5000 if needed
```

### Python Package Issues?
```bash
pip3 install --user --upgrade -r requirements.txt
```

## Performance Tips

DietPi is optimized out of the box, but for best performance:

1. **Use RPi 3 or newer** for 5+ simultaneous users
2. **RPi Zero 2 W** works great for 2-3 users
3. **Enable swap** if you have < 1GB RAM
4. **Use ethernet** instead of WiFi when possible

## Next Steps

1. Visit `http://YOUR_IP:5000/setup` to create admin account
2. Create channels in Admin Panel
3. Add users for your family/team
4. Optional: Set up Tailscale for remote access

Enjoy your private chat server! 🎉
