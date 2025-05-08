try:
    from celery import Celery
except ImportError:
    class Celery:
        """Stub Celery if not installed."""
        def __init__(self, *args, **kwargs):
            self.conf = self
        def config_from_object(self, obj):
            pass
        def autodiscover_tasks(self, modules):
            pass
        def update(self, **kwargs):
            pass
        def start(self):
            pass

import os
import importlib

# Create the Celery instance
app = Celery('user_management')

# Load configuration from environment variables
app.config_from_object('app.config.celery_config')

# Auto-discover tasks in all app modules
app.autodiscover_tasks(['app.tasks'])

# Optional: Configure Celery to use Redis as the result backend
app.conf.update(
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

if __name__ == '__main__':
    app.start()
