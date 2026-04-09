#!/bin/sh

# Start the health check in the background
python3 health_check.py &

# Use Flask's built-in development server with the official reloader
# This is more robust for hot-reloading inside Docker volumes
export FLASK_APP=server.py
export FLASK_DEBUG=1
python3 -m flask run --host=0.0.0.0 --port=8000
