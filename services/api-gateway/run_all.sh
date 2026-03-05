#!/bin/sh

# Start the health check in the background
python3 health_check.py &

# Start the API Gateway
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 60 server:app

