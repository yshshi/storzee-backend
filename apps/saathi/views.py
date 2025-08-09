from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.saathi.models import Saathi
from apps.storage_bookings.models import StorageBooking

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