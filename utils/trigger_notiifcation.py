from apps.users.models import UserNotification,User,UserDeviceToken
from rest_framework.response import Response
from apps.storage_bookings.models import StorageBooking
from apps.storage_units.utils import haversine
import requests
import environ
env = environ.Env()
from utils.send_fcm_notification import send_fcm_v1_message


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
    
    
def send_push_notification_to_user_for_delivery_arrived(saathi_id, user_id, status):
    booking_instance = StorageBooking.objects.filter(
        user_booked=user_id,
        assigned_saathi=saathi_id
    ).first()

    if booking_instance is None:
        return {"success": False, "message": "Booking not found."}

    user_instance = User.objects.filter(id=user_id).first()
    if user_instance is None:
        return {"success": False, "message": "User not found."}

    device_tokens = UserDeviceToken.objects.filter(user=user_instance).values_list('token', flat=True)

    if not device_tokens:
        return {"success": False, "message": "No device tokens found for user."}
    
    title = None
    body = None
    if status=='reached_destination':
        title='Luggage Arrived'
        body='Luggage arrived at your location.'
    else:
        title='Luggage Delivered',
        body='We have delivered your luggage.Please rate your experience!',

    for token in device_tokens:
        send_fcm_v1_message(
            token=token,
            title=title,
            body=body,
            data={"booking_id": str(booking_instance.booking_id)}
        )

    return {"success": True, "message": f"Notification sent to {len(device_tokens)} devices."}

     