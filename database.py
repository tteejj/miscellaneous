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

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            avatar_color TEXT DEFAULT '#667eea',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    ''')

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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            thumbnail_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            width INTEGER,
            height INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

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

    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_channel_id ON messages(channel_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_channel_id ON images(channel_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_timestamp ON images(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reactions_message_id ON reactions(message_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_channel_id ON files(channel_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_presence_channel_id ON user_presence(channel_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pinned_messages_channel_id ON pinned_messages(channel_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_datetime ON events(datetime)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id)')

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
