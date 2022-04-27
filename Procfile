release: python manage.py makemigrations --no-input && python manage.py migirate --no-input
web: gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker dtb.asgi:application
worker: celery -A dtb worker --loglevel=INFO
beat: celery -A dtb beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
