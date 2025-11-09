"""
Database initialization for RPi Local Chat Server
Creates SQLite database with messages, channels, auth, and admin tables
"""

import sqlite3
import os

DB_PATH = 'chat.db'


def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Channels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Messages table (with channel support)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (id)
        )
    ''')

    # Auth table for PIN storage
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
