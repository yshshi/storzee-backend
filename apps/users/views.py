from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from rest_framework import status
from .utils import is_valid_email,is_valid_phone,generate_otp,validate_email_or_phone
from utils.send_email import send_otp_email,send_login_otp_email
from datetime import datetime, timedelta

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    full_name = request.data.get("full_name")
    email = request.data.get("email")
    phone = request.data.get("phone")

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

    try:
        
        otp = generate_otp()
        req_body ={
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'otp': otp
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
    
    if user.otp_generated_time and datetime.now() > user.otp_generated_time + timedelta(minutes=10):
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