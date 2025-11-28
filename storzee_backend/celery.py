from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storzee_backend.settings')

app = Celery('storzee_backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# ---- SIMPLE CRON SETUP HERE ----
# app.conf.beat_schedule = {
#     # 'run-every-5-min': {
#     #     'task': 'apps.notification.tasks.sample_task',
#     #     'schedule': crontab(minute="*/1"),
#     # },
#     # 'send-test-notification-every-5-min': {
#     #     'task': 'apps.notification.tasks.send_test_notification',
#     #     'schedule': crontab(minute="*/5"),
#     # },
# }
app.conf.beat_schedule = {
    # Match-day related
    'run-morning': {
        'task': 'apps.notification.tasks.send_starting_notification',
        'schedule': crontab(hour=10, minute=0),
    },
    'run-midday': {
        'task': 'apps.notification.tasks.send_midday_notification',
        'schedule': crontab(hour=12, minute=0),
    },
    'run-discount': {
        'task': 'apps.notification.tasks.send_discount_notification',
        'schedule': crontab(hour=12, minute=30),
    },
    'run-during': {
        'task': 'apps.notification.tasks.send_during_notification',
        'schedule': crontab(hour=19, minute=0),
    },
    'run-post': {
        'task': 'apps.notification.tasks.send_post_notification',
        'schedule': crontab(hour=22, minute=0),
    },

    # Booking reminders
    'run-30minsReminder': {
        'task': 'apps.notification.tasks.cron_notify_booking_ending_soon',
        'schedule': crontab(minute="*/15"),
    },
    'run-postTimeReminder': {
        'task': 'apps.notification.tasks.cron_notify_late_pickup',
        'schedule': crontab(minute="*/20"),
    },
    'run-cancelbooking': {
        'task': 'apps.notification.tasks.cron_auto_cancel_unstored_bookings',
        'schedule': crontab(minute="*/20"),
    },
}
