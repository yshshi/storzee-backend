from django.shortcuts import render
import uuid
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from apps.users.models import User
from apps.storage_units.models import StorageUnit
from .models import StorageBooking
from .utils import generate_booking_id
import datetime
from django.utils.timezone import localtime
from rest_framework import status

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
        storage_weight = data.get("storage_weight")
        storage_booked_location = data.get("storage_booked_location")
        storage_image_url = data.get("storage_image_url")
        user_remark = data.get("user_remark", "")
        amount = data.get("amount")

        # Validation
        if not all([user_id, storage_unit_id, start_time]):
            return Response({
                "success": False,
                "message": "All required fields must be provided."
            }, status=400)
        
        if not storage_image_url and not storage_weight:
            return Response({
                "success": False,
                "message": "Image and Luggage Weight is mandatory to book a storage."
            }, status=400)

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
            storage_image_url=storage_image_url,
            storage_weight=storage_weight,
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