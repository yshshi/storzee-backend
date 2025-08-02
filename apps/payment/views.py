from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from storage_bookings.models import StorageBooking
from apps.users.models import User
from apps.storage_units.models import StorageUnit
from .utils import calculate_distance_km,create_razorpay_order
from apps.wallet.models import Wallet

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_return_payment(request):
    userId = request.user.get("user_id")
    user = User.objects.filter(id=userId).first()
    if user.DoesNotExist:
        return Response({'error': 'User does not exist.'}, status=400)
    booking_id = request.data.get('booking_id')

    if not booking_id or not userId:
        return Response({'error': 'Booking ID and user id is required.'}, status=400)
    
    try:
        booking = StorageBooking.objects.get(booking_id=request.data.get("booking_id"), user_booked=user)
    except StorageBooking.DoesNotExist:
        return Response({"success": False, "message": "Booking not found."}, status=404)
    
    distance_km = calculate_distance_km(float(booking.storage_unit.latitude), float(booking.storage_unit.longitude), float(booking.return_lat), float(booking.return_lng))

    # price details 
    storage_unit_instance = StorageUnit.objects.filter(id=booking.storage_unit).first()
    # Estimate amount: ₹50 base + ₹10/km
    estimated_amount = int(storage_unit_instance.price_per_hour) + (int(storage_unit_instance.price_per_km) * distance_km)
    estimated_amount = round(estimated_amount)

    return Response({
            'amount': estimated_amount,
            'distance': distance_km
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_return_payment(request):
    userId = request.user.get("user_id")
    user = User.objects.filter(id=userId).first()
    if user.DoesNotExist:
        return Response({'error': 'User does not exist.'}, status=400)
    data = request.data
    booking_id = data.get('booking_id')
    payment_method = data.get('payment_method')
    wallet_amount = float(data.get('wallet_amount', 0))
    amount = float(data.get('amount', 0))

    if not booking_id or not payment_method:
        return Response({'error': 'Booking ID and payment method required.'}, status=400)

    booking = get_object_or_404(StorageBooking, booking_id=booking_id, user_booked=user)

    if booking.status not in ['luggage_Stored', 'confirmed']:
        return Response({'error': 'Return cannot be initiated for current booking status.'}, status=400)

    total_return_amount = amount

    # Validate wallet balance
    wallet_instance =  Wallet.objects.filter(user=user).first()
    wallet_balance = wallet_instance.balance
    used_wallet = 0
    remaining_amount = total_return_amount

    if payment_method == 'wallet':
        if wallet_balance < total_return_amount:
            return Response({'error': 'Insufficient wallet balance.'}, status=400)
        user.wallet_balance -= total_return_amount
        user.save()
        booking.status = 'return_payment_done'
        booking.save()
        return Response({'status': 'paid_via_wallet', 'booking_id': booking_id})

    elif payment_method == 'wallet+razorpay':
        if wallet_balance > 0:
            used_wallet = min(wallet_balance, total_return_amount)
            user.wallet_balance -= used_wallet
            user.save()
            remaining_amount = total_return_amount - used_wallet
        # continue to Razorpay below

    if payment_method in ['razorpay', 'wallet+razorpay']:
        razorpay_order = create_razorpay_order(amount=remaining_amount, booking=booking)
        return Response({
            'status': 'payment_pending',
            'payment_method': payment_method,
            'wallet_used': used_wallet,
            'razorpay_order': razorpay_order,
            'amount_due': remaining_amount
        })

    return Response({'error': 'Invalid payment method.'}, status=400)