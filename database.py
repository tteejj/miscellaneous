"""
Database initialization for RPi Local Chat Server
Creates SQLite database with users, channels, messages, images, and admin tables
"""

import sqlite3
import os

DB_PATH = 'chat.db'


def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable WAL mode for better concurrent access (critical for Pi Zero)
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA synchronous=NORMAL')  # Faster, safe enough
    cursor.execute('PRAGMA cache_size=-20000')   # 20MB cache in RAM
    cursor.execute('PRAGMA temp_store=MEMORY')   # Keep temp tables in RAM
    cursor.execute('PRAGMA mmap_size=30000000')  # 30MB memory-mapped I/O
    cursor.execute('PRAGMA page_size=4096')      # Optimal for modern systems
    cursor.execute('PRAGMA foreign_keys=ON')     # Enforce foreign key constraints

    print("✓ Enabled WAL mode and performance optimizations")

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            avatar_color TEXT DEFAULT '#667eea',
            avatar_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    ''')

    # Migration: Add avatar_url column if it doesn't exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'avatar_url' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN avatar_url TEXT')
        print("✓ Added avatar_url column to users table")

    # Channels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Messages table (with user_id and message types)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            message_type TEXT DEFAULT 'text',
            content TEXT NOT NULL,
            metadata TEXT,
            reply_to_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (reply_to_id) REFERENCES messages (id) ON DELETE SET NULL
        )
    ''')

    # Migration: Add reply_to_id column if it doesn't exist (for threading)
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'reply_to_id' not in columns:
        cursor.execute('ALTER TABLE messages ADD COLUMN reply_to_id INTEGER REFERENCES messages(id) ON DELETE SET NULL')
        print("✓ Added reply_to_id column to messages table (threading support)")

    # Images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            thumbnail_filename TEXT NOT NULL,
            micro_thumbnail TEXT,
            file_size INTEGER NOT NULL,
            width INTEGER,
            height INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Migration: Add micro_thumbnail column if it doesn't exist (for lazy loading)
    cursor.execute("PRAGMA table_info(images)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'micro_thumbnail' not in columns:
        cursor.execute('ALTER TABLE images ADD COLUMN micro_thumbnail TEXT')
        print("✓ Added micro_thumbnail column to images table (lazy loading)")

    # Auth table for PIN storage (kept for backward compatibility)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    ''')

    # Admin users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Reactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            emoji TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(message_id, user_id, emoji)
        )
    ''')

    # Pinned messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pinned_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL UNIQUE,
            channel_id INTEGER NOT NULL,
            pinned_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE,
            FOREIGN KEY (channel_id) REFERENCES channels (id),
            FOREIGN KEY (pinned_by) REFERENCES users (id)
        )
    ''')

    # User presence table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_presence (
            user_id INTEGER PRIMARY KEY,
            channel_id INTEGER NOT NULL,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (channel_id) REFERENCES channels (id)
        )
    ''')

    # Message edits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            old_content TEXT NOT NULL,
            edited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE
        )
    ''')

    # Rate limiting table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rate_limits (
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, action, timestamp)
        )
    ''')

    # Files table (for non-image uploads)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            mime_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Events table (calendar events)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            datetime DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Unread tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unread_tracking (
            user_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            last_read_message_id INTEGER,
            PRIMARY KEY (user_id, channel_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (channel_id) REFERENCES channels (id),
            FOREIGN KEY (last_read_message_id) REFERENCES messages (id)
        )
    ''')

    # Polls table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            FOREIGN KEY (channel_id) REFERENCES channels (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Poll votes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poll_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            option_index INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(poll_id, user_id),
            FOREIGN KEY (poll_id) REFERENCES polls (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create optimized indexes for performance (composite indexes for common queries)
    # Most important: Message loading by channel (pagination)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_channel_time ON messages(channel_id, timestamp DESC, id DESC)')

    # Threading support
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_reply_to ON messages(reply_to_id)')

    # User messages
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_time ON messages(user_id, timestamp DESC)')

    # Image loading
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_channel_time ON images(channel_id, timestamp DESC)')

    # Reactions
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reactions_message_emoji ON reactions(message_id, emoji)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reactions_user ON reactions(user_id)')

    # Files
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_channel_time ON files(channel_id, timestamp DESC)')

    # Presence (active users in channel)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_presence_channel_active ON user_presence(channel_id, last_seen DESC)')

    # Pinned messages
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pinned_channel ON pinned_messages(channel_id, created_at DESC)')

    # Events
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_datetime ON events(datetime)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user_date ON events(user_id, datetime)')

    # Message edits
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_edits_message ON message_edits(message_id, edited_at DESC)')

    # Rate limits (cleanup old entries)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rate_limits_timestamp ON rate_limits(timestamp)')

    # Polls
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_polls_channel_time ON polls(channel_id, created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_poll_votes_poll ON poll_votes(poll_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_poll_votes_user ON poll_votes(user_id)')

    # Analyze tables for query optimization
    cursor.execute('ANALYZE')

    # Create full-text search virtual table
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
            content,
            content_rowid=id
        )
    ''')

    print("✓ Created database indexes and full-text search")

    # Create default channels if they don't exist
    cursor.execute("SELECT COUNT(*) FROM channels")
    if cursor.fetchone()[0] == 0:
        default_channels = [
            ('general', '#general'),
            ('pictures', '#pictures'),
            ('random', '#random')
        ]
        cursor.executemany(
            "INSERT INTO channels (name, display_name) VALUES (?, ?)",
            default_channels
        )
        print("✓ Created default channels: #general, #pictures, #random")

    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")


if __name__ == "__main__":
    init_db()
