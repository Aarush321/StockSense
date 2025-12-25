#!/bin/bash
cd "$(dirname "$0")/backend"
echo "Starting backend server on port 5001..."
python3 app.py

