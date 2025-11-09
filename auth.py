"""
PIN-based authentication system for RPi Local Chat Server
Generates and verifies 6-digit PINs
"""

import sqlite3
import secrets
from database import DB_PATH, init_db


def generate_pin():
    """Generate a random 6-digit PIN"""
    return str(secrets.randbelow(999999)).zfill(6)


def store_pin(pin):
    """Store a new PIN in the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Deactivate all previous PINs
    cursor.execute("UPDATE auth SET active = 0")

    # Insert new active PIN
    cursor.execute("INSERT INTO auth (pin, active) VALUES (?, 1)", (pin,))

    conn.commit()
    conn.close()


def verify_pin(pin):
    """Verify if the provided PIN is valid and active"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM auth WHERE pin = ? AND active = 1", (pin,))
    result = cursor.fetchone()

    conn.close()
    return result is not None


def create_new_pin():
    """Create and store a new PIN, returning it"""
    pin = generate_pin()
    store_pin(pin)
    return pin


if __name__ == "__main__":
    # Initialize database if needed
    init_db()

    # Generate a new PIN for testing
    new_pin = create_new_pin()
    print(f"New PIN: {new_pin}")

    # Verify it works
    print(f"Verification: {verify_pin(new_pin)}")
