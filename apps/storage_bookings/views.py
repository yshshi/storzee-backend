from django.shortcuts import render
import uuid
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from apps.users.models import User , UserDocument
from apps.storage_units.models import StorageUnit
from apps.storage_bookings.models import StorageBooking , BookingAddon , BookingStatusHistory
from apps.storage_bookings.utils import get_next_bag_id,calculate_distance_km,return_type,return_status,compute_booking_end_time,parse_addons_param

import datetime
from django.utils.timezone import localtime
from rest_framework import status
from django.core.files.base import ContentFile
import base64
from apps.storage_units.models import StorageUnit,Addon
from apps.saathi.utils import trigger_notification_to_saathi, trigger_notification_to_saathi_return
from utils.trigger_notiifcation import send_push_notification_to_user_for_delivery_arrived
from apps.saathi.models import Saathi
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status
import os
from django.db import transaction
from django.db.models import Prefetch
from decimal import Decimal
from apps.payment.models import Payment
from datetime import datetime
from utils.trigger_notiifcation import send_ayncpush_notification
from apps.users.models import UserDeviceToken
import asyncio

MAX_BOOKING_TIME = os.getenv('MAX_BOOKING_TIME')
# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    try:
        file = request.FILES.get('luggage_pic')
        user_id = request.data.get("user_id")
        storage_unit_id = request.data.get("storage_unit_id")
        start_time = request.data.get("booking_created_time")
        storage_booked_location = request.data.get("storage_booked_location")
        addons_param = request.data.get('addons')
        amount = request.data.get("amount")
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")
        user_remark = request.data.get("user_remark", "")
        luggage_time = request.data.get("luggage_time")

        # Validation
        if not all([user_id, storage_unit_id, start_time, latitude, longitude]):
            return Response({
                "success": False,
                "message": "All required fields must be provided."
            }, status=400)
        
        if not file:
            return Response({"detail": "Luggage Picture is required"}, status=status.HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            return Response({"detail": "file too large"}, status=status.HTTP_400_BAD_REQUEST)

        # build S3 key: documents/{user_id}/{uuid4}_{original_filename}
        ext = file.name.split('.')[-1] if '.' in file.name else ''
        key = f"luggage/{user_id}/{uuid.uuid4().hex}"
        if ext:
            key = f"{key}.{ext}"

        try:
            # Save file to configured storage (S3 if DEFAULT_FILE_STORAGE uses S3Boto3Storage)
            content = ContentFile(file.read())
            saved_path = default_storage.save(key, content)

            # Get public or signed URL depending on your storage config
            file_url = default_storage.url(saved_path)
        except Exception as e:
        # log exception in real app
            return Response({"success": "Fail", "message": str(e)}, status=500)

        try:
            user = User.objects.get(id=user_id)

            is_document_verified = UserDocument.objects.filter(user=user).exists()
            if not is_document_verified:
                return Response({"success": False, "message": "User documents not available."}, status=404)
            storage_unit = StorageUnit.objects.get(id=storage_unit_id)

            booking_id = get_next_bag_id()
            booking_type='Hourly' 

            if not luggage_time:
                luggage_time = MAX_BOOKING_TIME

            start_time_str = datetime.fromisoformat(start_time) 
            booking_end_time = compute_booking_end_time(start_time, luggage_time)

            diff = booking_end_time - start_time_str
            total_hours = diff.total_seconds() / 3600

            total_amount = Decimal(storage_unit.price_per_hour) * Decimal(total_hours)
            total_amount = round(total_amount)

            booking = StorageBooking.objects.create(
                user_booked=user,
                storage_unit=storage_unit,
                booking_id=booking_id,
                booking_type=booking_type,
                booking_created_time=start_time,
                booking_end_time=booking_end_time,
                status='confirmed',
                is_active=True,
                storage_booked_location=storage_booked_location,
                user_remark=user_remark,
                amount=total_amount,
                storage_latitude=latitude,
                storage_image_url=file_url,
                storage_longitude=longitude,
                updated_at=start_time
            )

            if addons_param:
                addon_ids = parse_addons_param(addons_param)
                with transaction.atomic():
                    for addon_id in addon_ids:
                        try:
                            addon_instance = Addon.objects.get(id=addon_id)
                            addons_booking = BookingAddon.objects.create(
                            booking=booking,
                            addon=addon_instance
                        )
                        except Exception as e:
                            return Response({"success": "Fail", "message": str(e)}, status=500) 
        except Exception as e:
            return Response({"success": "Fail", "message": str(e)}, status=500)
        
        booking_history = BookingStatusHistory.objects.create(
            booking=booking,
            booking_confirmed=True,
            booking_confirmed_at=timezone.now())


        # trigger_notification_to_saathi(bookingid=booking.id)
        token = UserDeviceToken.objects.filter(user=user).first()
        body = f"Awesome {user.full_name}! Your booking is all set. Drop your item at the nearest Saathi point."
        asyncio.run(send_ayncpush_notification(token.token,'Booking Confirmed', body))

        return Response({
            "success": True,
            "message": "Storage booked successfully.",
            "data": {
                "id": booking.id,
                "booking_id": booking.booking_id,
                "storage_title": storage_unit.title,
                "storage_id": storage_unit.id,
                "start_time": booking.booking_created_time,
                "end_time": booking.booking_end_time,
                "status": booking.status,
                'storage_image_url': booking.storage_image_url,
                "amount": booking.amount,
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
            } if booking.user_booked else [],
            "assigned_saathi": {
                "id": booking.assigned_saathi.id,
                "full_name": booking.assigned_saathi.full_name,
                "email": booking.assigned_saathi.email,
                "phone": booking.assigned_saathi.phone,
            } if booking.assigned_saathi else [],
            "luggage_rakshak": {
                "id": booking.luggage_rakshak.id,
                "full_name": booking.luggage_rakshak.full_name,
                "email": booking.luggage_rakshak.email,
                "phone": booking.luggage_rakshak.phone,
            } if booking.luggage_rakshak else [],
            "storage_unit": {
                "id": booking.storage_unit.id,
                "title": booking.storage_unit.title,
                "address": booking.storage_unit.address,
                "city": booking.storage_unit.city,
                "price_per_hour": str(booking.storage_unit.price_per_hour),
                "price_per_km": str(booking.storage_unit.price_per_km),
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
    data = request.data
    user_id = data.get("saathi_id")
    status = data.get("status")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"success": False, "message": "User not found."}, status=404)

    if user.role != 'saathi':
        return Response({"success": False, "message": "Only saathi can access this API."}, status=403)

    booking_id = request.data.get('booking_id')
    confirmed_weight = request.data.get('confirmed_weight')
    luggage_images = request.data.get('luggage_images')  # Should be list of base64 strings

    if status=='taking_pickup':
        if not booking_id or not confirmed_weight or not luggage_images:
            return Response({"success": False, "message": "booking_id, confirmed_weight, and luggage_images are required."}, status=400)

    try:
        booking = StorageBooking.objects.get(id=booking_id)
    except StorageBooking.DoesNotExist:
        return Response({"success": False, "message": "Booking not found or not assigned to you."}, status=404)

    if booking.status != 'active':
        return Response({"success": False, "message": f"Cannot pick up luggage. Current status: {booking.status}"}, status=400)

    if status=='taking_pickup':
        # Process and save images
        image_urls = []
        for index, image_base64 in enumerate(luggage_images):
            try:
                format, imgstr = image_base64.split(';base64,') 
                ext = format.split('/')[-1]
                file_name = f"luggage_{booking.booking_id}_{index}_{uuid.uuid4()}.{ext}"

                # Save file to Django FileField or custom storage logic
                # decoded_file = ContentFile(base64.b64decode(imgstr), name=file_name)
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
    elif status=='out_for_delivery':
        booking.status = 'out_for_delivery'

    booking.assigned_saathi = user_id
    booking.save()

    return Response({
        "success": True,
        "message": "Pickup confirmed and luggage status updated to 'pickup'.",
        "data": {
            "id": booking.id,
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

    trigger_notification_to_saathi_return(bookingid=booking.id)

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

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_delivery(request):
    data = request.data
    saathi_id = data.get("saathi_id")
    luggage_id = data.get("luggage_id")
    status = data.get("status")

    try:
        booking = StorageBooking.objects.get(booking_id=luggage_id)
    except StorageBooking.DoesNotExist:
        return Response({"success": False, "message": "Booking not found."}, status=404)
    
    saathi_ins = Saathi.objects.filter(id=saathi_id).first()
    
    if booking.status=='delivered':
        return Response({"success": False, "message": "Luggage is already delivered!."}, status=400)
    
    if status =='reached_destination':
        send_push_notification_to_user_for_delivery_arrived(saathi_id=saathi_id, user_id=booking.user_booked.id , status='reached_destination')
        booking.status = 'luggage_reached'
    else:
        send_push_notification_to_user_for_delivery_arrived(saathi_id=saathi_id, user_id=booking.user_booked.id)
        booking.status == 'complete'
        saathi_ins.is_available = True
        saathi_ins.save()

    booking.save()

    return Response({
        "success": True,
        "message": "Delievry Validated"
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def booking_details(request):
    user_id = request.query_params.get('user_id')  # Get from URL params
    storage_instances = StorageBooking.objects.filter(user_booked=user_id).order_by('-created_at')

    if not storage_instances.exists():
        return Response({
            "success": False,
            "message": "No luggage found for this user.",
            "data": []
        }, status=404)

    data = []
    for s in storage_instances:
        data.append({
            "id": str(s.id),
            "type": return_type(s.status),
            "storageId": s.storage_unit.id if s.storage_unit.id else "",
            "serviceName": s.storage_unit.title if s.storage_unit else "",
            "providerName": s.storage_unit.address if s.storage_unit else "",
            "date": localtime(s.booking_created_time).strftime("%Y-%m-%d") if s.booking_created_time else "",
            "time": localtime(s.booking_created_time).strftime("%I:%M %p") if s.booking_created_time else "",
            "location": s.storage_booked_location,
            "price": s.amount,
            "status": return_status(s.status),
            "bookingNumber": s.booking_id,
            "latitude": s.storage_latitude,
            "longitude": s.storage_longitude,
        })

    return Response({
        "success": True,
        "message": "Luggage Found!",
        "data": data
    }, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def booking_status(request):
    storage_id = request.query_params.get('storage_id')

    storage_instance = BookingStatusHistory.objects.filter(
        booking__id=storage_id
    ).first()

    if not storage_instance:
        return Response({
            "success": False,
            "message": "No luggage found for this ID.",
            "data": []
        }, status=404)

    data = {
        "id": storage_instance.id,
        "booking_confirmed": storage_instance.booking_confirmed,
        "booking_confirmed_at": storage_instance.booking_confirmed_at,
        "luggage_stored": storage_instance.luggage_stored,
        "luggage_stored_at": storage_instance.luggage_stored_at,
        "payment_completed": storage_instance.payment_completed,
        "payment_completed_at": storage_instance.payment_completed_at,
        "booking_completed": storage_instance.booking_completed,
        "booking_completed_at": storage_instance.booking_completed_at,
        "booking_cancelled": storage_instance.booking_cancelled,
        "booking_cancelled_at": storage_instance.booking_cancelled_at,
    }

    return Response({
        "success": True,
        "message": "Luggage Found!",
        "data": data
    })


@api_view(['PATCH'])
@permission_classes([AllowAny])
def change_status(request):
    storage_id = request.data.get('storage_id')
    status = request.data.get('status')
    updatedby = request.data.get('updatedby')
    storage_instance = StorageBooking.objects.get(id=storage_id)

    updatedby_instance = Saathi.objects.filter(id=updatedby).first()

    if not storage_instance:
        return Response({
            "success": False,
            "message": "No luggage found for this ID.",
            "data": []
        }, status=404)
    
    storage_instance.status = status
    storage_instance.last_updated_by = updatedby_instance.full_name if updatedby_instance else None
    storage_instance.updated_at = timezone.now()
    storage_instance.save(update_fields=['status', 'last_updated_by', 'updated_at'])

    booking_history = BookingStatusHistory.objects.filter(booking=storage_instance).first()
    if booking_history:
        if status == 'cancelled':
            booking_history.booking_cancelled = True
            booking_history.booking_cancelled_at = timezone.now()
        elif status == 'completed':
            booking_history.booking_completed = True
            booking_history.booking_completed_at = timezone.now()
        elif status == 'luggage_Stored':
            booking_history.luggage_stored = True
            booking_history.luggage_stored_at = timezone.now()
        elif status == 'payment_completed':
            booking_history.payment_completed = True
            booking_history.payment_completed_at = timezone.now()
        booking_history.save()

    return Response({
        "success": True,
        "message": "Status Updated Successfully!"})

@api_view(['PATCH'])
@permission_classes([AllowAny])
def change_amount(request):
    storage_id = request.data.get('storage_id')
    amount = request.data.get('amount')
    updatedby = request.data.get('updatedby')
    storage_instance = StorageBooking.objects.get(id=storage_id)

    updatedby_instance = Saathi.objects.filter(id=updatedby).first()

    if not storage_instance:
        return Response({
            "success": False,
            "message": "No luggage found for this ID.",
            "data": []
        }, status=404)
    
    storage_instance.amount = amount
    storage_instance.amount_updated_by = updatedby_instance.full_name if updatedby_instance else None
    storage_instance.updated_at = timezone.now()
    storage_instance.save(update_fields=['amount', 'amount_updated_by','updated_at'])

    paymentInstance = Payment.objects.filter(booking=storage_instance).first()
    if paymentInstance:
        paymentInstance.amount = amount
        paymentInstance.save(update_fields=['amount'])

    return Response({
        "success": True,
        "message": "Amount Updated Successfully!"})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_bookings(request):
    booking_id = request.GET.get('booking_id')

    # Optimized query: one-shot load of related data
    queryset = (
        StorageBooking.objects.select_related(
            'user_booked', 'storage_unit', 'assigned_saathi', 'luggage_rakshak'
        )
        .prefetch_related(
            Prefetch(
                'user_booked__user_documents',
                queryset=UserDocument.objects.only('id', 'original_name', 'imghippo_url', 'created_at')
            )
        )
        .order_by('-created_at')
    )

    if booking_id:
        queryset = queryset.filter(booking_id__icontains=booking_id)

    data = []
    for booking in queryset:
        user = booking.user_booked
        user_docs = user.user_documents.all() if hasattr(user, 'user_documents') else []

        data.append({
            "id": booking.id,
            "booking_id": booking.booking_id,
            "status": booking.status,
            "booking_type": booking.booking_type,
            "booking_created_time": booking.booking_created_time,
            "booking_end_time": booking.booking_end_time,
            "amount": booking.amount,
            "storage_booked_location": booking.storage_booked_location,
            "storage_unit": booking.storage_unit.title if booking.storage_unit else None,
            "assigned_saathi": getattr(booking.assigned_saathi, "name", None),
            'luggage_image': booking.storage_image_url if booking.storage_image_url else None,
            "updated_by": booking.last_updated_by if booking.last_updated_by else None,
            "amount_updated_by": booking.amount_updated_by if booking.amount_updated_by else None,
            "user_booked": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "city_name": user.city_name,
                "profile_picture": user.profile_picture,
                "latitude": user.latitude,
                "longitude": user.longitude,
                "documents": [
                    {
                        "id": doc.id,
                        "original_name": doc.original_name,
                        "imghippo_url": doc.imghippo_url,
                        "created_at": doc.created_at,
                    } for doc in user_docs
                ]
            }
        })

    return Response({
        "success": True,
        "message": "Luggage List Returned successfully!",
        "data": data})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_detail_bookings(request):
    booking_id = request.GET.get('booking_id')

    booking = StorageBooking.objects.filter(id=booking_id).first()
    if not booking:
        return Response({
            "success": False,
            "message": "No luggage details found for this ID.",
            "data": None
        }, status=404)

    data = {
        "storage_unit": {
            "longitude": booking.storage_unit.longitude,
            "latitude": booking.storage_unit.latitude,
            "name": booking.storage_unit.title,
        },
        "booking_number": booking.booking_id,
    }

    return Response({
        "success": True,
        "message": "Booking details returned successfully.",
        "data": data
    })
