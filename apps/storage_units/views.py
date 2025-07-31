from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from rest_framework import status
from .models import StorageUnit , Feedback

# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny])
def create_storage_unit(request):
    try:
        owner_id = request.data.get('owner')
        if not owner_id:
            return Response({
                "success": "Fail",
                "message": "User Id is required!"
            }, status=400)
    
        try:
            owner = User.objects.get(id=owner_id)
        except User.DoesNotExist:
            return Response({
                "success": "Fail",
                "message": "User not found!"
            }, status=404)
        
        title = request.data.get('title')
        description = request.data.get('description')
        address = request.data.get('address')
        city = request.data.get('city')
        state = request.data.get('state')
        pincode = request.data.get('pincode')
        latitude = float(request.data.get('latitude') or 0.0)
        longitude = float(request.data.get('longitude') or 0.0)
        capacity = request.data.get('capacity')
        price_per_hour = request.data.get('price_per_hour')
        price_per_day = request.data.get('price_per_day')
        available = request.data.get('available', True)
        is_active = request.data.get('is_active', True)
        rating = request.data.get('rating', 0.0)
        benefits = request.data.get('benefits', [])

        storage = StorageUnit.objects.create(
            owner=owner,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            benefits=benefits,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            capacity=capacity,
            price_per_day=price_per_day,
            price_per_hour=price_per_hour,
            available=available,
            is_active=is_active,
            rating=rating
        )

        return Response({
            "success": True,
            "message": "Storage unit created successfully.",
            "storage_id": storage.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "success": False,
            "message": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def create_feedback(request):
    try:
        user = request.data.get('user_id')
        if not user:
            return Response({
                "success": "Fail",
                "message": "User Id is required!"
            }, status=400)
    
        try:
            user_instance = User.objects.get(id=user)
        except User.DoesNotExist:
            return Response({
                "success": "Fail",
                "message": "User not found!"
            }, status=404)
        storage_unit_id = request.data.get('storage_unit_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not storage_unit_id or rating is None:
            return Response({
                "success": False,
                "message": "Storage unit ID and rating are required."
            }, status=400)

        storage_unit = StorageUnit.objects.filter(id=storage_unit_id).first()
        if not storage_unit:
            return Response({
                "success": False,
                "message": "Storage unit not found."
            }, status=404)

        feedback = Feedback.objects.create(
            storage_unit=storage_unit,
            user=user_instance,
            rating=rating,
            comment=comment
        )

        return Response({
            "success": True,
            "message": "Feedback submitted successfully.",
            "data": {
                "id": feedback.id,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "created_at": feedback.created_at
            }
        }, status=201)

    except Exception as e:
        return Response({
            "success": False,
            "message": f"Error submitting feedback: {str(e)}"
        }, status=500)