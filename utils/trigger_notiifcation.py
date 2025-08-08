from apps.users.models import UserNotification
from rest_framework.response import Response
from apps.storage_bookings.models import StorageBooking
from apps.storage_units.utils import haversine
import requests
import environ
env = environ.Env()


def send_push_notification_to_saathi_for_pickup(nearby_saathis, booking_id):
    try:
        booking = StorageBooking.objects.filter(id=booking_id).first()
        city = None
        booking_amount = None
        for saathi in nearby_saathis:
                distance = haversine(booking.storage_latitude, booking.storage_longitude, saathi.latitude, saathi.longitude)
                if saathi.fcm_token:
                    payload = {
                        "to": saathi.fcm_token,
                        "notification": {
                            "title": "New Booking Alert",
                            "booking_code": booking.booking_id,
                            "Pickup": city,
                            "amount": booking_amount,
                            "distance": distance,
                            "sound": "default",
                            "booking_id": booking.id
                        },
                    }
                    requests.post(
                        "https://fcm.googleapis.com/fcm/send",
                        headers={
                            "Authorization": f"key={env('FCM_SERVER_KEY')}",
                            "Content-Type": "application/json"
                        },
                        json=payload
                    )
    except Exception as e:
         return Response({"success": False, "message": "Unable to inform nearby saathi."}, status=404)
    

def send_push_notification_to_saathi_for_delivery(nearby_saathis, booking_id):
    try:
        booking = StorageBooking.objects.filter(id=booking_id).first()
        city = None
        booking_amount = None
        for saathi in nearby_saathis:
                distance = haversine(booking.return_lat, booking.return_lng, saathi.latitude, saathi.longitude)
                if saathi.fcm_token:
                    payload = {
                        "to": saathi.fcm_token,
                        "notification": {
                            "title": "New Booking Alert",
                            "booking_code": booking.booking_id,
                            "Pickup": city,
                            "amount": booking_amount,
                            "distance": distance,
                            "sound": "default",
                            "booking_id": booking.id
                        },
                    }
                    requests.post(
                        "https://fcm.googleapis.com/fcm/send",
                        headers={
                            "Authorization": f"key={env('FCM_SERVER_KEY')}",
                            "Content-Type": "application/json"
                        },
                        json=payload
                    )
    except Exception as e:
         return Response({"success": False, "message": "Unable to inform nearby saathi."}, status=404)