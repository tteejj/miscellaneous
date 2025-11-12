#!/bin/bash
echo "========================================="
echo "  TV Remote Test Server"
echo "========================================="
echo ""
echo "Starting Flask server..."
echo "Open browser to: http://localhost:5555"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
python3 test_server.py
