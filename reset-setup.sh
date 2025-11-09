#!/bin/bash
# Reset the chat database to allow fresh setup

echo "⚠️  Resetting RPi Chat Database..."
echo "This will delete all users, messages, and uploaded images."
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Stop the server if it's running
./stop-chat.sh 2>/dev/null

# Remove database
if [ -f "chat.db" ]; then
    rm chat.db
    echo "✓ Removed database"
fi

# Remove uploaded files
if [ -d "uploads" ]; then
    rm -rf uploads
    echo "✓ Removed uploads directory"
fi

# Reinitialize database
python3 database.py

echo ""
echo "✓ Database reset complete!"
echo "You can now run ./start-chat.sh and visit http://localhost:5000/setup"
