"""
Flask server for RPi Local Chat Server
Provides web interface for local network chat
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from datetime import datetime
from database import DB_PATH, init_db
from auth import verify_pin
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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


@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all messages"""
    if 'authenticated' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, message, timestamp
        FROM messages
        ORDER BY timestamp ASC
    ''')
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(messages)


@app.route('/api/messages', methods=['POST'])
def post_message():
    """Post a new message"""
    if 'authenticated' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    username = data.get('username', 'Anonymous').strip()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    if not username:
        username = 'Anonymous'

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (username, message)
        VALUES (?, ?)
    ''', (username, message))
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


if __name__ == '__main__':
    # Initialize database
    init_db()

    print("\n" + "=" * 50)
    print("🚀 RPi Local Chat Server Starting...")
    print("=" * 50)
    print("\n  Access the chat at: http://<your-rpi-ip>:5000")
    print("  Local: http://localhost:5000\n")
    print("=" * 50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
