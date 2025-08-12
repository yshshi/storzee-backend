import math

import uuid
from decimal import Decimal
from utils.RazorpayUtils import RazorpayClient 
from rest_framework.serializers import ValidationError
from rest_framework import status
import random
import string
from datetime import datetime

def generate_receipt_number():
    """
    Generates an alphanumeric receipt number in the format:
    YYYYMMDD-AB12C
    Where AB12C is a random mix of uppercase letters and digits.
    Example: PAYMENT-20250812-K9X3B
    """
    date_str = datetime.now().strftime("%Y%m%d")
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"PAYMENT-{date_str}-{suffix}"

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
    function to simulate Razorpay order creation.
    Returns a Razorpay order dict.
    """
    # Convert amount to paise as Razorpay expects integer values

    amount_in_paise = int(Decimal(amount) * 100)

    order = RazorpayClient.create_order(amount=amount_in_paise)

    if order.get("status") != 'created':
        raise ValidationError({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to create Razorpay Order"
            })

    return {
        "id": order.get("id"),  # Simulated Razorpay order_id
        "entity": "order",
        "amount": amount,
        "amount_paid": 0,
        "amount_due": amount_in_paise,
        "currency": currency,
        "receipt": order.get("receipt"),
        "status": "created",
        "notes": notes or {},
        "created_at": order.get("created_at")
    }


def confirm_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    function to simulate Razorpay order creation.
    Returns a Razorpay order dict.
    """
    payment_confirm = RazorpayClient.verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature)


    return {
        "id": payment_confirm.get("id"),  
        "payment_data": payment_confirm
    }
