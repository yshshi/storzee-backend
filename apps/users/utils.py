import re

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def is_valid_phone(phone):
    pattern = r'^[6-9]\d{9}$'  # 10-digit Indian number starting with 6–9
    return re.match(pattern, phone)