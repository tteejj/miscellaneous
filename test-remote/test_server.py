#!/usr/bin/env python3
"""
Minimal Flask server for testing TV Remote
No authentication, just pure remote control testing
"""

from flask import Flask, render_template_string, jsonify, request
import logging
from datetime import datetime

app = Flask(__name__)

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Store command history for debugging
command_history = []

@app.route('/')
def index():
    """Serve the test remote page"""
    with open('test_remote.html', 'r') as f:
        return render_template_string(f.read())

@app.route('/api/remote/command', methods=['POST', 'OPTIONS'])
def remote_command():
    """Handle TV remote commands with extensive logging"""

    # Handle CORS preflight
    if request.method == 'OPTIONS':
        app.logger.info('OPTIONS preflight request received')
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    app.logger.info('=' * 60)
    app.logger.info('COMMAND REQUEST RECEIVED')
    app.logger.info('=' * 60)

    # Log request details
    app.logger.info(f'Method: {request.method}')
    app.logger.info(f'Headers: {dict(request.headers)}')
    app.logger.info(f'Content-Type: {request.content_type}')
    app.logger.info(f'Content-Length: {request.content_length}')

    # Get raw data
    raw_data = request.get_data(as_text=True)
    app.logger.info(f'Raw request body: {raw_data}')

    # Try to parse JSON
    try:
        data = request.get_json()
        app.logger.info(f'Parsed JSON: {data}')
        command = data.get('command') if data else None
    except Exception as e:
        app.logger.error(f'JSON parsing error: {e}')
        return jsonify({'error': 'Invalid JSON', 'details': str(e)}), 400

    if not command:
        app.logger.error('No command in request!')
        return jsonify({'error': 'No command provided'}), 400

    # Log successful command
    timestamp = datetime.now().isoformat()
    command_entry = {
        'timestamp': timestamp,
        'command': command,
        'ip': request.remote_addr
    }
    command_history.append(command_entry)

    app.logger.info(f'✓ COMMAND RECEIVED: {command}')
    app.logger.info(f'✓ Total commands received: {len(command_history)}')
    app.logger.info('=' * 60)

    # Return success
    response = jsonify({
        'status': 'success',
        'command': command,
        'timestamp': timestamp,
        'count': len(command_history)
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200

@app.route('/api/history')
def get_history():
    """Get command history for debugging"""
    return jsonify({
        'total': len(command_history),
        'commands': command_history[-20:]  # Last 20 commands
    })

@app.route('/api/test')
def test_endpoint():
    """Simple test endpoint"""
    app.logger.info('Test endpoint called')
    return jsonify({
        'status': 'ok',
        'message': 'Server is running!',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print('=' * 60)
    print('TV REMOTE TEST SERVER')
    print('=' * 60)
    print('Starting server on http://localhost:5555')
    print('Open browser to: http://localhost:5555')
    print('API endpoints:')
    print('  - POST /api/remote/command')
    print('  - GET  /api/history')
    print('  - GET  /api/test')
    print('=' * 60)

    app.run(host='0.0.0.0', port=5555, debug=True)
