#!/bin/bash
set -e

# Default PORT to 8080 if not set
export PORT="${PORT:-8080}"

echo "=========================================="
echo "  Starting University Comparison App"
echo "=========================================="
echo "Port: $PORT"
echo "Workers: 2"
echo "Timeout: 120s"
echo "=========================================="
echo ""

# Run migrations (safe to run multiple times)
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migrations failed, but continuing..."

# Collect static files (if not done in build)
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static collection failed, but continuing..."

# Start Gunicorn
echo "Starting Gunicorn on 0.0.0.0:$PORT..."
exec gunicorn university_project.wsgi \
    --bind "0.0.0.0:$PORT" \
    --timeout 120 \
    --workers 1 \
    --threads 4 \
    --worker-class gthread \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --log-level info
