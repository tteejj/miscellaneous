#!/bin/bash
# Optimization script for Raspberry Pi Zero 2 W
# Reduces SD card writes and improves performance

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Pi Zero 2 W Optimization Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# 1. Disable swap (reduces SD card writes)
echo -e "${YELLOW}[1/8] Configuring swap...${NC}"
if [ -f /etc/dphys-swapfile ]; then
    echo "CONF_SWAPSIZE=0" > /etc/dphys-swapfile
    dphys-swapfile swapoff
    dphys-swapfile uninstall
    systemctl disable dphys-swapfile
    echo -e "${GREEN}✓ Swap disabled${NC}"
else
    swapoff -a
    sed -i '/swap/d' /etc/fstab
    echo -e "${GREEN}✓ Swap disabled via fstab${NC}"
fi

# 2. Configure tmpfs mounts
echo -e "${YELLOW}[2/8] Setting up tmpfs mounts...${NC}"
mkdir -p /tmp/rpi-chat /var/log/rpi-chat

# Backup fstab
cp /etc/fstab /etc/fstab.backup.$(date +%Y%m%d)

# Add tmpfs entries if not already present
if ! grep -q "/tmp/rpi-chat" /etc/fstab; then
    echo "tmpfs /tmp/rpi-chat tmpfs defaults,noatime,nosuid,nodev,mode=1777,size=50M 0 0" >> /etc/fstab
    echo -e "${GREEN}✓ Added /tmp/rpi-chat tmpfs${NC}"
fi

if ! grep -q "/var/log/rpi-chat" /etc/fstab; then
    echo "tmpfs /var/log/rpi-chat tmpfs defaults,noatime,nosuid,nodev,mode=0755,size=30M 0 0" >> /etc/fstab
    echo -e "${GREEN}✓ Added /var/log/rpi-chat tmpfs${NC}"
fi

mount -a
echo -e "${GREEN}✓ tmpfs mounts active${NC}"

# 3. Configure journald for reduced writes
echo -e "${YELLOW}[3/8] Configuring journald...${NC}"
mkdir -p /etc/systemd/journald.conf.d/
cat > /etc/systemd/journald.conf.d/00-rpi-optimize.conf <<EOF
[Journal]
Storage=volatile
RuntimeMaxUse=50M
Compress=yes
SyncIntervalSec=5m
RateLimitInterval=30s
RateLimitBurst=1000
EOF
systemctl restart systemd-journald
echo -e "${GREEN}✓ Journald configured for volatile storage${NC}"

# 4. Optimize filesystem mounts (noatime)
echo -e "${YELLOW}[4/8] Optimizing filesystem mounts...${NC}"
if ! grep -q "noatime" /etc/fstab | grep -q "/$"; then
    sed -i 's/defaults/defaults,noatime/g' /etc/fstab
    echo -e "${GREEN}✓ Added noatime to mounts${NC}"
    echo -e "${YELLOW}Note: Reboot required for mount options to take effect${NC}"
fi

# 5. Configure system limits
echo -e "${YELLOW}[5/8] Setting system limits...${NC}"
cat > /etc/sysctl.d/99-rpi-chat.conf <<EOF
# Reduce swappiness (prefer RAM over swap)
vm.swappiness=10

# Reduce disk write cache
vm.dirty_ratio=10
vm.dirty_background_ratio=5

# Increase file descriptor limits
fs.file-max=65536

# Network optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
EOF
sysctl -p /etc/sysctl.d/99-rpi-chat.conf
echo -e "${GREEN}✓ System limits configured${NC}"

# 6. Disable unnecessary services
echo -e "${YELLOW}[6/8] Disabling unnecessary services...${NC}"
SERVICES_TO_DISABLE=(
    "bluetooth.service"
    "hciuart.service"
    "apt-daily.timer"
    "apt-daily-upgrade.timer"
    "man-db.timer"
)

for service in "${SERVICES_TO_DISABLE[@]}"; do
    if systemctl is-enabled "$service" 2>/dev/null | grep -q "enabled"; then
        systemctl disable "$service"
        systemctl stop "$service" 2>/dev/null || true
        echo -e "${GREEN}✓ Disabled $service${NC}"
    fi
done

# 7. Disable WiFi power management (reduces latency)
echo -e "${YELLOW}[7/8] Disabling WiFi power management...${NC}"
cat > /etc/NetworkManager/conf.d/wifi-powersave.conf <<EOF
[connection]
wifi.powersave = 2
EOF

# Also create rc.local entry for older systems
if [ -f /etc/rc.local ]; then
    if ! grep -q "iwconfig wlan0 power off" /etc/rc.local; then
        sed -i '/^exit 0/i iwconfig wlan0 power off 2>/dev/null || true' /etc/rc.local
    fi
fi
echo -e "${GREEN}✓ WiFi power management disabled${NC}"

# 8. Create monitoring script
echo -e "${YELLOW}[8/8] Creating monitoring script...${NC}"
cat > /usr/local/bin/rpi-chat-monitor <<'EOF'
#!/bin/bash
# RPI Chat monitoring script

echo "=== RPI Chat System Status ==="
echo ""

# Temperature
TEMP=$(vcgencmd measure_temp | cut -d'=' -f2)
echo "Temperature: $TEMP"

# Memory usage
echo ""
echo "Memory Usage:"
free -h | grep -E "Mem|Swap"

# Disk usage
echo ""
echo "Disk Usage:"
df -h / | tail -1

# Throttling status
THROTTLED=$(vcgencmd get_throttled)
echo ""
echo "Throttle Status: $THROTTLED"
if [ "$THROTTLED" != "throttled=0x0" ]; then
    echo "WARNING: System has been throttled!"
fi

# RPI Chat service status
echo ""
echo "RPI Chat Service:"
systemctl status rpi-chat --no-pager -l | head -n 5

# tmpfs mounts
echo ""
echo "tmpfs Mounts:"
df -h | grep tmpfs | grep -E "rpi-chat|shm"

# Top processes by memory
echo ""
echo "Top 5 Processes by Memory:"
ps aux --sort=-%mem | head -n 6
EOF

chmod +x /usr/local/bin/rpi-chat-monitor
echo -e "${GREEN}✓ Monitoring script created: rpi-chat-monitor${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Optimization Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Summary of changes:${NC}"
echo "  ✓ Swap disabled"
echo "  ✓ tmpfs configured for /tmp and /var/log"
echo "  ✓ Journald configured for volatile storage"
echo "  ✓ Filesystem mounts optimized with noatime"
echo "  ✓ System limits tuned"
echo "  ✓ Unnecessary services disabled"
echo "  ✓ WiFi power management disabled"
echo "  ✓ Monitoring script installed"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Reboot your Pi: sudo reboot"
echo "  2. After reboot, verify tmpfs: df -h"
echo "  3. Monitor system: rpi-chat-monitor"
echo ""
echo -e "${YELLOW}Backup created: /etc/fstab.backup.$(date +%Y%m%d)${NC}"
