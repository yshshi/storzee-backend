import random
import string

def generate_booking_id(length=8):
    chars = string.ascii_uppercase + string.digits  # A-Z + 0-9
    return 'BOOKINGID_'+''.join(random.choices(chars, k=length))