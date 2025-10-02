import os
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

# Load task modules from all registered Django apps.
app.autodiscover_tasks()