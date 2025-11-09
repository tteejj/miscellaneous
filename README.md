# RPi Local Chat Server

A lightweight, PIN-protected chat server designed for Raspberry Pi, enabling local network communication without internet dependency.

## Features

- **PIN-based Authentication**: Secure 6-digit PIN system
- **Real-time Messaging**: Auto-refreshing chat interface
- **No Internet Required**: Fully functional on local network
- **Lightweight**: Minimal resource usage, perfect for Raspberry Pi
- **Modern UI**: Clean, responsive web interface
- **SQLite Database**: Simple, file-based storage

## Prerequisites

- Raspberry Pi (any model with network capability)
- Python 3.7 or higher
- Local network connection

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd miscellaneous
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python3 database.py
```

### 5. Generate First PIN

```bash
python3 auth.py
```

This will output a 6-digit PIN. Save this PIN - you'll need it to log in.

## Usage

### Start the Server

```bash
python3 server.py
```

The server will start on port 5000. You'll see output like:

```
==================================================
🚀 RPi Local Chat Server Starting...
==================================================

  Access the chat at: http://<your-rpi-ip>:5000
  Local: http://localhost:5000

==================================================
```

### Access the Chat

1. Open a web browser on any device connected to the same network
2. Navigate to `http://<your-rpi-ip>:5000`
3. Enter the PIN when prompted
4. Start chatting!

### Generate New PIN

To create a new PIN (invalidates old ones):

```bash
python3 auth.py
```

## Project Structure

```
miscellaneous/
├── server.py           # Flask application
├── database.py         # Database initialization
├── auth.py            # PIN authentication system
├── requirements.txt   # Python dependencies
├── templates/
│   ├── chat.html      # Chat interface
│   └── login.html     # Login page
└── chat.db            # SQLite database (created on first run)
```

## API Endpoints

- `GET /` - Main chat interface (requires authentication)
- `GET /login` - Login page
- `POST /login` - Submit PIN for authentication
- `GET /logout` - Clear session and logout
- `GET /api/messages` - Fetch all messages (JSON)
- `POST /api/messages` - Post new message (JSON)

## Security Notes

- Change the PIN regularly using `auth.py`
- This is designed for trusted local networks only
- Not recommended for public internet exposure
- Uses session-based authentication

## Troubleshooting

### Server won't start

- Check if port 5000 is already in use: `lsof -i :5000`
- Ensure Flask is installed: `pip list | grep Flask`

### Can't connect from other devices

- Verify all devices are on the same network
- Check firewall settings on Raspberry Pi
- Ensure you're using the correct IP address

### Database errors

- Delete `chat.db` and run `python3 database.py` again
- Check file permissions

## Development

### Run in Debug Mode

Edit `server.py` and change:

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## License

MIT License - Feel free to modify and distribute

## Contributing

Pull requests welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All features are tested on Raspberry Pi
- Documentation is updated

## Support

For issues and questions, please open an issue on the repository.
