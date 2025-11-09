"""
Flask server for RPi Local Chat Server
Multi-channel chat with user authentication, image uploads, and link previews
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import re
import json
import secrets
from datetime import datetime
from PIL import Image
from database import DB_PATH, init_db

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuration
UPLOAD_FOLDER = 'uploads'
THUMBNAIL_FOLDER = 'uploads/thumbnails'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
THUMBNAIL_SIZE = (800, 800)  # Max dimensions for thumbnails
IMAGE_LOAD_LIMIT = 100 * 1024 * 1024  # 100MB

# Create upload directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def is_localhost():
    """Check if request is from localhost"""
    return request.remote_addr in ['127.0.0.1', 'localhost', '::1']


def is_admin(user_id):
    """Check if user is an admin"""
    if not user_id:
        return False
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id FROM admins a
        JOIN users u ON a.username = u.username
        WHERE u.id = ?
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def get_user_info(user_id):
    """Get user information"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_youtube_url(url):
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def detect_message_type(content):
    """Detect message type and extract metadata"""
    # Check for YouTube URL
    youtube_id = parse_youtube_url(content)
    if youtube_id:
        return 'youtube', json.dumps({'video_id': youtube_id, 'url': content})

    # Check for other URLs
    url_pattern = r'https?://[^\s]+'
    if re.search(url_pattern, content):
        return 'link', None

    return 'text', None


@app.route('/')
def index():
    """Main chat interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('login.html', error='Username and password required')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash, active FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user['active'] and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('index'))

        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/setup')
def setup_page():
    """Initial setup page - localhost only"""
    if not is_localhost():
        return "Setup is only accessible from localhost", 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()

    if user_count > 0:
        return redirect(url_for('login'))

    return render_template('setup.html')


@app.route('/admin')
def admin_panel():
    """Admin management interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if not is_admin(session['user_id']):
        return "Access denied. Admin only.", 403

    return render_template('admin.html')


@app.route('/gallery/<int:channel_id>')
def gallery():
    """Photo gallery view"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('gallery.html')


# API Endpoints

@app.route('/api/setup', methods=['POST'])
def initial_setup():
    """Create first admin user - localhost only"""
    if not is_localhost():
        return jsonify({'error': 'Setup only accessible from localhost'}), 403

    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Check if any users exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return jsonify({'error': 'Setup already completed'}), 400

    # Create first user
    password_hash = generate_password_hash(password)
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
    user_id = cursor.lastrowid

    # Make them admin
    cursor.execute('INSERT INTO admins (username) VALUES (?)', (username,))
    conn.commit()
    conn.close()

    # Log them in
    session['user_id'] = user_id
    session['username'] = username

    return jsonify({'success': True, 'message': 'Setup complete'}), 200


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if not is_admin(session['user_id']):
        return jsonify({'error': 'Admin privileges required'}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.created_at, u.active,
               CASE WHEN a.username IS NOT NULL THEN 1 ELSE 0 END as is_admin
        FROM users u
        LEFT JOIN admins a ON u.username = a.username
        ORDER BY u.created_at DESC
    ''')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(users)


@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user (admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if not is_admin(session['user_id']):
        return jsonify({'error': 'Admin privileges required'}), 403

    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    make_admin = data.get('is_admin', False)

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if len(password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        user_id = cursor.lastrowid

        if make_admin:
            cursor.execute('INSERT INTO admins (username) VALUES (?)', (username,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'user': {'id': user_id, 'username': username, 'password': password}
        }), 201

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 400


@app.route('/api/users/<int:user_id>/password', methods=['PUT'])
def change_user_password():
    """Change user password (admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if not is_admin(session['user_id']):
        return jsonify({'error': 'Admin privileges required'}), 403

    data = request.get_json()
    new_password = data.get('password', '').strip()

    if not new_password or len(new_password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400

    conn = get_db()
    cursor = conn.cursor()
    password_hash = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'password': new_password})


@app.route('/api/channels', methods=['GET'])
def get_channels():
    """Get all channels"""
    if 'user_id' not in session:
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
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if not is_admin(session['user_id']):
        return jsonify({'error': 'Admin privileges required'}), 403

    data = request.get_json()
    name = data.get('name', '').strip().lower()
    display_name = data.get('display_name', '').strip()

    if not name or not display_name:
        return jsonify({'error': 'Name and display name required'}), 400

    if not display_name.startswith('#'):
        display_name = '#' + display_name

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO channels (name, display_name) VALUES (?, ?)', (name, display_name))
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
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db()
    cursor = conn.cursor()

    # Get total image size for this channel
    cursor.execute('''
        SELECT COALESCE(SUM(file_size), 0) as total_size
        FROM images
        WHERE channel_id = ?
    ''', (channel_id,))
    total_size = cursor.fetchone()['total_size']

    # Calculate how many images to load (last 100MB)
    cursor.execute('''
        SELECT i.id, i.file_size,
               SUM(i.file_size) OVER (ORDER BY i.timestamp DESC) as running_total
        FROM images i
        WHERE i.channel_id = ?
        ORDER BY i.timestamp DESC
    ''', (channel_id,))

    image_ids_to_load = []
    for row in cursor.fetchall():
        if row['running_total'] <= IMAGE_LOAD_LIMIT:
            image_ids_to_load.append(row['id'])
        else:
            break

    # Get messages with user info
    cursor.execute('''
        SELECT m.id, m.message_type, m.content, m.metadata, m.timestamp,
               u.username
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.channel_id = ?
        ORDER BY m.timestamp ASC
    ''', (channel_id,))

    messages = []
    for row in cursor.fetchall():
        msg = dict(row)

        # Parse metadata if exists
        if msg['metadata']:
            try:
                msg['metadata'] = json.loads(msg['metadata'])
            except:
                msg['metadata'] = None

        # If it's an image, check if it should be loaded
        if msg['message_type'] == 'image':
            img_id = int(msg['content'])  # content stores image ID
            msg['loaded'] = img_id in image_ids_to_load

            if msg['loaded']:
                # Get image details
                cursor.execute('''
                    SELECT filename, thumbnail_filename, width, height
                    FROM images WHERE id = ?
                ''', (img_id,))
                img_data = cursor.fetchone()
                if img_data:
                    msg['image'] = dict(img_data)

        messages.append(msg)

    conn.close()
    return jsonify({'messages': messages, 'total_image_size': total_size})


@app.route('/api/messages/<int:channel_id>', methods=['POST'])
def post_message(channel_id):
    """Post a new message to a channel"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    content = data.get('message', '').strip()

    if not content:
        return jsonify({'error': 'Message cannot be empty'}), 400

    user_id = session['user_id']

    # Detect message type
    message_type, metadata = detect_message_type(content)

    conn = get_db()
    cursor = conn.cursor()

    # Verify channel exists
    cursor.execute('SELECT id FROM channels WHERE id = ?', (channel_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Channel not found'}), 404

    cursor.execute('''
        INSERT INTO messages (channel_id, user_id, message_type, content, metadata)
        VALUES (?, ?, ?, ?, ?)
    ''', (channel_id, user_id, message_type, content, metadata))
    conn.commit()
    message_id = cursor.lastrowid

    # Get the new message with user info
    cursor.execute('''
        SELECT m.id, m.message_type, m.content, m.metadata, m.timestamp,
               u.username
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.id = ?
    ''', (message_id,))
    new_message = dict(cursor.fetchone())

    if new_message['metadata']:
        try:
            new_message['metadata'] = json.loads(new_message['metadata'])
        except:
            new_message['metadata'] = None

    conn.close()
    return jsonify(new_message), 201


@app.route('/api/upload/<int:channel_id>', methods=['POST'])
def upload_image(channel_id):
    """Upload image to channel"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large (max {MAX_FILE_SIZE // (1024*1024)}MB)'}), 400

    user_id = session['user_id']

    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = secrets.token_hex(4)
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{timestamp}_{random_str}.{ext}"
    thumbnail_filename = f"{timestamp}_{random_str}_thumb.{ext}"

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_filename)

    # Save original
    file.save(filepath)

    # Create thumbnail
    try:
        with Image.open(filepath) as img:
            # Get original dimensions
            width, height = img.size

            # Create thumbnail
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, quality=85, optimize=True)

    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Image processing failed: {str(e)}'}), 500

    # Save to database
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO images (channel_id, user_id, filename, thumbnail_filename, file_size, width, height)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (channel_id, user_id, filename, thumbnail_filename, file_size, width, height))
    image_id = cursor.lastrowid

    # Create message pointing to this image
    cursor.execute('''
        INSERT INTO messages (channel_id, user_id, message_type, content)
        VALUES (?, ?, 'image', ?)
    ''', (channel_id, user_id, str(image_id)))
    message_id = cursor.lastrowid

    conn.commit()

    # Get the message with user info
    cursor.execute('''
        SELECT m.id, m.message_type, m.content, m.timestamp,
               u.username
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.id = ?
    ''', (message_id,))
    new_message = dict(cursor.fetchone())
    new_message['loaded'] = True
    new_message['image'] = {
        'filename': filename,
        'thumbnail_filename': thumbnail_filename,
        'width': width,
        'height': height
    }

    conn.close()

    return jsonify(new_message), 201


@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    if 'user_id' not in session:
        return "Unauthorized", 401
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/uploads/thumbnails/<filename>')
def serve_thumbnail(filename):
    """Serve thumbnail files"""
    if 'user_id' not in session:
        return "Unauthorized", 401
    return send_from_directory(THUMBNAIL_FOLDER, filename)


@app.route('/api/images/<int:channel_id>', methods=['GET'])
def get_channel_images(channel_id):
    """Get all images for a channel (for gallery view)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT i.id, i.filename, i.thumbnail_filename, i.width, i.height,
               i.file_size, i.timestamp, u.username
        FROM images i
        JOIN users u ON i.user_id = u.id
        WHERE i.channel_id = ?
        ORDER BY i.timestamp DESC
    ''', (channel_id,))

    images = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(images)


@app.route('/api/admin/check', methods=['GET'])
def check_admin():
    """Check if current user is admin"""
    if 'user_id' not in session:
        return jsonify({'is_admin': False, 'username': None})

    user_info = get_user_info(session['user_id'])
    return jsonify({
        'is_admin': is_admin(session['user_id']),
        'username': user_info['username'] if user_info else None
    })


if __name__ == '__main__':
    # Initialize database
    init_db()

    # Check if setup is needed
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()

    print("\n" + "=" * 50)
    print("🚀 RPi Local Chat Server Starting...")
    print("=" * 50)

    if user_count == 0:
        print("\n  ⚠️  FIRST TIME SETUP REQUIRED")
        print("  Visit from localhost: http://localhost:5000/setup")
        print("  (Setup only accessible from localhost for security)")
    else:
        print("\n  Access the chat at: http://<your-ip>:5000")
        print("  Local: http://localhost:5000")

    print("\n" + "=" * 50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
