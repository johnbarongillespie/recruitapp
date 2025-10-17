import os
import sys
from celery import Celery
from dotenv import load_dotenv

# Ensure the .env file is loaded for the standalone celery command
load_dotenv()

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitapp_core.settings')

app = Celery('recruitapp_core')

# Configure Celery directly using the environment variable.
# This is more robust than the 'config_from_object' method for this setup.
app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
app.conf.result_backend = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.timezone = 'UTC'

# Periodic task schedule to keep worker connections alive
app.conf.beat_schedule = {
    'db-keepalive-every-5-minutes': {
        'task': 'recruiting.tasks.db_keepalive',
        'schedule': 300.0,  # Run every 5 minutes (300 seconds)
    },
}

# Windows-specific configuration: Use solo pool (works without gevent dependency issues)
# For production with concurrency, deploy to Linux or resolve gevent venv installation
if sys.platform == 'win32':
    app.conf.worker_pool = 'solo'  # Single-threaded, works reliably on Windows

    # To enable gevent (requires proper venv installation):
    # pip install --no-user gevent
    # Then uncomment:
    # app.conf.worker_pool = 'gevent'
    # app.conf.worker_concurrency = 10

# Load task modules from all registered Django apps.
app.autodiscover_tasks()