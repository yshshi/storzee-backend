from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from rest_framework import status
from .utils import is_valid_email,is_valid_phone,generate_otp,validate_email_or_phone,generate_random_number
from utils.send_email import send_otp_email,send_login_otp_email
from datetime import datetime, timedelta
from django.utils import timezone

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
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
        role = 'user'

    try:
        
        otp = generate_otp()
        idx = generate_random_number()
        randomAvatar = f'https://avatar.iran.liara.run/public/{idx}.png'
        req_body ={
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'otp': otp,
            'profile_picture':randomAvatar,
            'role': role
        }
        send_otp_email(email,otp, full_name)
        user_created = User.objects.create(**req_body)
        
        print(f'User created -- {user_created.id}')
        return Response({
            'user_id': user_created.id,
            'full_name': full_name,
            'email': email,
            'phone': phone
        }, status=status.HTTP_201_CREATED)


    except Exception as e:
        print(e)
        return Response({ 
            "success": "Fail",
            "message": "something went wrong!"
        }, status=400)

   

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email_phone = request.data.get("email_phone")

    if not email_phone:
        return Response({
            "success": "Fail",
            "message": "Email or phone is required!"
        }, status=400)

    input_type = validate_email_or_phone(email_phone)

    if input_type["type"] == 'email' and not input_type["valid"]:
        return Response({
            "success": "Fail",
            "message": "Invalid Email!"
        }, status=400)

    if input_type["type"] == 'phone' and not input_type["valid"]:
        return Response({
            "success": "Fail",
            "message": "Invalid Phone Number!"
        }, status=400)

    if input_type["type"] == 'unknown':
        return Response({
            "success": "Fail",
            "message": "Please enter a valid email or phone number!"
        }, status=400)

    # Initialize variables
    email = email_phone if input_type["type"] == "email" else None
    phone = email_phone if input_type["type"] == "phone" else None

    user = None
    if email:
        user = User.objects.filter(email=email).first()
    elif phone:
        user = User.objects.filter(phone=phone).first()

    if not user:
        return Response({
            "success": "Fail",
            "message": "User not found!"
        }, status=404)
    else:
        otp = generate_otp()
        user.otp = otp
        user.save()
        send_login_otp_email(user.email,otp, user.full_name)
        return Response({
            'message': 'OTP is sent to your register email.',
            'data':{
                'user_id': user.id
            }
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    user_id = request.data.get("user_id")
    otp = request.data.get("otp")

    if not user_id and not otp:
        return Response({
            "success": "Fail",
            "message": "User Id and Otp is required!"
        }, status=400)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
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

    return Response({
        "success": "Success",
        "message": "OTP verified successfully!",
        "user_id": user.id
    }, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_profile_picture(request):
    user_id = request.data.get("user_id")

    if not user_id:
        return Response({
            "success": "Fail",
            "message": "User Id is required!"
        }, status=400)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "success": "Fail",
            "message": "User not found!"
        }, status=404)
    
    idx = generate_random_number()
    randomAvatar = f'https://avatar.iran.liara.run/public/{idx}.png'    
    user.profile_picture = randomAvatar
    user.save()

    return Response({
        "success": "Success",
        "message": "Profile Picture Updated successfully!",
        "data": user
    }, status=200)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_profile(request):
    user_id = request.data.get("user_id")
    
    if not user_id:
        return Response({
            "success": "Fail",
            "message": "User ID is required."
        }, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
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
        if User.objects.filter(phone=phone).exclude(id=user.id).exists():
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
        }
    }, status=200)