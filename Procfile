web: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
worker: cd backend && celery -A app.celery worker --loglevel=info 