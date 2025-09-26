from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.saathi.models import Saathi
from apps.storage_bookings.models import StorageBooking
from rest_framework import status
from apps.users.models import User, UserNotification, UserDeviceToken
from apps.users.utils import generate_otp,is_valid_email,is_valid_phone
from utils.send_email import send_login_otp_email
import environ
env = environ.Env()
from datetime import datetime, timedelta
from django.utils import timezone
from utils.get_city_name import get_city_name_from_coords
import os
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from apps.wallet.models import SaathiWallet
from apps.storage_bookings.models import StorageBooking
from utils.calculate_route import calculate_route

# Load configs from env
BASE_FARE_DISTANCE = float(os.getenv("BASE_FARE_DISTANCE", 3))  # km
BASE_FARE_AMOUNT = float(os.getenv("BASE_FARE_AMOUNT", 50))
PER_KM_RATE = float(os.getenv("PER_KM_RATE", 10))
TASK_BONUS = float(os.getenv("TASK_BONUS", 5))  # max extra
ALLOWED_TIME_PER_KM = float(os.getenv("ALLOWED_TIME_PER_KM", 5))  # min/km


# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny])  
def saathi_booking_response(request):
    try:
        saathi_id = request.data.get("saathi_id") 
        saathi = Saathi.objects.filter(id=saathi_id).first()
        if not saathi:
            return Response({"success": False, "message": "Saathi Not Found"}, status=400)
        booking_id = request.data.get("booking_id")
        action = request.data.get("action")

        if not booking_id or action not in ["pickup_accept","delivery_accept"]:
            return Response({"success": False, "message": "Invalid booking_id or action"}, status=400)
        if not saathi.is_verified or not saathi.is_available:
            return Response({"success": False, "message": "You are not eligible to accept bookings"}, status=403)
        
        booking = StorageBooking.objects.filter(id=booking_id).first()
        booking.assigned_saathi = saathi

        if action == "accept":
            booking.status = 'confirmed'
        elif action == "delivery_accept":
            booking.status = "out_for_delivery"
        booking.save()
        saathi.is_available = False
        saathi.save()
    except StorageBooking.DoesNotExist:
        return Response({"success": False, "message": "Booking not found"}, status=404)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def saathi_login(request):
    phone = request.data.get("phone")

    if not phone:
        return Response({ 
            "success": "Fail",
            "message": "Phone is required!"
        }, status=400)
    
    user_instance = Saathi.objects.filter(phone=phone).first()

    if not user_instance:
        return Response({
            "success": "Pass",
            "is_register": False,
            "data": None
        }, status=200)
    
    otp = generate_otp()
    user_instance.otp = otp
    user_instance.save()
    if env('ENV')=='Prod':
        send_login_otp_email(user_instance.email,otp, user_instance.full_name)
    else:
        user_instance.otp = '123456'
        user_instance.save()

    response_body = {
        'saathi_id': user_instance.id,
        'full_name': user_instance.full_name,
        'phone': user_instance.phone,
        'email': user_instance.email,
        'is_verified': user_instance.is_verified,
        'profile_verified': user_instance.profile_verified,
        'document_verified': user_instance.document_verified
    }
    return Response({
        'message': 'OTP is sent to your register email.',
        'data': response_body,
        "is_register": True
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_saathi(request):
    full_name = request.data.get("full_name")
    email = request.data.get("email")
    phone = request.data.get("phone")
    role = request.data.get("role")

    if not full_name:
        return Response({ 
            "success": "Fail",
            "message": "Full Name is required!"
        }, status=400)
    
    if not email:
        return Response({ 
            "success": "Fail",
            "message": "Email is required!"
        }, status=400)
    
    if not is_valid_email(email):
        return Response({ 
            "success": "Fail",
            "message": "Invalid Email!"
        }, status=400)
    
    if not phone:
        return Response({ 
            "success": "Fail",
            "message": "Phone is required!"
        }, status=400)
    
    if not is_valid_phone(phone):
        return Response({ 
            "success": "Fail",
            "message": "Invalid phone number!"
        }, status=400)
    
    if not role:
        role = 'saathi'

    try:
        
        # otp = generate_otp()
        # send_otp_email(email,otp, full_name)
        if env('ENV')=='Prod':
            send_login_otp_email(email,otp,full_name)
        else:
            otp = '123456'

        req_body ={
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'otp': otp,
            'role': role,
            'otp_generated_time': timezone.now()
        }
        user_created = Saathi.objects.create(**req_body)

        return Response({
            'saathi_id': user_created.id,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'is_verified': user_created.is_verified,
            'document_verified':user_created.document_verified
        }, status=status.HTTP_201_CREATED)


    except Exception as e:
        print(e)
        return Response({ 
            "success": "Fail",
            "message": "something went wrong!"
        }, status=400)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_saathi_otp(request):
    user_id = request.data.get("saathi_id")
    otp = request.data.get("otp")

    if not user_id and not otp:
        return Response({
            "success": "Fail",
            "message": "User Id and Otp is required!"
        }, status=400)
    
    try:
        user = Saathi.objects.get(id=user_id)
    except Saathi.DoesNotExist:
        return Response({
            "success": "Fail",
            "message": "User not found!"
        }, status=404)
    
    if user.otp_generated_time and timezone.now() > user.otp_generated_time + timedelta(minutes=10):
        return Response({
            "success": "Fail",
            "message": "OTP has expired. Please request a new one."
        }, status=400)

    if user.otp != otp:
        return Response({
            "success": "Fail",
            "message": "Invalid OTP!"
        }, status=400)

    # Optionally: mark user as verified, clear OTP
    user.is_verified = True  # if you have a field like this
    user.otp = None
    user.save()

    response_body = {
        'saathi_id': user.id,
        'full_name': user.full_name,
        'phone': user.phone,
        'email': user.email,
        'is_verified': user.is_verified,
        'profile_verified': user.profile_verified,
        'document_verified':user.document_verified
    }

    return Response({
        "success": "Success",
        "message": "OTP verified successfully!",
        "data": response_body
    }, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def upload_saathi_documents(request):
    user_id = request.data.get("saathi_id")
    pan_card_number = request.data.get("pan_card_number")
    aadhar_card_number = request.data.get("aadhar_card_number")
    vehicle_number = request.data.get("vehicle_number")
    pan_card = request.data.get("pan_card")
    aadhar_card = request.data.get("aadhar_card")

    if not all([user_id, pan_card_number, aadhar_card_number, vehicle_number]):
        return Response({"success": False, "message": "All feilds details are required."}, status=400)
    
    try:
        user = Saathi.objects.get(id=user_id)
    except Saathi.DoesNotExist:
        return Response({
            "success": "Fail",
            "message": "User not found!"
        }, status=404)
    
    user.vehicle_number= vehicle_number
    user.pan_card_number = pan_card_number
    user.aadhaar_card_number = aadhar_card_number
    user.pan_card_upload_link = pan_card
    user.aadhaar_card_upload_link = aadhar_card
    user.profile_verified = True
    user.terms_and_condition_agreed = True
    user.save()

    response_body = {
        'saathi_id': user.id,
        'full_name': user.full_name,
        'phone': user.phone,
        'email': user.email,
        'is_verified': user.is_verified,
        'profile_verified': user.profile_verified,
        'document_verified':user.document_verified
    }

    return Response({
        "success": "Success",
        "message": "Profile verified successfully!",
        "data": response_body
    }, status=200)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_saathi_profile(request):
    user_id = request.data.get("user_id")
    
    if not user_id:
        return Response({
            "success": "Fail",
            "message": "User ID is required."
        }, status=400)

    try:
        user = Saathi.objects.get(id=user_id)
    except Saathi.DoesNotExist:
        return Response({
            "success": "Fail",
            "message": "User not found."
        }, status=404)

    # Optional fields to update
    full_name = request.data.get("full_name")
    phone = request.data.get("phone")
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")

    # Update only if provided
    if full_name:
        user.full_name = full_name
    
    if phone:
        if Saathi.objects.filter(phone=phone).exclude(id=user.id).exists():
            return Response({
                "success": "Fail",
                "message": "Phone number already in use."
            }, status=400)
        user.phone = phone

    if latitude:
        try:
            user.latitude = float(latitude)
        except ValueError:
            return Response({"message": "Invalid latitude."}, status=400)

    if longitude:
        try:
            user.longitude = float(longitude)
        except ValueError:
            return Response({"message": "Invalid longitude."}, status=400)
        
    if longitude and latitude:
        city = get_city_name_from_coords(lat=latitude,lng=longitude)
        user.city_name = city

    user.save()

    return Response({
        "success": "Success",
        "message": "Profile updated successfully.",
        "data": {
            "user_id": user.id,
            "full_name": user.full_name,
            "phone": user.phone,
            "latitude": user.latitude,
            "longitude": user.longitude,
            'is_verified': user.is_verified,
            'profile_verified': user.profile_verified,
            'document_verified':user.document_verified
        }
    }, status=200)


def calculate_fare(user_lat, user_lng, unit_lat, unit_lng, actual_time_taken=None):
    """
    Calculate fare & incentive/penalty
    """

    # --- Step 1: Get distance & duration from Google Maps ---
    # directions = gmaps.directions(
    #     (user_lat, user_lng),
    #     (unit_lat, unit_lng),
    #     mode="driving",
    #     departure_time=datetime.now()
    # )

    # distance_meters = directions[0]['legs'][0]['distance']['value']
    # duration_seconds = directions[0]['legs'][0]['duration']['value']

    distance_km, expected_time_min, _ = calculate_route(user_lat, user_lng, unit_lat, unit_lng)

    if distance_km is None:
        return {"error": "Unable to calculate route."}
    
    distance_meters = distance_km * 1000

    distance_km = distance_meters / 1000.0
    expected_time_min = (distance_km * ALLOWED_TIME_PER_KM)

    # --- Step 2: Fare calculation ---
    if distance_km <= BASE_FARE_DISTANCE:
        fare = BASE_FARE_AMOUNT
    else:
        extra_km = distance_km - BASE_FARE_DISTANCE
        fare = BASE_FARE_AMOUNT + (extra_km * PER_KM_RATE)

    # --- Step 3: Bonus/Penalty ---
    bonus = TASK_BONUS
    if actual_time_taken:
        delay = actual_time_taken - expected_time_min
        if delay > 0:
            # Reduce bonus proportional to delay (e.g., lose 1 point every 5 min delay)
            penalty = min(bonus, (delay / expected_time_min) * bonus)
            bonus -= penalty

    return {
        "distance_km": round(distance_km, 2),
        "expected_time_min": round(expected_time_min, 2),
        "base_fare": round(fare, 2),
        "bonus": round(bonus, 2),
        "total_amount": round(fare + bonus, 2)
    }


class CalculateFareAPI(APIView):
    """
    API to calculate fare for a delivery task
    """

    def post(self, request):
        user_lat = float(request.data.get("user_lat"))
        user_lng = float(request.data.get("user_lng"))
        unit_lat = float(request.data.get("unit_lat"))
        unit_lng = float(request.data.get("unit_lng"))
        actual_time_taken = request.data.get("actual_time_taken")  # minutes, optional

        result = calculate_fare(user_lat, user_lng, unit_lat, unit_lng, float(actual_time_taken) if actual_time_taken else None)
        return Response(result, status=status.HTTP_200_OK)


class CompleteTaskAPI(APIView):
    """
    API to finalize task and credit Saathi wallet
    """

    def post(self, request, task_id):
        try:
            task = StorageBooking.objects.get(id=task_id)
            actual_time_taken = float(request.data.get("actual_time_taken"))

            current_context = request.data.get("current_context")

            if current_context == 'pickup':
                user_lat = task.storage_latitude
                user_lng = task.storage_longitude
                unit_lat = task.storage_unit.latitude
                unit_lng = task.storage_unit.longitude
            elif current_context == 'delivery':
                user_lat = task.return_lat
                user_lng = task.return_lng
                unit_lat = task.storage_unit.latitude
                unit_lng = task.storage_unit.longitude

            result = calculate_fare(
                user_lat, user_lng, unit_lat, unit_lng,
                actual_time_taken
            )

            # Update wallet
            wallet, _ = SaathiWallet.objects.get_or_create(saathi=task.assigned_saathi)
            wallet.balance += result["total_amount"]
            wallet.save()

            task.status = "completed"
            task.completed_at = datetime.now()
            task.earned_amount = result["total_amount"]
            task.save()

            return Response({"booking_id": task.id, "payout": result}, status=status.HTTP_200_OK)

        except StorageBooking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
