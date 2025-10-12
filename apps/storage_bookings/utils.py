import random
import string
import math
from django.db import transaction
from .models import Counter
from datetime import timedelta, datetime
from django.utils import timezone, dateparse
import os
import json

COMP_OFF_MINUTES = int(os.getenv('COMP_OFF_MINUTES'))

def get_next_bag_id(prefix='BAG', width=3):
    with transaction.atomic():
        counter, _ = Counter.objects.select_for_update().get_or_create(name='bag')
        counter.value += 1
        counter.save(update_fields=['value'])
        return f"{prefix}{counter.value:0{width}d}"


def calculate_distance_km(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371  # Earth radius in KM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def return_type(value):
    if value == None:
        return 'Active'
    elif value == 'completed':
        return 'Completed'
    elif value == 'cancelled':
        return 'Cancelled'
    else:
        return 'Active'
    
def return_status(value):
    if value == None:
        return 'In Progress'
    elif value == 'completed':
        return 'Completed'
    elif value == 'cancelled':
        return 'Cancelled'
    else:
        return 'In Progress'
    
def compute_booking_end_time(booking_created_time=None, luggage_time_hours=0):
    # default now
    if booking_created_time is None:
        booking_created_time = timezone.now()
    # parse string ISO datetimes
    elif isinstance(booking_created_time, str):
        booking_created_time = dateparse.parse_datetime(booking_created_time)
        if booking_created_time is None:
            raise ValueError("booking_created_time string is not a valid datetime")
    # ensure datetime type
    if not isinstance(booking_created_time, datetime):
        raise TypeError("booking_created_time must be datetime or ISO datetime string")

    # make timezone-aware if naive
    if timezone.is_naive(booking_created_time):
        booking_created_time = timezone.make_aware(booking_created_time, timezone.get_current_timezone())

    # compute minutes
    try:
        hours = float(luggage_time_hours or 0)
    except (TypeError, ValueError):
        hours = 0.0

    comp_off = int(COMP_OFF_MINUTES)
    extra_minutes = int(hours * 60) + comp_off

    return booking_created_time + timedelta(minutes=extra_minutes)

def parse_addons_param(val):
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        val = val.strip()
        # try JSON array first
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        # comma separated fallback
        if ',' in val:
            return [x.strip() for x in val.split(',') if x.strip()]
        # single id string (maybe quoted)
        return [val.strip().strip('"').strip("'")]
    return []