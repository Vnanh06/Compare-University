#!/bin/bash
set -e

# Default PORT to 8080 if not set
export PORT="${PORT:-8080}"

echo "=========================================="
echo "  Starting University Comparison App"
echo "=========================================="
echo "Port: $PORT"
echo "Workers: 1 (gthread with 4 threads)"
echo "Timeout: 120s"
echo "=========================================="
echo ""

# Create database tables (if not exist)
echo "Creating database tables..."
python manage.py create_tables || echo "Tables already exist, continuing..."

# Load initial data (if database is empty)
echo "Loading initial data..."

python manage.py loaddata /app/database_export.json || echo "Data already loaded or file not found, continuing..."

# Run migrations (safe to run multiple times)
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migrations failed, but continuing..."

# Note: ChromaDB will be built lazily on first chatbot query to avoid OOM during startup

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
