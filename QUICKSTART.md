# RPi Chat Server - Quick Start

## 🎯 Pick Your Path

### Path 1: Standard (systemd) - Recommended for RPi Zero 2 W

```bash
./install.sh
```

**Done!** Access at `http://YOUR_PI_IP:5000`

---

### Path 2: Container (Podman) - For RPi 4+

```bash
cd container-version
./install-container.sh
```

**Done!** Access at `http://YOUR_PI_IP:5000`

---

## 🔐 Want HTTPS? (Optional)

### Standard Version:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
sudo tailscale funnel --bg 5000 on
```

### Container Version:
```bash
cd container-version
./setup-tailscale.sh
```

**Result:** `https://your-pi.tailnet.ts.net:5000`

---

## 📱 User Access

### Local Network (No HTTPS):
- URL: `http://192.168.1.X:5000`
- Works: Same WiFi only
- PWA: Limited features

### Tailscale Funnel (HTTPS):
- URL: `https://your-pi.tailnet.ts.net:5000`
- Works: Anywhere, anyone with link
- PWA: **Full features** (install as app, offline mode, notifications)
- Users: **No installation needed**

---

## 🎉 First Login

1. Visit the URL
2. Click "Setup" (first time only)
3. Create admin account
4. Start chatting!

---

## 📚 Full Docs

- **Standard:** `INSTALL.md`
- **Container:** `container-version/README.md`
- **Comparison:** `DEPLOYMENT-GUIDE.md`

---

## 🆘 Help

```bash
# Standard version
sudo journalctl -u rpi-chat -f

# Container version
podman logs -f rpi-chat
```
