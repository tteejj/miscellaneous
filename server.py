"""
Flask server for RPi Local Chat Server
Provides web interface for local network chat with multi-channel support
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from datetime import datetime
from database import DB_PATH, init_db
from auth import verify_pin, create_new_pin
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def is_admin(username):
    """Check if user is an admin"""
    if not username:
        return False
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM admins WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


@app.route('/')
def index():
    """Main chat interface"""
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """PIN authentication page"""
    if request.method == 'POST':
        pin = request.form.get('pin', '')
        if verify_pin(pin):
            session['authenticated'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid PIN')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin')
def admin_panel():
    """Admin management interface"""
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    username = session.get('username', '')
    if not is_admin(username):
        return "Access denied. Admin only.", 403

    return render_template('admin.html')


@app.route('/api/channels', methods=['GET'])
def get_channels():
    """Get all channels"""
    if 'authenticated' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, display_name FROM channels ORDER BY id ASC')
    channels = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(channels)


@app.route('/api/channels', methods=['POST'])
def create_channel():
    """Create a new channel (admin only)"""
    if 'authenticated' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    username = session.get('username', '')
    if not is_admin(username):
        return jsonify({'error': 'Admin privileges required'}), 403

    data = request.get_json()
    name = data.get('name', '').strip().lower()
    display_name = data.get('display_name', '').strip()

    if not name or not display_name:
        return jsonify({'error': 'Name and display name required'}), 400

    # Ensure display_name starts with #
    if not display_name.startswith('#'):
        display_name = '#' + display_name

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO channels (name, display_name) VALUES (?, ?)',
            (name, display_name)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': new_id, 'name': name, 'display_name': display_name}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Channel already exists'}), 400


@app.route('/api/messages/<int:channel_id>', methods=['GET'])
def get_messages(channel_id):
    """Get messages for a specific channel"""
    if 'authenticated' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, message, timestamp
        FROM messages
        WHERE channel_id = ?
        ORDER BY timestamp ASC
    ''', (channel_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(messages)


@app.route('/api/messages/<int:channel_id>', methods=['POST'])
def post_message(channel_id):
    """Post a new message to a channel"""
    if 'authenticated' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    username = data.get('username', 'Anonymous').strip()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    if not username:
        username = 'Anonymous'

    # Store username in session for admin checks
    session['username'] = username

    conn = get_db()
    cursor = conn.cursor()

    # Verify channel exists
    cursor.execute('SELECT id FROM channels WHERE id = ?', (channel_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Channel not found'}), 404

    cursor.execute('''
        INSERT INTO messages (channel_id, username, message)
        VALUES (?, ?, ?)
    ''', (channel_id, username, message))
    conn.commit()

    # Get the new message
    cursor.execute('''
        SELECT id, username, message, timestamp
        FROM messages
        WHERE id = ?
    ''', (cursor.lastrowid,))
    new_message = dict(cursor.fetchone())
    conn.close()

    return jsonify(new_message), 201


@app.route('/api/admin/set-pin', methods=['POST'])
def set_pin():
    """Set a new PIN (admin only or first-time setup)"""
    data = request.get_json()
    new_pin = data.get('pin', '').strip()
    username = data.get('username', '').strip()

    if not new_pin or len(new_pin) != 6 or not new_pin.isdigit():
        return jsonify({'error': 'PIN must be 6 digits'}), 400

    # Check if any admins exist
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM admins')
    admin_count = cursor.fetchone()[0]

    # If no admins exist, this is first-time setup
    if admin_count == 0:
        if not username:
            conn.close()
            return jsonify({'error': 'Username required for initial setup'}), 400

        # Create first admin
        cursor.execute('INSERT INTO admins (username) VALUES (?)', (username,))
        conn.commit()

        # Set the PIN
        cursor.execute("UPDATE auth SET active = 0")
        cursor.execute("INSERT INTO auth (pin, active) VALUES (?, 1)", (new_pin,))
        conn.commit()
        conn.close()

        session['authenticated'] = True
        session['username'] = username
        return jsonify({'success': True, 'message': 'Initial setup complete'}), 200

    # Otherwise, require admin authentication
    if 'authenticated' not in session:
        conn.close()
        return jsonify({'error': 'Authentication required'}), 401

    session_username = session.get('username', '')
    if not is_admin(session_username):
        conn.close()
        return jsonify({'error': 'Admin privileges required'}), 403

    # Update PIN
    cursor.execute("UPDATE auth SET active = 0")
    cursor.execute("INSERT INTO auth (pin, active) VALUES (?, 1)", (new_pin,))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'PIN updated'}), 200


@app.route('/api/admin/add-admin', methods=['POST'])
def add_admin():
    """Add a new admin user (admin only)"""
    if 'authenticated' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    session_username = session.get('username', '')
    if not is_admin(session_username):
        return jsonify({'error': 'Admin privileges required'}), 403

    data = request.get_json()
    new_admin = data.get('username', '').strip()

    if not new_admin:
        return jsonify({'error': 'Username required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO admins (username) VALUES (?)', (new_admin,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'{new_admin} added as admin'}), 200
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Admin already exists'}), 400


@app.route('/api/admin/check', methods=['GET'])
def check_admin():
    """Check if current user is admin"""
    if 'authenticated' not in session:
        return jsonify({'is_admin': False, 'username': None})

    username = session.get('username', '')
    return jsonify({
        'is_admin': is_admin(username),
        'username': username
    })


@app.route('/setup')
def setup_page():
    """Initial setup page if no admins exist"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM admins')
    admin_count = cursor.fetchone()[0]
    conn.close()

    if admin_count > 0:
        return redirect(url_for('login'))

    return render_template('setup.html')


if __name__ == '__main__':
    # Initialize database
    init_db()

    # Check if setup is needed
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM admins')
    admin_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM auth WHERE active = 1')
    pin_count = cursor.fetchone()[0]
    conn.close()

    print("\n" + "=" * 50)
    print("🚀 RPi Local Chat Server Starting...")
    print("=" * 50)

    if admin_count == 0 or pin_count == 0:
        print("\n  ⚠️  FIRST TIME SETUP REQUIRED")
        print("  Visit: http://<your-rpi-ip>:5000/setup")
        print("  Or local: http://localhost:5000/setup")
    else:
        print("\n  Access the chat at: http://<your-rpi-ip>:5000")
        print("  Local: http://localhost:5000")

    print("\n" + "=" * 50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
