# RPi Chat Server - Deployment Guide

## 🎯 Which Version Should You Use?

### Quick Decision Tree

```
Do you have RPi Zero 2 W (512MB RAM)?
├─ Yes → Use Standard Version (systemd)
└─ No → Do you have RPi 4 (4GB+)?
    ├─ Yes → Use Container Version (Podman)
    └─ RPi 3/4 (1-2GB) → Use Standard Version
```

## 📊 Detailed Comparison

### Standard Version (systemd)

**Best for:** RPi Zero 2 W, RPi 3, simple setups

```bash
./install.sh
```

**Pros:**
- ✅ Minimal RAM usage (~50-100MB)
- ✅ Direct Python execution (no overhead)
- ✅ Simpler troubleshooting
- ✅ Faster startup
- ✅ Perfect for RPi Zero 2 W

**Cons:**
- ❌ No isolation
- ❌ Manual dependency management
- ❌ Less portable

**Memory:** ~100MB total

---

### Container Version (Podman + systemd)

**Best for:** RPi 4 (4GB+), multiple deployments

```bash
cd container-version
./install-container.sh
```

**Pros:**
- ✅ Full application isolation
- ✅ Reproducible builds
- ✅ Easy updates (rebuild image)
- ✅ Portable across systems
- ✅ No dependency conflicts

**Cons:**
- ❌ Higher RAM usage (~180MB)
- ❌ Slightly more complex
- ❌ Slower startup

**Memory:** ~180MB total

---

## 🔐 HTTPS Options (Both Versions)

### Tailscale Funnel (Recommended)

**✅ Best for:** Everyone

**Features:**
- No domain needed
- Automatic HTTPS
- Works from anywhere
- Users don't need Tailscale installed (Funnel mode)
- Zero configuration

**Setup (Standard):**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
sudo tailscale funnel --bg 5000 on
```

**Setup (Container):**
```bash
cd container-version
./setup-tailscale.sh
```

---

### Caddy Reverse Proxy

**✅ Best for:** Custom domain, public website

**Features:**
- Your own domain
- Automatic SSL renewal
- Professional setup

**Setup:**
```bash
sudo apt install caddy
# Edit /etc/caddy/Caddyfile
chat.yourdomain.com {
    reverse_proxy localhost:5000
}
sudo systemctl reload caddy
```

---

## 📱 Access Modes Explained

### Mode 1: Local Network Only
```
URL: http://192.168.1.50:5000
```
- ✅ Works immediately
- ✅ No setup needed
- ❌ Only on same WiFi
- ❌ No HTTPS (limited PWA features)

### Mode 2: Tailscale Private
```
URL: https://rpi-chat.tailnet.ts.net:5000
```
- ✅ Secure remote access
- ✅ Full HTTPS
- ✅ Works anywhere
- ⚠️ Users need Tailscale installed

### Mode 3: Tailscale Funnel (Public)
```
URL: https://rpi-chat.tailnet.ts.net:5000
```
- ✅ Public HTTPS access
- ✅ Users need nothing installed
- ✅ Works anywhere
- ✅ Full PWA features
- ⚠️ Public to internet (use authentication!)

---

## 🚀 Installation Examples

### Example 1: RPi Zero 2 W (Home Family Chat)

**Hardware:** RPi Zero 2 W (512MB RAM)
**Users:** 5 family members on same WiFi
**Access:** Local network only

```bash
# Install standard version
./install.sh

# Access at: http://192.168.1.50:5000
```

**Why:** Minimal RAM usage, no remote access needed

---

### Example 2: RPi 4 (Friend Group with Remote Access)

**Hardware:** RPi 4 (4GB RAM)
**Users:** 10 friends, need access from anywhere
**Access:** Remote with HTTPS

```bash
# Install container version
cd container-version
./install-container.sh

# Add Tailscale Funnel (public HTTPS)
./setup-tailscale.sh
# Choose option 2 (Public)

# Share: https://rpi-chat.tailnet.ts.net:5000
```

**Why:** Container isolation, public HTTPS, PWA features

---

### Example 3: RPi 3 (Community Chat)

**Hardware:** RPi 3 (1GB RAM)
**Users:** 20 people, custom domain
**Access:** Public website

```bash
# Install standard version (save RAM)
./install.sh

# Install Caddy
sudo apt install caddy

# Configure domain
sudo nano /etc/caddy/Caddyfile
# Add: chat.yourdomain.com { reverse_proxy localhost:5000 }

sudo systemctl reload caddy
```

**Why:** Standard version for RAM savings, Caddy for professional setup

---

## 📋 Feature Availability

| Feature | Standard | Container | HTTPS Required |
|---------|----------|-----------|----------------|
| **Basic Chat** | ✅ | ✅ | ❌ |
| **Real-time Updates** | ✅ | ✅ | ❌ |
| **File Upload** | ✅ | ✅ | ❌ |
| **Notifications** | ⚠️ Limited | ⚠️ Limited | ✅ Full |
| **PWA Install** | ❌ | ❌ | ✅ |
| **Offline Mode** | ❌ | ❌ | ✅ |
| **Camera Access** | ❌ | ❌ | ✅ |
| **Background Sync** | ❌ | ❌ | ✅ |
| **Remote Access** | ⚠️ Port Forward | ⚠️ Port Forward | ✅ Tailscale |

---

## 🔧 Switching Between Versions

### From Standard to Container:

```bash
# Stop standard version
sudo systemctl stop rpi-chat
sudo systemctl disable rpi-chat

# Backup data
cp chat.db ~/rpi-chat-data/
cp -r uploads ~/rpi-chat-data/

# Install container version
cd container-version
./install-container.sh
```

### From Container to Standard:

```bash
# Stop container
podman stop rpi-chat

# Copy data back
cp ~/rpi-chat-data/chat.db ./
cp -r ~/rpi-chat-data/uploads ./

# Install standard version
cd ..
./install.sh
```

---

## 💾 Backup & Restore

### Standard Version:
```bash
# Backup
tar -czf backup-$(date +%Y%m%d).tar.gz chat.db uploads/

# Restore
tar -xzf backup-20250110.tar.gz
```

### Container Version:
```bash
# Backup
tar -czf backup-$(date +%Y%m%d).tar.gz ~/rpi-chat-data/

# Restore
tar -xzf backup-20250110.tar.gz -C ~/
```

---

## 🎓 Learning Path

### Just Starting?
1. Use Standard Version
2. Local network only
3. Get familiar with features

### Want Remote Access?
1. Keep Standard Version
2. Add Tailscale Funnel
3. Share HTTPS link

### Want Full Isolation?
1. Switch to Container Version
2. Learn Podman basics
3. Experiment with builds

---

## 🆘 Quick Troubleshooting

### Standard Version:
```bash
# Check logs
sudo journalctl -u rpi-chat -f

# Restart
sudo systemctl restart rpi-chat

# Check if running
sudo systemctl status rpi-chat
```

### Container Version:
```bash
# Check logs
podman logs -f rpi-chat

# Restart
podman restart rpi-chat

# Check if running
podman ps
```

### Tailscale:
```bash
# Check status
sudo tailscale status

# Check funnel
sudo tailscale funnel status

# Restart
sudo systemctl restart tailscaled
```

---

## 🎯 Recommendations by Use Case

| Use Case | Version | HTTPS | Why |
|----------|---------|-------|-----|
| **Home family chat** | Standard | Optional | Simple, low resources |
| **Friend group remote** | Either | Tailscale | Easy remote access |
| **Community (20+ users)** | Standard | Caddy + Domain | Professional, save RAM |
| **Development/Testing** | Container | Optional | Easy rebuilds |
| **Multi-site deployment** | Container | Tailscale | Reproducible |

---

## 📚 Next Steps

1. **Choose your version** (see decision tree above)
2. **Install** (one command!)
3. **Add HTTPS** (if needed)
4. **Create first user** (visit /setup)
5. **Invite users** (share link)
6. **Enjoy chatting!** 🎉
