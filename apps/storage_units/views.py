from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from rest_framework import status
from .models import StorageUnit , Feedback
from .utils import haversine
from utils.get_city_name import get_city_name_from_coords

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
        price_per_km = request.data.get('price_per_km')
        available = request.data.get('available', True)
        is_active = request.data.get('is_active', True)
        rating = request.data.get('rating', 0.0)
        benefits = request.data.get('benefits', [])

        city = get_city_name_from_coords(lat=latitude,lng=longitude)
        city_name = city if city else "Unknown"

        storage = StorageUnit.objects.create(
            owner=owner,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            benefits=benefits,
            address=address,
            city=city_name,
            state=state,
            pincode=pincode,
            capacity=capacity,
            price_per_km=price_per_km,
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
 
@api_view(['GET'])
@permission_classes([AllowAny])
def get_nearby_storage_units(request):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({
            "success": False,
            "message": "User Id is required!"
        }, status=400)

    try:
        user_instance = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "success": False,
            "message": "User not found!"
        }, status=404)

    if user_instance.latitude == 0.0 and user_instance.longitude == 0.0:
        return Response({
            "success": False,
            "message": "User doesn't have valid coordinates."
        }, status=400)

    units = StorageUnit.objects.filter(available=True, is_active=True)
    result = []

    for unit in units:
        distance_km = haversine(user_instance.latitude, user_instance.longitude, unit.latitude, unit.longitude)

        # Fetch all image URLs
        images = [img.image_url for img in unit.images.all()]

        # Fetch feedback details
        feedbacks = []
        for feedback in unit.feedbacks.select_related('user').all():
            feedbacks.append({
                "user": feedback.user.full_name,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "created_at": feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        result.append({
            "id": str(unit.id),
            "title": unit.title,
            "owner": unit.owner.full_name,
            "description": unit.description,
            "address": unit.address,
            "city": unit.city,
            "state": unit.state,
            "pincode": unit.pincode,
            "latitude": unit.latitude,
            "longitude": unit.longitude,
            "price_per_hour": float(unit.price_per_hour or 0),
            "price_per_km": float(unit.price_per_km or 0),
            "rating": unit.rating,
            "benefits": unit.benefits,
            "distance_km": round(distance_km, 2),
            "images": images,
            "feedbacks": feedbacks
        })

    # Sort by distance
    result.sort(key=lambda x: x['distance_km'])

    return Response({
        "success": True,
        "data": result
    }, status=200)