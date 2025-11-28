from celery import shared_task
from utils.trigger_notiifcation import send_push_notification
from apps.users.models import UserDeviceToken
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.core.cache import cache
from apps.storage_bookings.models import StorageBooking

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

@shared_task
def cron_notify_booking_ending_soon():
    current_time = now()
    window_start = current_time
    window_end = current_time + timedelta(minutes=30)

    bookings = StorageBooking.objects.filter(
        status__in=['active', 'confirmed', 'luggage_Stored'],
        booking_end_time__gte=window_start,
        booking_end_time__lte=window_end,
        ending_soon_notified=False      # NEW: No duplicate checks needed
    )

    for booking in bookings:
        message = (
            "⏳ Your storage booking is ending soon! "
            "Please pick up your luggage or extend your booking."
        )

        send_push_notification(
            user=booking.user_booked,
            title="Your Booking Ends in 30 Minutes",
            message=message
        )

        booking.ending_soon_notified = True
        booking.save(update_fields=['ending_soon_notified'])


@shared_task
def cron_notify_late_pickup():
    current_time = now()

    bookings = StorageBooking.objects.filter(
        booking_end_time__lt=current_time,
        status__in=['active', 'confirmed', 'luggage_Stored'],
        late_pickup_notified=False    # NEW
    )

    for booking in bookings:
        message = (
            "⚠️ Your booking time has ended. Please pick up your luggage. "
            "Additional charges may apply for late pickup."
        )

        send_push_notification(
            user=booking.user_booked,
            title="Your Booking Time Has Ended",
            message=message
        )

        booking.late_pickup_notified = True
        booking.save(update_fields=['late_pickup_notified'])

@shared_task
def send_starting_notification():
    title = "Big Match Today! Travel Light, Cheer Loud!"
    body = "Going to watch India vs South Africa? Store your bags safely with us & enjoy the game worry-free."

    tokens = UserDeviceToken.objects.all()
    for t in tokens:
        send_push_notification(t.token, title, body)

    return "Notifications sent!"

@shared_task
def send_midday_notification():
    title = "Let’s Cheer India Without Any Bags Holding You Back!"
    body = "Store your luggage nearby and enjoy the match hands-free."

    tokens = UserDeviceToken.objects.all()
    for t in tokens:
        send_push_notification(t.token, title, body)

    return "Notifications sent!"

@shared_task
def send_discount_notification():
    title = "Match Day Special: Your First Hour is from us!"
    body = "We know you are here to support Team India, we are here to support you! Get your first hour of luggage storage free today."

    tokens = UserDeviceToken.objects.all()
    for t in tokens:
        send_push_notification(t.token, title, body)

    return "Notifications sent!"

@shared_task
def send_during_notification():
    title = "How’s the Match Vibe? We’re Keeping Your Luggage Safe!"
    body = "A soft engagement ping to stay top-of-mind."

    tokens = UserDeviceToken.objects.all()
    for t in tokens:
        send_push_notification(t.token, title, body)

    return "Notifications sent!"

@shared_task
def send_post_notification():
    title = "Match Over? Pick Your Luggage Anytime!"
    body = "We’re open. Collect at your convenience."

    tokens = UserDeviceToken.objects.all()
    for t in tokens:
        send_push_notification(t.token, title, body)

    return "Notifications sent!"

@shared_task
def cron_auto_cancel_unstored_bookings():
    """
    Cancel bookings that were confirmed but never moved to 'luggage_Stored'
    within 2 hours from booking_start_time.
    """
    current_time = now()
    two_hours_ago = current_time - timedelta(hours=2)

    # Bookings that are confirmed for more than 2 hours
    bookings = StorageBooking.objects.filter(
        status="confirmed",
        booking_start_time__lte=two_hours_ago
    )

    for booking in bookings:
        booking.status = "cancelled"
        booking.save(update_fields=["status"])

        # Optional: notify user
        try:
            from utils.trigger_notiifcation import send_push_notification
            send_push_notification(
                user=booking.user_booked,
                title="Booking Cancelled",
                message="Your booking was cancelled because luggage was not stored within 2 hours."
            )
        except Exception as e:
            print("Notification error:", e)

    return f"{bookings.count()} bookings auto-cancelled"