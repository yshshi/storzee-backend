from django.db import transaction
from math import radians, sin, cos, sqrt, atan2
from apps.saathi.models import Saathi
from apps.storage_units.utils import haversine
from apps.storage_bookings.models import StorageBooking 
import environ
env = environ.Env()
from utils.trigger_notiifcation import send_push_notification_to_saathi_for_pickup,send_push_notification_to_saathi_for_delivery

def trigger_notification_to_saathi(bookingid):
    booking = StorageBooking.objects.filter(id=bookingid).first()
    nearby_saathis = []
    for saathi in Saathi.objects.filter(is_available=True):
                if saathi.latitude and saathi.longitude:
                    distance = haversine(booking.storage_latitude, booking.storage_longitude, saathi.latitude, saathi.longitude)
                    if distance <= int(env('SAATHI_AVALIBLE_DISTANCE', default='10')):
                        nearby_saathis.append(saathi)

    send_push_notification_to_saathi_for_pickup(nearby_saathis,bookingid)
    


def trigger_notification_to_saathi_return(bookingid):
    booking = StorageBooking.objects.filter(id=bookingid).first()
    nearby_saathis = []
    for saathi in Saathi.objects.filter(is_available=True):
                if saathi.latitude and saathi.longitude:
                    distance = haversine(booking.return_lat, booking.return_lng, saathi.latitude, saathi.longitude)
                    if distance <= int(env('SAATHI_AVALIBLE_DISTANCE', default='10')):
                        nearby_saathis.append(saathi)
    
    send_push_notification_to_saathi_for_delivery(nearby_saathis,bookingid)
    