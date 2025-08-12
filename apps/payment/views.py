from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.storage_bookings.models import StorageBooking
from apps.users.models import User
from apps.storage_units.models import StorageUnit
from .utils import calculate_distance_km,create_razorpay_order,confirm_razorpay_payment
from apps.wallet.models import UserWallet
from apps.payment.models import Payment
from rest_framework.serializers import ValidationError
from rest_framework import status

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_return_payment(request):
    userId = request.data.get("user_id")
    user = User.objects.filter(id=userId).first()
    if not user:
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
@permission_classes([AllowAny])
def initiate_return_payment(request):
    userId = request.data.get("user_id")
    user = User.objects.filter(id=userId).first()
    if not user:
        return Response({'error': 'User does not exist.'}, status=400)
    data = request.data
    booking_id = data.get('booking_id')
    payment_method = data.get('payment_method')
    wallet_amount = float(data.get('wallet_amount', 0))
    amount = float(data.get('amount', 0))

    if not booking_id or not payment_method:
        return Response({'error': 'Booking ID and payment method required.'}, status=400)

    booking = get_object_or_404(StorageBooking, id=booking_id, user_booked=user)

    if booking.status in ['completed', 'cancelled']:
        return Response({'error': 'Return cannot be initiated for current booking status.'}, status=400)

    total_return_amount = amount

    # Validate wallet balance
    wallet_instance =  UserWallet.objects.filter(user=user).first()
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
        try:
            razorpay_order = create_razorpay_order(amount=remaining_amount)

            body = {
                'user':user,
                'booking': booking,
                'razorpay_order_id': razorpay_order.get("id"),
                'amount': amount,
                'status': 'Initated',
                'payment_method': payment_method,
                'raw_response_from_razorpay': razorpay_order
            }

            payment__created = Payment.objects.create(**body)
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'Payment Order Created Succeefully !',
                'payment_id': payment__created.id,
                'razorpay_order': razorpay_order,
            })
        except Exception as e:
            raise ValidationError({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": e
            })

    return Response({'error': 'Invalid payment method.'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def razor_payment_confirm(request):
    userId = request.data.get("user_id")
    user = User.objects.filter(id=userId).first()
    if not user:
        return Response({'error': 'User does not exist.'}, status=400)
    data = request.data
    payment_id = data.get('payment_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    if not all([userId, payment_id, razorpay_payment_id, razorpay_signature]):
        return Response({"success": False, "message": "All feilds details are required."}, status=400)
    
    try:
        payment_instance = Payment.objects.filter(id=payment_id).first()
        if payment_instance.status in ['success', 'failed']:
            return Response({'error': 'Return cannot be initiated for current booking status.'}, status=400)
        
        razorpay_order_id = payment_instance.razorpay_order_id
        razorpay_order = confirm_razorpay_payment(razorpay_order_id=razorpay_order_id,razorpay_payment_id=razorpay_payment_id,razorpay_signature=razorpay_signature)

        if razorpay_order.get("success") == True:

            payment_instance.razorpay_payment_id = razorpay_payment_id
            payment_instance.razorpay_signature = razorpay_signature
            payment_instance.status = 'Success'
            payment_instance.save()

            return Response({
                'status': status.HTTP_200_OK,
                'message': 'Payment Verified Succeefully !',
                'payment_id': payment_instance.id,
            })
        
        else:
            payment_instance.status = 'Failed'
            payment_instance.save()

            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Payment Verified Failed !',
                'payment_id': payment_instance.id,
            })
    except Exception as e:
        raise ValidationError({
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": e
        })