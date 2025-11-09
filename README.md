# RPi Local Chat Server

A lightweight, multi-channel chat server for Raspberry Pi with PIN authentication, admin management, and mobile-optimized interface. Perfect for local network communication without internet dependency.

## Features

- **Multi-Channel Support**: Organize conversations with #general, #pictures, #random, and custom channels
- **Admin-Only Channel Creation**: Control who can create new channels
- **Web-Based PIN Management**: Set and change PINs through the admin interface
- **Mobile-Optimized**: Collapsible channel sidebar, touch-friendly inputs
- **Cross-Device Compatible**: Works on Safari, Chrome, Firefox, Fire tablets, and more
- **Auto-Start on Boot**: Systemd (Debian/Ubuntu) and runit (Void Linux) support
- **Real-time Messaging**: Auto-refreshing chat with 2-second polling
- **No Internet Required**: Fully functional on local network
- **Lightweight**: Minimal resource usage, perfect for Raspberry Pi
- **SQLite Database**: Simple, persistent file-based storage

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create virtual environment
- Install all dependencies
- Initialize database
- Configure system service (systemd or runit)
- Create start/stop helper scripts

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 database.py

# Start server
python3 server.py
```

## First Time Setup

1. Start the server (see above)
2. Visit `http://<your-rpi-ip>:5000/setup`
3. Create your admin username and PIN
4. You're ready to chat!

## Usage

### Starting the Server

**Manual start:**
```bash
./start-chat.sh
```

**Auto-start on boot (systemd):**
```bash
sudo systemctl enable rpi-chat
sudo systemctl start rpi-chat
```

**Auto-start on boot (runit/Void):**
```bash
sudo ln -s /etc/sv/rpi-chat /var/service/
```

### Stopping the Server

**Manual:**
```bash
./stop-chat.sh
```

**Systemd:**
```bash
sudo systemctl stop rpi-chat
```

**Runit:**
```bash
sudo rm /var/service/rpi-chat
```

### Accessing the Chat

1. Open browser: `http://<your-rpi-ip>:5000`
2. Enter your PIN
3. Choose a channel from the sidebar (☰ on mobile)
4. Start chatting!

### Admin Features

Admins can access the admin panel at `/admin` to:
- Change the PIN (persistent across reboots)
- Add new admin users
- Create new channels (via "+ New Channel" button)

## Project Structure

```
miscellaneous/
├── server.py              # Flask application with channel support
├── database.py            # Database with channels, admins, messages
├── auth.py               # PIN authentication
├── setup.sh              # Automated setup script
├── start-chat.sh         # Helper: start server manually
├── stop-chat.sh          # Helper: stop server
├── rpi-chat.service      # Systemd service file
├── runit-service/
│   └── run               # Runit service file
├── requirements.txt      # Python dependencies
├── templates/
│   ├── chat.html         # Multi-channel chat interface
│   ├── login.html        # PIN login page
│   ├── setup.html        # Initial setup page
│   └── admin.html        # Admin management panel
└── chat.db               # SQLite database (auto-created)
```

## API Endpoints

### Public
- `GET /login` - Login page
- `POST /login` - Submit PIN
- `GET /setup` - Initial setup (only if no admins exist)

### Authenticated
- `GET /` - Chat interface
- `GET /logout` - Logout
- `GET /api/channels` - List all channels
- `GET /api/messages/<channel_id>` - Get messages for channel
- `POST /api/messages/<channel_id>` - Post message to channel

### Admin Only
- `GET /admin` - Admin panel
- `POST /api/channels` - Create new channel
- `POST /api/admin/set-pin` - Update PIN
- `POST /api/admin/add-admin` - Add admin user
- `GET /api/admin/check` - Check admin status

## Mobile Compatibility

The interface is fully optimized for mobile devices:

- **Safari (iOS)**: PIN input uses numeric keyboard
- **Chrome (Android)**: Full support with touch-optimized inputs
- **Fire Tablet**: Fixed input visibility issues, 44px touch targets
- **Pixel Phone**: Responsive layout adapts to screen size

Channel sidebar:
- Desktop: Always visible on left
- Mobile: Collapsible via ☰ menu button
- Auto-hides after channel selection on mobile

## System Service Setup

### Debian/Ubuntu/Raspbian (systemd)

Automatic (via setup.sh):
```bash
./setup.sh
sudo systemctl enable rpi-chat
sudo systemctl start rpi-chat
```

Manual:
```bash
sudo cp rpi-chat.service /etc/systemd/system/
# Edit the file to update User and paths
sudo systemctl daemon-reload
sudo systemctl enable rpi-chat
sudo systemctl start rpi-chat
```

### Void Linux (runit)

Automatic (via setup.sh):
```bash
./setup.sh
sudo ln -s /etc/sv/rpi-chat /var/service/
```

Manual:
```bash
sudo cp -r runit-service /etc/sv/rpi-chat
# Edit /etc/sv/rpi-chat/run to update user and paths
sudo chmod +x /etc/sv/rpi-chat/run
sudo ln -s /etc/sv/rpi-chat /var/service/
```

## Security Notes

- **PIN Management**: Change PIN anytime via `/admin` - persists across reboots
- **Admin Access**: Only admins can create channels and manage settings
- **Local Network Only**: Designed for trusted local networks
- **Session-Based Auth**: Secure cookie-based sessions
- **Not for Internet**: Do NOT expose directly to the internet

## Troubleshooting

### Server won't start
- Check port 5000: `lsof -i :5000` or `ss -tulpn | grep 5000`
- Verify Flask installed: `pip list | grep Flask`
- Check logs: `sudo journalctl -u rpi-chat -f` (systemd)

### Can't connect from other devices
- Verify same network: `ip addr` or `ifconfig`
- Check firewall: `sudo ufw status` (if using ufw)
- Test connectivity: `ping <rpi-ip>` from other device

### Database errors
```bash
rm chat.db
python3 database.py
```

### Mobile input not visible
- Clear browser cache
- Update to latest code
- Check browser developer console for errors

### PIN not persisting
- Ensure using `/admin` to set PIN (not `auth.py`)
- Check database permissions: `ls -l chat.db`

## Default Channels

- **#general**: Main discussion channel
- **#pictures**: Share images and media
- **#random**: Off-topic conversations

Admins can create additional channels via the admin panel.

## Browser Support

- ✅ Chrome (Desktop & Android)
- ✅ Firefox (Desktop & Mobile)
- ✅ Safari (Desktop & iOS)
- ✅ Edge
- ✅ Fire Tablet (Chrome/Silk)
- ✅ Mobile browsers with 768px+ screens

## Development

### Debug Mode

Edit `server.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Database Schema

**channels**: id, name, display_name, created_at
**messages**: id, channel_id, username, message, timestamp
**auth**: id, pin, created_at, active
**admins**: id, username, created_at

## License

MIT License - Free to modify and distribute

## Contributing

Pull requests welcome! Please:
- Follow PEP 8 style guidelines
- Test on actual Raspberry Pi hardware
- Test on mobile devices (especially tablets)
- Update documentation
- Test both Debian and Void Linux if modifying setup

## Support

For issues and questions, open an issue on the repository.

---

Made with ❤️ for local network communication
