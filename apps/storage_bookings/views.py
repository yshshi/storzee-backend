from django.shortcuts import render
import uuid
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from apps.users.models import User
from apps.storage_units.models import StorageUnit
from .models import StorageBooking
from .utils import generate_booking_id,calculate_distance_km
import datetime
from django.utils.timezone import localtime
from rest_framework import status
from django.core.files.base import ContentFile
import base64
from apps.storage_units.models import StorageUnit

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    try:
        data = request.data

        user_id = data.get("user_id")
        storage_unit_id = data.get("storage_unit_id")
        booking_type = data.get("booking_type")  # 'hourly' or 'daily'
        start_time = data.get("booking_created_time")
        # storage_weight = data.get("storage_weight")
        storage_booked_location = data.get("storage_booked_location")
        # storage_image_url = data.get("storage_image_url")
        user_remark = data.get("user_remark", "")
        amount = data.get("amount")

        # Validation
        if not all([user_id, storage_unit_id, start_time]):
            return Response({
                "success": False,
                "message": "All required fields must be provided."
            }, status=400)
        
        # if not storage_image_url and not storage_weight:
        #     return Response({
        #         "success": False,
        #         "message": "Image and Luggage Weight is mandatory to book a storage."
        #     }, status=400)

        user = User.objects.get(id=user_id)
        storage_unit = StorageUnit.objects.get(id=storage_unit_id)

        booking_id = generate_booking_id()

        booking = StorageBooking.objects.create(
            user_booked=user,
            storage_unit=storage_unit,
            booking_id=booking_id,
            booking_type=booking_type,
            booking_created_time=start_time,
            status='active',
            # storage_image_url=storage_image_url,
            # storage_weight=storage_weight,
            is_active=True,
            storage_booked_location=storage_booked_location,
            user_remark=user_remark,
            amount=amount
        )

        return Response({
            "success": True,
            "message": "Storage booked successfully.",
            "data": {
                "booking_id": booking.booking_id,
                "storage_title": storage_unit.title,
                "start_time": booking.booking_created_time,
                "end_time": booking.booking_end_time,
                "status": booking.status
            }
        }, status=201)

    except User.DoesNotExist:
        return Response({"success": False, "message": "User not found."}, status=404)
    except StorageUnit.DoesNotExist:
        return Response({"success": False, "message": "Storage unit not found."}, status=404)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_luggage_location_by_saathi(request):
    data = request.data

    saathi_id = data.get("saathi_id")
    luggage_id = data.get("luggage_id")
    current_latitude = data.get("current_latitude")
    current_longitude = data.get("current_longitude")
    luggage_status = data.get("luggage_status")
    rakshak_id = data.get("rakshak_id")

    if not all([saathi_id, luggage_id, current_latitude,current_longitude]):
            return Response({
                "success": False,
                "message": "All required fields must be provided."
            }, status=400)
    try:
        storage_instance = StorageBooking.objects.filter(id=luggage_id).first()

        if not storage_instance:
            return Response({
                    "success": False,
                    "message": "No Luggage Found!"
                }, status=400)
        
        storage_instance.storage_latitude = current_latitude
        storage_instance.storage_longitude = current_longitude
        storage_instance.storage_location_updated_at = datetime.now()

        if luggage_status=='pickup':
            storage_instance.status = 'pickup'
            saathi_instance = User.objects.filter(id=saathi_id).first()
            storage_instance.assigned_saathi = saathi_instance
        elif luggage_status=='out_for_delivery':
            storage_instance.status = 'out_for_delivery'
            saathi_instance = User.objects.filter(id=saathi_id).first()
            storage_instance.assigned_saathi = saathi_instance
        else:
            storage_instance.status = 'luggage_Stored'
            raksak_instance = User.objects.filter(id=rakshak_id).first()
            storage_instance.luggage_rakshak = raksak_instance

        storage_instance.save()

    except User.DoesNotExist:
        return Response({"success": False, "message": "User not found."}, status=404)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def update_luggage_deatils(request):
    data = request.data
    luggage_id = data.get("luggage_id")
    luggage_status = data.get("luggage_status")
    rakshak_id = data.get("rakshak_id")

    if not all([ luggage_id, luggage_status,rakshak_id]):
            return Response({
                "success": False,
                "message": "All required fields must be provided."
            }, status=400)
    
    try:
        storage_instance = StorageBooking.objects.filter(id=luggage_id).first()

        if not storage_instance:
            return Response({
                    "success": False,
                    "message": "No Luggage Found!"
                }, status=400)
        
        if luggage_status=='storage':
            storage_instance.status = 'luggage_Stored'

        if luggage_status=='out_for_delivery':
            storage_instance.status = 'out_for_delivery'

        if luggage_status=='completed':
            storage_instance.status = 'completed'

        if luggage_status=='cancelled':
            storage_instance.status = 'cancelled'
        
        if rakshak_id:
            rakshak_instance = User.objects.filter(id=rakshak_id).first()
            storage_instance.luggage_rakshak = rakshak_instance
        storage_instance.save()

    except User.DoesNotExist:
        return Response({"success": False, "message": "User not found."}, status=404)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_luggage_deatils(request):
    data = request.data
    user_id = data.get("user_id")

    bookings = StorageBooking.objects.filter(user_booked=user_id).select_related(
            'storage_unit',
            'storage_unit__owner',
            'assigned_saathi',
            'luggage_rakshak'
        ).order_by('-created_at')

    data = []
    for booking in bookings:
        data.append({
            "id": booking.id,
            "booking_id": booking.booking_id,
            "booking_type": booking.booking_type,
            "status": booking.status,
            "booking_created_time": booking.booking_created_time,
            "booking_end_time": booking.booking_end_time,
            "amount": booking.amount,
            "storage_weight": booking.storage_weight,
            "storage_latitude": booking.storage_latitude,
            "storage_longitude": booking.storage_longitude,
            "storage_booked_location": booking.storage_booked_location,
            "storage_location_updated_at": booking.storage_location_updated_at,
            "user_remark": booking.user_remark,

            "user_booked": {
                "id": booking.user_booked.id,
                "full_name": booking.user_booked.full_name,
                "email": booking.user_booked.email,
                "phone": booking.user_booked.phone,
            },
            "assigned_saathi": {
                "id": booking.assigned_saathi.id,
                "full_name": booking.assigned_saathi.full_name,
                "email": booking.assigned_saathi.email,
                "phone": booking.assigned_saathi.phone,
            },
            "luggage_rakshak": {
                "id": booking.luggage_rakshak.id,
                "full_name": booking.luggage_rakshak.full_name,
                "email": booking.luggage_rakshak.email,
                "phone": booking.luggage_rakshak.phone,
            },
            "storage_unit": {
                "id": booking.storage_unit.id,
                "title": booking.storage_unit.title,
                "address": booking.storage_unit.address,
                "city": booking.storage_unit.city,
                "price_per_hour": str(booking.storage_unit.price_per_hour),
                "price_per_day": str(booking.storage_unit.price_per_day),
                "owner": {
                    "id": booking.storage_unit.owner.id,
                    "full_name": booking.storage_unit.owner.full_name,
                    "email": booking.storage_unit.owner.email,
                    "phone": booking.storage_unit.owner.phone,
                }
            }
        })

    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_pickup(request):
    user = request.user

    if user.role != 'saathi':
        return Response({"success": False, "message": "Only saathi can access this API."}, status=403)

    booking_id = request.data.get('booking_id')
    confirmed_weight = request.data.get('confirmed_weight')
    luggage_images = request.data.get('luggage_images')  # Should be list of base64 strings

    if not booking_id or not confirmed_weight or not luggage_images:
        return Response({"success": False, "message": "booking_id, confirmed_weight, and luggage_images are required."}, status=400)

    try:
        booking = StorageBooking.objects.get(booking_id=booking_id, assigned_saathi=user)
    except StorageBooking.DoesNotExist:
        return Response({"success": False, "message": "Booking not found or not assigned to you."}, status=404)

    if booking.status != 'active':
        return Response({"success": False, "message": f"Cannot pick up luggage. Current status: {booking.status}"}, status=400)

    # Process and save images
    image_urls = []
    for index, image_base64 in enumerate(luggage_images):
        try:
            format, imgstr = image_base64.split(';base64,') 
            ext = format.split('/')[-1]
            file_name = f"luggage_{booking.booking_id}_{index}_{uuid.uuid4()}.{ext}"

            # Save file to Django FileField or custom storage logic
            decoded_file = ContentFile(base64.b64decode(imgstr), name=file_name)
            # If you have Image model or S3 uploader use that, else temporarily save paths
            # For now, we fake the URL
            image_urls.append(f"https://cdn.storzee.in/uploads/{file_name}")
        except Exception as e:
            return Response({"success": False, "message": f"Error processing image: {str(e)}"}, status=400)

    # Update booking
    booking.status = 'pickup'
    booking.storage_weight = confirmed_weight
    booking.luggage_images = image_urls  # JSONField
    booking.pickup_confirmed_at = timezone.now()
    booking.save()

    return Response({
        "success": True,
        "message": "Pickup confirmed and luggage status updated to 'pickup'.",
        "data": {
            "booking_id": booking.booking_id,
            "status": booking.status,
            "image_urls": image_urls
        }
    }, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_to_rakshak(request):
    userId = request.user.get("user_id")
    user = User.objects.filter(id=userId).first()

    if user.role != 'saathi':
        return Response({"success": False, "message": "Only saathi can access this API."}, status=403)

    booking_id = request.data.get('booking_id')

    if not booking_id:
        return Response({"success": False, "message": "booking_id is required."}, status=400)

    try:
        booking = StorageBooking.objects.select_related('storage_unit').get(
            booking_id=booking_id,
            assigned_saathi=user
        )
    except StorageBooking.DoesNotExist:
        return Response({"success": False, "message": "Booking not found or not assigned to you."}, status=404)

    if booking.status != 'pickup':
        return Response({"success": False, "message": f"Invalid booking status: {booking.status}. Expected 'pickup'."}, status=400)

    # Update status to 'luggage_Stored'
    booking.status = 'luggage_Stored'
    booking.storage_location_updated_at = timezone.now()
    booking.delivered_to_rakshak_at = timezone.now()

    # Update current coordinates to rakshak storage unit
    booking.storage_latitude = booking.storage_unit.latitude
    booking.storage_longitude = booking.storage_unit.longitude
    booking.save()

    return Response({
        "success": True,
        "message": "Luggage successfully submitted to Rakshak.",
        "data": {
            "booking_id": booking.booking_id,
            "status": booking.status,
            "storage_location": {
                "lat": booking.storage_latitude,
                "lng": booking.storage_longitude
            }
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def request_return(request):
    userId = request.user.get("user_id")
    user = User.objects.filter(id=userId).first()
    data = request.data

    try:
        booking = StorageBooking.objects.get(booking_id=data.get("booking_id"), user_booked=user)
    except StorageBooking.DoesNotExist:
        return Response({"success": False, "message": "Booking not found."}, status=404)

    if booking.status != 'luggage_Stored':
        return Response({"success": False, "message": "Luggage is not stored yet."}, status=400)

    delivery_lat = data.get("delivery_lat")
    delivery_lng = data.get("delivery_lng")
    delivery_address = data.get("delivery_address")
    preferred_time = data.get("preferred_time")

    if not all([delivery_lat, delivery_lng, delivery_address, preferred_time]):
        return Response({"success": False, "message": "All delivery details are required."}, status=400)

    # Calculate distance between storage and delivery location
    distance_km = calculate_distance_km(float(booking.storage_unit.latitude), float(booking.storage_unit.longitude), float(delivery_lat), float(delivery_lng))

    # price details 
    storage_unit_instance = StorageUnit.objects.filter(id=booking.storage_unit).first()
    # Estimate amount: ₹50 base + ₹10/km
    estimated_amount = int(storage_unit_instance.price_per_hour) + (int(storage_unit_instance.price_per_km) * distance_km)
    estimated_amount = round(estimated_amount)

    # Update booking
    booking.return_requested_at = timezone.now()
    booking.return_lat = delivery_lat
    booking.return_lng = delivery_lng
    booking.return_address = delivery_address
    booking.return_preferred_time = preferred_time
    booking.return_estimated_amount = estimated_amount
    booking.save()

    return Response({
        "success": True,
        "message": "Return request initiated. Please complete payment to proceed.",
        "data": {
            "booking_id": booking.booking_id,
            "estimated_amount": estimated_amount,
            "distance_km": round(distance_km, 2),
            "preferred_time": preferred_time
        }
    })