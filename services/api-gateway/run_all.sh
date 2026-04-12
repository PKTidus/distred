#!/bin/sh

# Start the health check in the background
python3 health_check.py &

gunicorn "server:app" \
  --workers 4 \
  --worker-class gthread \
  --threads 2 \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
