release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: sh -c "gunicorn university_project.wsgi --bind 0.0.0.0:\${PORT:-8080} --timeout 120 --workers 2 --max-requests 1000 --max-requests-jitter 50"
