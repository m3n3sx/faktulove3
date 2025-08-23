"""
Celery configuration for FaktuLove OCR processing
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')

app = Celery('faktulove')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'cleanup-old-documents': {
        'task': 'faktury.tasks.cleanup_old_documents',
        'schedule': 60.0 * 60.0 * 24.0,  # Daily at midnight
        'options': {'queue': 'cleanup'}
    },
    'cleanup-failed-documents': {
        'task': 'faktury.tasks.cleanup_failed_documents', 
        'schedule': 60.0 * 60.0 * 6.0,  # Every 6 hours
        'options': {'queue': 'cleanup'}
    },
}

# Configure task routing
app.conf.task_routes = {
    'faktury.tasks.process_ocr_document': {'queue': 'ocr'},
    'faktury.tasks.cleanup_old_documents': {'queue': 'cleanup'},
    'faktury.tasks.cleanup_failed_documents': {'queue': 'cleanup'},
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
