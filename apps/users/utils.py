import re
import random
from datetime import datetime, timezone

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def is_valid_phone(phone):
    pattern = r'^[6-9]\d{9}$'  # 10-digit Indian number starting with 6–9
    return re.match(pattern, phone)

def generate_otp():
    return str(random.randint(100000, 999999))

def validate_email_or_phone(input_str):
    input_str = input_str.strip()
    
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    phone_pattern = r'^[6-9]\d{9}$'

    if re.match(email_pattern, input_str):
        return {"type": "email", "valid": True}
    elif re.match(phone_pattern, input_str):
        return {"type": "phone", "valid": True}
    else:
        # Check whether it's more like email or phone but invalid
        if "@" in input_str or "." in input_str:
            return {"type": "email", "valid": False}
        elif input_str.isdigit():
            return {"type": "phone", "valid": False}
        else:
            return {"type": "unknown", "valid": False}
        
def generate_random_number():
    return str(random.randint(1, 99))

def get_time_diff(created_at):
    now = datetime.now(timezone.utc)   # current UTC time
    diff = now - created_at

    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days

    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif minutes < 60:
        return f"{int(minutes)} minutes ago"
    elif hours < 24:
        return f"{int(hours)} hours ago"
    else:
        return f"{days} days ago"