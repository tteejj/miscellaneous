"""
Flask server for RPi Local Chat Server
Multi-channel chat with user authentication, image uploads, and link previews
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory, Response, stream_with_context
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import re
import json
import secrets
import time
import mimetypes
import base64
from io import BytesIO
from collections import defaultdict
from datetime import datetime, timedelta
from PIL import Image
from database import DB_PATH, init_db
import markdown
import bleach
import queue
import threading

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuration
UPLOAD_FOLDER = 'uploads'
THUMBNAIL_FOLDER = 'uploads/thumbnails'
FILES_FOLDER = 'uploads/files'
AVATARS_FOLDER = 'uploads/avatars'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_FILE_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'mp3', 'mp4', 'wav'}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB for other files
THUMBNAIL_SIZE = (800, 800)  # Max dimensions for thumbnails
IMAGE_LOAD_LIMIT = 100 * 1024 * 1024  # 100MB
RATE_LIMIT_MESSAGES = 30  # Max messages per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Create upload directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)
os.makedirs(FILES_FOLDER, exist_ok=True)
os.makedirs(AVATARS_FOLDER, exist_ok=True)

# SSE message queues for each user
message_queues = {}
queue_lock = threading.Lock()

# In-memory caches for reducing SD card writes (critical for Pi Zero)
presence_cache = {}  # {(user_id, channel_id): timestamp}
rate_limit_cache = defaultdict(list)  # {(user_id, action): [timestamps]}
cache_lock = threading.Lock()

# Background thread to persist presence cache every 5 minutes
def persist_presence_cache():
    """Periodically persist presence cache to database"""
    while True:
        time.sleep(300)  # 5 minutes
        try:
            with cache_lock:
                if not presence_cache:
                    continue

                conn = get_db()
                cursor = conn.cursor()
                for (user_id, channel_id), timestamp in presence_cache.items():
                    cursor.execute(
                        "INSERT OR REPLACE INTO user_presence (user_id, channel_id, last_seen) VALUES (?, ?, ?)",
                        (user_id, channel_id, datetime.fromtimestamp(timestamp))
                    )
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error persisting presence cache: {e}")

# Start background persistence thread
persistence_thread = threading.Thread(target=persist_presence_cache, daemon=True)
persistence_thread.start()


def get_db():
    """Get database connection with optimizations"""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency (should already be set, but ensure it)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
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


def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    else:
        return ext in ALLOWED_FILE_EXTENSIONS


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


def check_rate_limit(user_id, action='message'):
    """Check if user has exceeded rate limit (in-memory for Pi Zero optimization)"""
    now = time.time()
    cache_key = (user_id, action)

    with cache_lock:
        # Clean up old entries
        rate_limit_cache[cache_key] = [
            ts for ts in rate_limit_cache[cache_key]
            if now - ts < RATE_LIMIT_WINDOW
        ]

        # Check count
        return len(rate_limit_cache[cache_key]) < RATE_LIMIT_MESSAGES


def record_rate_limit(user_id, action='message'):
    """Record a rate-limited action (in-memory for Pi Zero optimization)"""
    cache_key = (user_id, action)
    with cache_lock:
        rate_limit_cache[cache_key].append(time.time())


def update_user_presence(user_id, channel_id):
    """Update user's last seen timestamp (in-memory for Pi Zero optimization)"""
    with cache_lock:
        presence_cache[(user_id, channel_id)] = time.time()


def get_active_users(channel_id, minutes=5):
    """Get users active in the last N minutes (checks in-memory cache first)"""
    cutoff_timestamp = time.time() - (minutes * 60)
    active_user_ids = set()

    # Check in-memory cache first
    with cache_lock:
        for (user_id, ch_id), timestamp in presence_cache.items():
            if ch_id == channel_id and timestamp > cutoff_timestamp:
                active_user_ids.add(user_id)

    # Get user details from database
    if not active_user_ids:
        return []

    conn = get_db()
    cursor = conn.cursor()
    placeholders = ','.join('?' * len(active_user_ids))
    cursor.execute(f'''
        SELECT id, username FROM users WHERE id IN ({placeholders})
    ''', tuple(active_user_ids))
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def parse_markdown(text):
    """Parse markdown and sanitize HTML"""
    # Convert markdown to HTML
    html = markdown.markdown(text, extensions=['fenced_code', 'nl2br', 'sane_lists'])

    # Sanitize HTML to prevent XSS
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'code', 'pre',
        'a', 'ul', 'ol', 'li', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    ]
    allowed_attrs = {'a': ['href', 'title'], 'code': ['class']}

    clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    # Make links open in new tab and add nofollow
    clean_html = clean_html.replace('<a ', '<a target="_blank" rel="nofollow noopener" ')

    return clean_html


def optimize_image(filepath, max_size_mb=2):
    """Optimize image file size while maintaining reasonable quality"""
    try:
        with Image.open(filepath) as img:
            # Convert RGBA to RGB if needed (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Get file size
            file_size = os.path.getsize(filepath)
            max_bytes = max_size_mb * 1024 * 1024

            # If already under limit, just optimize quality
            if file_size < max_bytes:
                img.save(filepath, quality=85, optimize=True)
                return

            # Calculate resize ratio needed
            ratio = (max_bytes / file_size) ** 0.5
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)

            # Resize and save
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img.save(filepath, quality=80, optimize=True)

    except Exception as e:
        print(f"Image optimization failed: {e}")


def generate_micro_thumbnail(filepath, size=(20, 20)):
    """Generate a tiny base64-encoded thumbnail for lazy loading placeholders"""
    try:
        with Image.open(filepath) as img:
            # Create tiny thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Save to bytes buffer
            buffer = BytesIO()
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            img.save(buffer, 'JPEG', quality=50, optimize=True)

            # Encode as base64 data URL
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/jpeg;base64,{img_str}"

    except Exception as e:
        print(f"Micro thumbnail generation error: {str(e)}")
        return None


def broadcast_message(channel_id, message_data):
    """Broadcast message to all connected clients via SSE"""
    with queue_lock:
        for user_queue in message_queues.values():
            try:
                user_queue.put({
                    'type': 'message',
                    'channel_id': channel_id,
                    'data': message_data
                })
            except:
                pass


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
    """Initial setup page - accessible from anywhere if no users exist"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()

    # If users exist, redirect to login
    if user_count > 0:
        return redirect(url_for('login'))

    # If no users exist, allow setup from anywhere (first-time setup)
    return render_template('setup.html')


@app.route('/admin')
def admin_panel():
    """Admin management interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if not is_admin(session['user_id']):
        return "Access denied. Admin only.", 403

    return render_template('admin.html')


@app.route('/profile')
def profile_page():
    """User profile settings page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('profile.html')


@app.route('/remote')
def remote_control():
    """Samsung TV Remote Control interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('remote.html')


@app.route('/api/remote/command', methods=['POST'])
def remote_command():
    """Handle TV remote commands"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    command = data.get('command')

    if not command:
        return jsonify({'error': 'No command provided'}), 400

    # Log the command (in real implementation, this would send to TV via IR/network)
    user_info = get_user_info(session['user_id'])
    app.logger.info(f"TV Remote command from {user_info['username']}: {command}")

    # TODO: Implement actual TV control via Samsung SmartThings API or IR blaster
    # For now, just acknowledge the command
    return jsonify({'status': 'success', 'command': command}), 200


@app.route('/gallery/<int:channel_id>')
def gallery():
    """Photo gallery view"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('gallery.html')


@app.route('/api/stream/<int:channel_id>')
def message_stream(channel_id):
    """Server-Sent Events stream for real-time updates"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    def event_generator():
        # Create a queue for this user
        user_queue = queue.Queue(maxsize=50)
        user_id = session.get('user_id')

        with queue_lock:
            message_queues[user_id] = user_queue

        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"

            while True:
                try:
                    # Wait for messages with timeout to send heartbeat
                    msg = user_queue.get(timeout=30)

                    # Only send messages for the current channel
                    if msg.get('channel_id') == channel_id or msg.get('type') in ['reaction', 'edit', 'pin', 'presence']:
                        yield f"data: {json.dumps(msg)}\n\n"
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield f": heartbeat\n\n"

        except GeneratorExit:
            # Client disconnected
            with queue_lock:
                if user_id in message_queues:
                    del message_queues[user_id]

    return Response(stream_with_context(event_generator()),
                   mimetype='text/event-stream',
                   headers={
                       'Cache-Control': 'no-cache',
                       'X-Accel-Buffering': 'no',
                       'Connection': 'keep-alive'
                   })


# API Endpoints

@app.route('/api/setup', methods=['POST'])
def initial_setup():
    """Create first admin user - accessible from anywhere if no users exist"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Check if any users exist
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'Setup already completed'}), 400

        # Create first user
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        user_id = cursor.lastrowid

        # Make them admin (handle case where admin entry already exists)
        try:
            cursor.execute('INSERT INTO admins (username) VALUES (?)', (username,))
        except sqlite3.IntegrityError:
            # Admin already exists, that's fine
            pass

        conn.commit()

        # Log them in
        session['user_id'] = user_id
        session['username'] = username

        return jsonify({'success': True, 'message': 'Setup complete'}), 200

    except sqlite3.IntegrityError as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f'Database error: User may already exist'}), 400

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f'Setup failed: {str(e)}'}), 500

    finally:
        if conn:
            conn.close()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration"""
    try:
        # Quick database check
        conn = get_db()
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


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
    """Get all channels with unread counts"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, display_name, description FROM channels ORDER BY id ASC')
    channels = [dict(row) for row in cursor.fetchall()]

    # Get unread counts for each channel
    for channel in channels:
        # Get last read message ID
        cursor.execute('''
            SELECT last_read_message_id FROM unread_tracking
            WHERE user_id = ? AND channel_id = ?
        ''', (user_id, channel['id']))
        result = cursor.fetchone()
        last_read_id = result['last_read_message_id'] if result else 0

        # Count messages after last read
        cursor.execute('''
            SELECT COUNT(*) as unread_count FROM messages
            WHERE channel_id = ? AND id > ?
        ''', (channel['id'], last_read_id))
        channel['unread_count'] = cursor.fetchone()['unread_count']

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
    """Get messages for a specific channel with pagination support"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']

    # Pagination parameters
    before_id = request.args.get('before', type=int)  # Message ID to load before
    limit = request.args.get('limit', 50, type=int)  # Number of messages to load
    limit = min(limit, 100)  # Cap at 100 messages per request

    # Update user presence
    update_user_presence(user_id, channel_id)

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

    # Build query with optional pagination
    query = '''
        SELECT m.id, m.message_type, m.content, m.metadata, m.reply_to_id, m.timestamp, m.user_id,
               u.username, u.avatar_color, u.avatar_url,
               CASE WHEN me.message_id IS NOT NULL THEN 1 ELSE 0 END as edited,
               CASE WHEN pm.message_id IS NOT NULL THEN 1 ELSE 0 END as pinned
        FROM messages m
        JOIN users u ON m.user_id = u.id
        LEFT JOIN (SELECT DISTINCT message_id FROM message_edits) me ON m.id = me.message_id
        LEFT JOIN pinned_messages pm ON m.id = pm.message_id
        WHERE m.channel_id = ?
    '''

    params = [channel_id]

    if before_id:
        query += ' AND m.id < ?'
        params.append(before_id)

    query += ' ORDER BY m.timestamp DESC, m.id DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)

    messages = []
    message_ids = []
    reply_to_ids = set()

    for row in cursor.fetchall():
        msg = dict(row)
        message_ids.append(msg['id'])

        if msg['reply_to_id']:
            reply_to_ids.add(msg['reply_to_id'])

        # Parse metadata if exists
        if msg['metadata']:
            try:
                msg['metadata'] = json.loads(msg['metadata'])
            except:
                msg['metadata'] = None

        # Get reactions for this message
        cursor.execute('''
            SELECT r.emoji, u.username, r.user_id
            FROM reactions r
            JOIN users u ON r.user_id = u.id
            WHERE r.message_id = ?
        ''', (msg['id'],))
        reactions = {}
        for react_row in cursor.fetchall():
            emoji = react_row['emoji']
            if emoji not in reactions:
                reactions[emoji] = []
            reactions[emoji].append({
                'username': react_row['username'],
                'user_id': react_row['user_id']
            })
        msg['reactions'] = reactions

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

        # If it's a file, get file details
        elif msg['message_type'] == 'file':
            file_id = int(msg['content'])
            cursor.execute('''
                SELECT filename, original_filename, file_size, mime_type
                FROM files WHERE id = ?
            ''', (file_id,))
            file_data = cursor.fetchone()
            if file_data:
                msg['file'] = dict(file_data)

        messages.append(msg)

    # Reverse messages to get chronological order (oldest first)
    messages.reverse()

    # Get reply context for threaded messages
    reply_context = {}
    if reply_to_ids:
        placeholders = ','.join('?' * len(reply_to_ids))
        cursor.execute(f'''
            SELECT m.id, m.content, u.username, m.message_type
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.id IN ({placeholders})
        ''', tuple(reply_to_ids))
        for row in cursor.fetchall():
            reply_context[row['id']] = {
                'content': row['content'][:100],  # First 100 chars
                'username': row['username'],
                'message_type': row['message_type']
            }

    # Add reply context to messages
    for msg in messages:
        if msg['reply_to_id'] and msg['reply_to_id'] in reply_context:
            msg['reply_to'] = reply_context[msg['reply_to_id']]

    # Get active users
    active_users = get_active_users(channel_id)

    # Check if there are more messages
    has_more = len(messages) == limit

    # Get pinned messages
    cursor.execute('''
        SELECT message_id FROM pinned_messages
        WHERE channel_id = ?
    ''', (channel_id,))
    pinned_ids = [row['message_id'] for row in cursor.fetchall()]

    # Mark channel as read (update to last message ID)
    if messages:
        last_message_id = messages[-1]['id']
        cursor.execute('''
            INSERT OR REPLACE INTO unread_tracking (user_id, channel_id, last_read_message_id)
            VALUES (?, ?, ?)
        ''', (user_id, channel_id, last_message_id))
        conn.commit()

    conn.close()
    return jsonify({
        'messages': messages,
        'total_image_size': total_size,
        'active_users': active_users,
        'pinned_messages': pinned_ids,
        'has_more': has_more,
        'oldest_id': messages[0]['id'] if messages else None
    })


@app.route('/api/messages/<int:channel_id>', methods=['POST'])
def post_message(channel_id):
    """Post a new message to a channel"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    # Check rate limit
    user_id = session['user_id']
    if not check_rate_limit(user_id, 'message'):
        return jsonify({'error': 'Rate limit exceeded. Please slow down.'}), 429

    data = request.get_json()
    content = data.get('message', '').strip()
    reply_to_id = data.get('reply_to_id')  # Optional: for threading
    use_markdown = data.get('markdown', True)  # Enable markdown by default

    if not content:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Record rate limit
    record_rate_limit(user_id, 'message')

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
        INSERT INTO messages (channel_id, user_id, message_type, content, metadata, reply_to_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (channel_id, user_id, message_type, content, metadata, reply_to_id))
    conn.commit()
    message_id = cursor.lastrowid

    # Add to full-text search index
    if message_type == 'text':
        cursor.execute('''
            INSERT INTO messages_fts (rowid, content) VALUES (?, ?)
        ''', (message_id, content))
        conn.commit()

    # Get the new message with user info
    cursor.execute('''
        SELECT m.id, m.message_type, m.content, m.metadata, m.reply_to_id, m.timestamp, m.user_id,
               u.username, u.avatar_color, u.avatar_url
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

    new_message['reactions'] = {}
    new_message['edited'] = 0
    new_message['pinned'] = 0

    # Parse markdown if it's a text message and detect @mentions
    mentioned_users = []
    if message_type == 'text':
        # Detect @mentions
        mention_pattern = r'@(\w+)'
        matches = re.findall(mention_pattern, content)
        if matches:
            # Get user IDs for mentioned usernames
            placeholders = ','.join('?' * len(matches))
            query = 'SELECT id, username FROM users WHERE username IN ({})'.format(placeholders)
            cursor.execute(query, matches)
            mentioned_users = [dict(row) for row in cursor.fetchall()]

        if use_markdown:
            new_message['content_html'] = parse_markdown(content)
            # Highlight mentions in HTML
            for mentioned in mentioned_users:
                new_message['content_html'] = new_message['content_html'].replace(
                    f'@{mentioned["username"]}',
                    f'<span class="mention">@{mentioned["username"]}</span>'
                )

    conn.close()

    # Broadcast via SSE
    broadcast_message(channel_id, new_message)

    # Send mention notifications to mentioned users
    if mentioned_users:
        sender_username = new_message['username']
        with queue_lock:
            for user_queue in message_queues.values():
                try:
                    user_queue.put({
                        'type': 'mention',
                        'message_id': message_id,
                        'channel_id': channel_id,
                        'sender': sender_username,
                        'mentioned_users': [u['username'] for u in mentioned_users]
                    })
                except:
                    pass

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

    # Optimize the original image
    optimize_image(filepath, max_size_mb=2)

    # Create thumbnail and micro thumbnail
    try:
        with Image.open(filepath) as img:
            # Get original dimensions
            width, height = img.size

            # Create thumbnail
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, quality=85, optimize=True)

        # Generate micro thumbnail (for lazy loading)
        micro_thumb = generate_micro_thumbnail(filepath)

    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Image processing failed: {str(e)}'}), 500

    # Save to database
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO images (channel_id, user_id, filename, thumbnail_filename, micro_thumbnail, file_size, width, height)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (channel_id, user_id, filename, thumbnail_filename, micro_thumb, file_size, width, height))
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


@app.route('/api/profile/avatar', methods=['POST'])
def upload_avatar():
    """Upload user avatar"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use PNG, JPG, or GIF'}), 400

    # Check file size (max 5MB for avatars)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > 5 * 1024 * 1024:
        return jsonify({'error': 'Avatar too large (max 5MB)'}), 400

    user_id = session['user_id']

    # Delete old avatar if exists
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT avatar_url FROM users WHERE id = ?', (user_id,))
    old_avatar = cursor.fetchone()
    if old_avatar and old_avatar['avatar_url']:
        old_path = os.path.join(AVATARS_FOLDER, old_avatar['avatar_url'])
        if os.path.exists(old_path):
            os.remove(old_path)

    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = secrets.token_hex(4)
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"avatar_{user_id}_{timestamp}_{random_str}.{ext}"
    filepath = os.path.join(AVATARS_FOLDER, filename)

    # Save and process avatar
    file.save(filepath)

    try:
        with Image.open(filepath) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize to 200x200 square avatar
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)

            # Create a square image
            width, height = img.size
            if width != height:
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                img = img.resize((200, 200), Image.Resampling.LANCZOS)

            # Save optimized avatar
            img.save(filepath, quality=90, optimize=True)
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Avatar processing failed: {str(e)}'}), 500

    # Update database
    cursor.execute('UPDATE users SET avatar_url = ? WHERE id = ?', (filename, user_id))
    conn.commit()
    conn.close()

    return jsonify({'avatar_url': f'/uploads/avatars/{filename}'}), 200


@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get current user's profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, avatar_url, avatar_color FROM users WHERE id = ?', (session['user_id'],))
    user = dict(cursor.fetchone())
    conn.close()

    return jsonify(user), 200


@app.route('/uploads/avatars/<filename>')
def serve_avatar(filename):
    """Serve avatar files"""
    return send_from_directory(AVATARS_FOLDER, filename)


@app.route('/api/messages/<int:message_id>/react', methods=['POST'])
def add_reaction(message_id):
    """Add a reaction to a message"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    emoji = data.get('emoji', '').strip()

    if not emoji:
        return jsonify({'error': 'Emoji required'}), 400

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # Get message info
    cursor.execute('SELECT channel_id FROM messages WHERE id = ?', (message_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({'error': 'Message not found'}), 404

    channel_id = result['channel_id']

    try:
        cursor.execute('''
            INSERT INTO reactions (message_id, user_id, emoji)
            VALUES (?, ?, ?)
        ''', (message_id, user_id, emoji))
        conn.commit()
    except sqlite3.IntegrityError:
        # Already reacted with this emoji
        conn.close()
        return jsonify({'error': 'Already reacted'}), 400

    # Get username
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    username = cursor.fetchone()['username']

    conn.close()

    # Broadcast reaction via SSE
    with queue_lock:
        for user_queue in message_queues.values():
            try:
                user_queue.put({
                    'type': 'reaction',
                    'action': 'add',
                    'message_id': message_id,
                    'emoji': emoji,
                    'username': username,
                    'user_id': user_id
                })
            except:
                pass

    return jsonify({'success': True})


@app.route('/api/messages/<int:message_id>/react', methods=['DELETE'])
def remove_reaction(message_id):
    """Remove a reaction from a message"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    emoji = data.get('emoji', '').strip()

    if not emoji:
        return jsonify({'error': 'Emoji required'}), 400

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM reactions
        WHERE message_id = ? AND user_id = ? AND emoji = ?
    ''', (message_id, user_id, emoji))
    conn.commit()
    conn.close()

    # Broadcast reaction removal via SSE
    with queue_lock:
        for user_queue in message_queues.values():
            try:
                user_queue.put({
                    'type': 'reaction',
                    'action': 'remove',
                    'message_id': message_id,
                    'emoji': emoji,
                    'user_id': user_id
                })
            except:
                pass

    return jsonify({'success': True})


@app.route('/api/messages/<int:message_id>/edit', methods=['PUT'])
def edit_message(message_id):
    """Edit a message"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    new_content = data.get('content', '').strip()

    if not new_content:
        return jsonify({'error': 'Content cannot be empty'}), 400

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # Get current message
    cursor.execute('''
        SELECT content, user_id, channel_id, message_type
        FROM messages WHERE id = ?
    ''', (message_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({'error': 'Message not found'}), 404

    old_content = result['content']
    msg_user_id = result['user_id']
    channel_id = result['channel_id']
    message_type = result['message_type']

    # Only allow editing own messages
    if msg_user_id != user_id:
        conn.close()
        return jsonify({'error': 'Cannot edit other users messages'}), 403

    # Only allow editing text messages
    if message_type != 'text':
        conn.close()
        return jsonify({'error': 'Can only edit text messages'}), 400

    # Save edit history
    cursor.execute('''
        INSERT INTO message_edits (message_id, old_content)
        VALUES (?, ?)
    ''', (message_id, old_content))

    # Update message
    cursor.execute('''
        UPDATE messages SET content = ?
        WHERE id = ?
    ''', (new_content, message_id))

    # Update FTS index
    cursor.execute('''
        UPDATE messages_fts SET content = ?
        WHERE rowid = ?
    ''', (new_content, message_id))

    conn.commit()
    conn.close()

    # Broadcast edit via SSE
    with queue_lock:
        for user_queue in message_queues.values():
            try:
                user_queue.put({
                    'type': 'edit',
                    'message_id': message_id,
                    'content': new_content,
                    'content_html': parse_markdown(new_content),
                    'channel_id': channel_id
                })
            except:
                pass

    return jsonify({'success': True, 'content': new_content, 'content_html': parse_markdown(new_content)})


@app.route('/api/messages/<int:message_id>/pin', methods=['POST'])
def pin_message(message_id):
    """Pin a message (admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if not is_admin(session['user_id']):
        return jsonify({'error': 'Admin privileges required'}), 403

    conn = get_db()
    cursor = conn.cursor()

    # Get message channel
    cursor.execute('SELECT channel_id FROM messages WHERE id = ?', (message_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({'error': 'Message not found'}), 404

    channel_id = result['channel_id']

    try:
        cursor.execute('''
            INSERT INTO pinned_messages (message_id, channel_id, pinned_by)
            VALUES (?, ?, ?)
        ''', (message_id, channel_id, session['user_id']))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Message already pinned'}), 400

    conn.close()

    # Broadcast pin via SSE
    with queue_lock:
        for user_queue in message_queues.values():
            try:
                user_queue.put({
                    'type': 'pin',
                    'action': 'add',
                    'message_id': message_id,
                    'channel_id': channel_id
                })
            except:
                pass

    return jsonify({'success': True})


@app.route('/api/messages/<int:message_id>/pin', methods=['DELETE'])
def unpin_message(message_id):
    """Unpin a message (admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if not is_admin(session['user_id']):
        return jsonify({'error': 'Admin privileges required'}), 403

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT channel_id FROM pinned_messages WHERE message_id = ?', (message_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({'error': 'Message not pinned'}), 404

    channel_id = result['channel_id']

    cursor.execute('DELETE FROM pinned_messages WHERE message_id = ?', (message_id,))
    conn.commit()
    conn.close()

    # Broadcast unpin via SSE
    with queue_lock:
        for user_queue in message_queues.values():
            try:
                user_queue.put({
                    'type': 'pin',
                    'action': 'remove',
                    'message_id': message_id,
                    'channel_id': channel_id
                })
            except:
                pass

    return jsonify({'success': True})


@app.route('/api/search', methods=['GET'])
def search_messages():
    """Search messages using full-text search"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    query = request.args.get('q', '').strip()
    channel_id = request.args.get('channel_id', type=int)

    if not query:
        return jsonify({'error': 'Query required'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Build search query
    search_query = '''
        SELECT m.id, m.channel_id, m.content, m.timestamp, u.username, c.display_name as channel_name
        FROM messages_fts fts
        JOIN messages m ON fts.rowid = m.id
        JOIN users u ON m.user_id = u.id
        JOIN channels c ON m.channel_id = c.id
        WHERE fts MATCH ?
    '''

    params = [query]

    if channel_id:
        search_query += ' AND m.channel_id = ?'
        params.append(channel_id)

    search_query += ' ORDER BY m.timestamp DESC LIMIT 50'

    cursor.execute(search_query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({'results': results})


@app.route('/api/upload-file/<int:channel_id>', methods=['POST'])
def upload_file(channel_id):
    """Upload a file to channel"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename, 'file'):
        return jsonify({'error': 'File type not allowed'}), 400

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large (max {MAX_FILE_SIZE // (1024*1024)}MB)'}), 400

    user_id = session['user_id']
    original_filename = secure_filename(file.filename)

    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = secrets.token_hex(4)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'bin'
    filename = f"{timestamp}_{random_str}.{ext}"

    filepath = os.path.join(FILES_FOLDER, filename)

    # Save file
    file.save(filepath)

    # Get MIME type
    mime_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'

    # Save to database
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO files (channel_id, user_id, filename, original_filename, file_size, mime_type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (channel_id, user_id, filename, original_filename, file_size, mime_type))
    file_id = cursor.lastrowid

    # Create message pointing to this file
    cursor.execute('''
        INSERT INTO messages (channel_id, user_id, message_type, content)
        VALUES (?, ?, 'file', ?)
    ''', (channel_id, user_id, str(file_id)))
    message_id = cursor.lastrowid

    conn.commit()

    # Get the message with user info
    cursor.execute('''
        SELECT m.id, m.message_type, m.content, m.timestamp, m.user_id,
               u.username
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.id = ?
    ''', (message_id,))
    new_message = dict(cursor.fetchone())
    new_message['file'] = {
        'filename': filename,
        'original_filename': original_filename,
        'file_size': file_size,
        'mime_type': mime_type
    }
    new_message['reactions'] = {}
    new_message['edited'] = 0
    new_message['pinned'] = 0

    conn.close()

    # Broadcast via SSE
    broadcast_message(channel_id, new_message)

    return jsonify(new_message), 201


@app.route('/uploads/files/<filename>')
def serve_file(filename):
    """Serve uploaded files"""
    if 'user_id' not in session:
        return "Unauthorized", 401
    return send_from_directory(FILES_FOLDER, filename)


@app.route('/api/presence/<int:channel_id>', methods=['GET'])
def get_presence(channel_id):
    """Get active users in a channel"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    active_users = get_active_users(channel_id)
    return jsonify({'active_users': active_users})


@app.route('/api/presence/<int:channel_id>', methods=['POST'])
def update_presence(channel_id):
    """Update user presence in a channel"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    update_user_presence(session['user_id'], channel_id)
    return jsonify({'success': True})


@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT e.id, e.title, e.description, e.datetime, e.user_id, u.username,
               DATE(e.datetime) as date
        FROM events e
        JOIN users u ON e.user_id = u.id
        ORDER BY e.datetime ASC
    ''')
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({'events': events})


@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a new event"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    event_datetime = data.get('datetime', '').strip()

    if not title or not event_datetime:
        return jsonify({'error': 'Title and datetime required'}), 400

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO events (user_id, title, description, datetime)
        VALUES (?, ?, ?, ?)
    ''', (user_id, title, description, event_datetime))
    conn.commit()
    event_id = cursor.lastrowid

    # Get the created event with user info
    cursor.execute('''
        SELECT e.id, e.title, e.description, e.datetime, e.user_id, u.username,
               DATE(e.datetime) as date
        FROM events e
        JOIN users u ON e.user_id = u.id
        WHERE e.id = ?
    ''', (event_id,))
    event = dict(cursor.fetchone())
    conn.close()

    return jsonify(event), 201


@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # Check if user owns the event or is admin
    cursor.execute('SELECT user_id FROM events WHERE id = ?', (event_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({'error': 'Event not found'}), 404

    if result['user_id'] != user_id and not is_admin(user_id):
        conn.close()
        return jsonify({'error': 'Permission denied'}), 403

    cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/polls/<int:channel_id>', methods=['POST'])
def create_poll(channel_id):
    """Create a poll in a channel"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    question = data.get('question', '').strip()
    options = data.get('options', [])
    expires_at = data.get('expires_at')

    if not question or len(options) < 2:
        return jsonify({'error': 'Question and at least 2 options required'}), 400

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO polls (channel_id, user_id, question, options, expires_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (channel_id, user_id, question, json.dumps(options), expires_at))
    poll_id = cursor.lastrowid
    conn.commit()

    # Broadcast poll creation
    poll_data = get_poll_data(cursor, poll_id, user_id)
    conn.close()

    broadcast_message(channel_id, {
        'type': 'poll',
        'data': poll_data
    })

    return jsonify(poll_data), 201


@app.route('/api/polls/<int:poll_id>/vote', methods=['POST'])
def vote_poll(poll_id):
    """Vote on a poll"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    option_index = data.get('option')

    if option_index is None:
        return jsonify({'error': 'Option required'}), 400

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # Check if poll exists and is not expired
    cursor.execute('SELECT channel_id, expires_at FROM polls WHERE id = ?', (poll_id,))
    poll = cursor.fetchone()
    if not poll:
        conn.close()
        return jsonify({'error': 'Poll not found'}), 404

    if poll['expires_at']:
        expires = datetime.fromisoformat(poll['expires_at'])
        if datetime.now() > expires:
            conn.close()
            return jsonify({'error': 'Poll has expired'}), 400

    # Insert or update vote
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO poll_votes (poll_id, user_id, option_index)
            VALUES (?, ?, ?)
        ''', (poll_id, user_id, option_index))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

    # Get updated poll data
    poll_data = get_poll_data(cursor, poll_id, user_id)
    conn.close()

    # Broadcast poll update
    broadcast_message(poll['channel_id'], {
        'type': 'poll_update',
        'data': poll_data
    })

    return jsonify(poll_data)


def get_poll_data(cursor, poll_id, user_id):
    """Helper function to get poll data with vote counts"""
    cursor.execute('''
        SELECT p.id, p.channel_id, p.question, p.options, p.created_at, p.expires_at,
               u.username
        FROM polls p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    ''', (poll_id,))
    poll = dict(cursor.fetchone())
    poll['options'] = json.loads(poll['options'])

    # Get vote counts
    cursor.execute('''
        SELECT option_index, COUNT(*) as count
        FROM poll_votes
        WHERE poll_id = ?
        GROUP BY option_index
    ''', (poll_id,))
    vote_counts = {row['option_index']: row['count'] for row in cursor.fetchall()}

    # Get total votes
    total_votes = sum(vote_counts.values())

    # Check user's vote
    cursor.execute('''
        SELECT option_index FROM poll_votes
        WHERE poll_id = ? AND user_id = ?
    ''', (poll_id, user_id))
    user_vote = cursor.fetchone()

    poll['vote_counts'] = vote_counts
    poll['total_votes'] = total_votes
    poll['user_vote'] = user_vote['option_index'] if user_vote else None

    return poll


@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # Get message info
    cursor.execute('SELECT user_id, channel_id, message_type, content FROM messages WHERE id = ?', (message_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({'error': 'Message not found'}), 404

    msg_user_id = result['user_id']
    channel_id = result['channel_id']
    message_type = result['message_type']
    content = result['content']

    # Check permission: owner or admin
    if msg_user_id != user_id and not is_admin(user_id):
        conn.close()
        return jsonify({'error': 'Permission denied'}), 403

    # Delete associated data first
    cursor.execute('DELETE FROM reactions WHERE message_id = ?', (message_id,))
    cursor.execute('DELETE FROM pinned_messages WHERE message_id = ?', (message_id,))
    cursor.execute('DELETE FROM message_edits WHERE message_id = ?', (message_id,))
    cursor.execute('DELETE FROM messages_fts WHERE rowid = ?', (message_id,))

    # If it's an image, delete from images table and files
    if message_type == 'image':
        try:
            image_id = int(content)
            cursor.execute('SELECT filename, thumbnail_filename FROM images WHERE id = ?', (image_id,))
            img_data = cursor.fetchone()
            if img_data:
                # Delete files from disk
                import os
                try:
                    if os.path.exists(os.path.join(UPLOAD_FOLDER, img_data['filename'])):
                        os.remove(os.path.join(UPLOAD_FOLDER, img_data['filename']))
                    if os.path.exists(os.path.join(THUMBNAIL_FOLDER, img_data['thumbnail_filename'])):
                        os.remove(os.path.join(THUMBNAIL_FOLDER, img_data['thumbnail_filename']))
                except:
                    pass
                cursor.execute('DELETE FROM images WHERE id = ?', (image_id,))
        except:
            pass

    # If it's a file, delete from files table and disk
    elif message_type == 'file':
        try:
            file_id = int(content)
            cursor.execute('SELECT filename FROM files WHERE id = ?', (file_id,))
            file_data = cursor.fetchone()
            if file_data:
                try:
                    if os.path.exists(os.path.join(FILES_FOLDER, file_data['filename'])):
                        os.remove(os.path.join(FILES_FOLDER, file_data['filename']))
                except:
                    pass
                cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
        except:
            pass

    # Delete the message itself
    cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
    conn.commit()
    conn.close()

    # Broadcast deletion via SSE
    with queue_lock:
        for user_queue in message_queues.values():
            try:
                user_queue.put({
                    'type': 'delete',
                    'message_id': message_id,
                    'channel_id': channel_id
                })
            except:
                pass

    return jsonify({'success': True})


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
