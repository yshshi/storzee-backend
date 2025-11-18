from celery import shared_task

@shared_task
def sample_task():
    print("Cron running successfully...")
    return "done"
