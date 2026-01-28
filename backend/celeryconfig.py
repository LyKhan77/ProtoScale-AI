"""Celery configuration for CLI usage."""
from app.tasks import celery_app

# This file allows running celery with:
# celery -A celeryconfig worker --loglevel=info
