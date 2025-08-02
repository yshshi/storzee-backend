import random
import string
import math

def generate_booking_id(length=8):
    chars = string.ascii_uppercase + string.digits  # A-Z + 0-9
    return 'BOOKINGID_'+''.join(random.choices(chars, k=length))


def calculate_distance_km(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371  # Earth radius in KM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c