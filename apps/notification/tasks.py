from celery import shared_task
from utils.trigger_notiifcation import send_push_notification
from apps.users.models import UserDeviceToken

@shared_task
def sample_task():
    print("Cron running successfully...")
    return "done"


@shared_task
def send_test_notification():
    print("🔔 Test Notification Cron Triggered!")
    title = "Test Notification"
    body = "This is a test notification sent from Celery cron job."

    tokens = UserDeviceToken.objects.all()
    for t in tokens:
        send_push_notification(t.token, title, body)

    return "Notifications sent!"
