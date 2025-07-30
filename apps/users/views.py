from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from rest_framework import status
from .utils import is_valid_email,is_valid_phone

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
        req_body ={
            'full_name': full_name,
            'email': email,
            'phone': phone
        }

        user_created = User.objects.create(**req_body)
        print(f'User created -- {user_created.id}')
        return Response({
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

   