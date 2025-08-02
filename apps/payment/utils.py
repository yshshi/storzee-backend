import math

import uuid
from decimal import Decimal

def calculate_distance_km(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371  # Earth radius in KM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def create_razorpay_order(amount, currency="INR", receipt=None, notes=None):
    """
    Dummy function to simulate Razorpay order creation.
    Returns a mock Razorpay order dict.
    """
    # Convert amount to paise as Razorpay expects integer values
    amount_in_paise = int(Decimal(amount) * 100)

    return {
        "id": f"order_{uuid.uuid4().hex[:14]}",  # Simulated Razorpay order_id
        "entity": "order",
        "amount": amount_in_paise,
        "amount_paid": 0,
        "amount_due": amount_in_paise,
        "currency": currency,
        "receipt": receipt or f"rcpt_{uuid.uuid4().hex[:10]}",
        "status": "created",
        "notes": notes or {},
        "created_at": 1693046400  # Static timestamp (optional)
    }