# TV Remote Test Project

Standalone test environment for debugging the Samsung TV remote control.

## Purpose

This is a minimal Flask app with **maximum debugging** to isolate and fix the TV remote button issues.

## Files

- `test_server.py` - Minimal Flask server with extensive logging
- `test_remote.html` - Remote control UI with debug panel
- `README.md` - This file

## Installation

```bash
cd /home/user/test-remote

# Install Flask (if not already installed)
pip3 install flask

# OR on Void Linux:
sudo xbps-install -S python3-Flask
```

## Running

```bash
cd /home/user/test-remote
python3 test_server.py
```

Server will start on: **http://localhost:5555**

## Testing

1. **Open browser**: http://localhost:5555
2. **Look at left panel** - Shows real-time debug info
3. **Run system tests** - Click the 4 test buttons at top
4. **Click any remote button** - Watch debug panel for details

## What to Look For

### In the Browser (Debug Panel)

✅ **Good signs:**
- Status shows "✅ All systems ready!"
- "Found X buttons with data-command"
- When clicking: "📤 Sending command: POWER"
- "✅ Command 'POWER' sent successfully!"

❌ **Bad signs:**
- Status shows "❌ Some tests failed!"
- "Fetch API is not available"
- "Exception sending command: [error]"
- Any red error messages

### In the Terminal (Server Logs)

✅ **Good signs:**
```
COMMAND REQUEST RECEIVED
Method: POST
Parsed JSON: {'command': 'POWER'}
✓ COMMAND RECEIVED: POWER
```

❌ **Bad signs:**
- No logs when clicking buttons (JavaScript not working)
- "JSON parsing error"
- 400/500 status codes

## Debugging Steps

1. **Run all 4 system tests** - Shows if fetch/JSON/DOM work
2. **Click Power button** - Watch BOTH panels
3. **Check browser console** (F12) - Look for errors
4. **Check terminal** - See if server receives requests

## Common Issues

### Buttons don't respond
- Check debug panel: "Found X buttons"
- Check browser console for JavaScript errors
- Try the "Test Event Listeners" button

### Fetch fails
- Check if server is running: curl http://localhost:5555/api/test
- Check browser console for CORS/network errors
- Try "Test Server Connection" button

### Server doesn't log anything
- JavaScript is failing before fetch
- Check browser console
- Run "Test Fetch API" button

## API Endpoints

- `GET  /` - Main remote UI
- `POST /api/remote/command` - Send command (logs everything)
- `GET  /api/history` - See last 20 commands
- `GET  /api/test` - Simple connectivity test

## Testing Command Flow

```
Click Button → JavaScript Event → sendCommand() → Fetch API → Server
                  ↓                    ↓              ↓          ↓
              Log in panel      Log in panel   Log response  Log in terminal
```

Every step is logged. Find where it fails.

## Tips

- Use browser developer tools (F12)
- Watch both debug panel AND terminal
- Test buttons one at a time
- Clear log between tests for clarity
- Check network tab in browser dev tools

## Next Steps After Testing

Once we identify the issue here, we can fix it in the main chat application.
