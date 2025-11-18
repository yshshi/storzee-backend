from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storzee_backend.settings')

app = Celery('storzee_backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# ---- SIMPLE CRON SETUP HERE ----
app.conf.beat_schedule = {
    'run-every-5-min': {
        'task': 'apps.notification.tasks.sample_task',
        'schedule': crontab(minute="*/1"),
    },
    'send-test-notification-every-5-min': {
        'task': 'apps.notification.tasks.send_test_notification',
        'schedule': crontab(minute="*/5"),
    },
}