# from django.shortcuts import render
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from apps.storage_bookings.models import StorageBooking
# from apps.users.models import User
# from apps.storage_units.models import StorageUnit
# from .utils import calculate_distance_km,create_razorpay_order,confirm_razorpay_payment
# from apps.wallet.models import UserWallet
# from apps.payment.models import Payment
# from rest_framework.serializers import ValidationError
# from rest_framework import status

# Create your views here.

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def calculate_return_payment(request):
#     userId = request.data.get("user_id")
#     user = User.objects.filter(id=userId).first()
#     if not user:
#         return Response({'error': 'User does not exist.'}, status=400)
#     booking_id = request.data.get('booking_id')

#     if not booking_id or not userId:
#         return Response({'error': 'Booking ID and user id is required.'}, status=400)
    
    
#     booking = StorageBooking.objects.get(id=request.data.get("booking_id"), user_booked=user)
#     if not booking:
#         return Response({"success": False, "message": "Booking not found."}, status=404)
    
#     distance_km = calculate_distance_km(float(booking.storage_unit.latitude), float(booking.storage_unit.longitude), float(booking.return_lat), float(booking.return_lng))

#     # price details 
#     storage_unit_instance = StorageUnit.objects.filter(id=booking.storage_unit.id).first()
#     # Estimate amount: ₹50 base + ₹10/km
#     estimated_amount = int(storage_unit_instance.price_per_hour) + (int(storage_unit_instance.price_per_km) * distance_km)
#     estimated_amount = round(estimated_amount)

#     return Response({
#             'amount': estimated_amount,
#             'distance': distance_km
#         })

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def initiate_return_payment(request):
#     userId = request.data.get("user_id")
#     user = User.objects.filter(id=userId).first()
#     if not user:
#         return Response({'error': 'User does not exist.'}, status=400)
#     data = request.data
#     booking_id = data.get('booking_id')
#     payment_method = data.get('payment_method')
#     wallet_amount = float(data.get('wallet_amount', 0))
#     amount = float(data.get('amount', 0))

#     if not booking_id or not payment_method:
#         return Response({'error': 'Booking ID and payment method required.'}, status=400)

#     booking = get_object_or_404(StorageBooking, id=booking_id, user_booked=user)

#     if booking.status in ['completed', 'cancelled']:
#         return Response({'error': 'Return cannot be initiated for current booking status.'}, status=400)

#     total_return_amount = amount

#     # Validate wallet balance
#     wallet_instance =  UserWallet.objects.filter(user=user).first()
#     wallet_balance = wallet_instance.balance
#     used_wallet = 0
#     remaining_amount = total_return_amount

#     if payment_method == 'wallet':
#         if wallet_balance < total_return_amount:
#             return Response({'error': 'Insufficient wallet balance.'}, status=400)
#         user.wallet_balance -= total_return_amount
#         user.save()
#         booking.status = 'return_payment_done'
#         booking.save()
#         return Response({'status': 'paid_via_wallet', 'booking_id': booking_id})

#     elif payment_method == 'wallet+razorpay':
#         if wallet_balance > 0:
#             used_wallet = min(wallet_balance, total_return_amount)
#             user.wallet_balance -= used_wallet
#             user.save()
#             remaining_amount = total_return_amount - used_wallet
#         # continue to Razorpay below

#     if payment_method in ['razorpay', 'wallet+razorpay']:
#         try:
#             razorpay_order = create_razorpay_order(amount=remaining_amount)

#             body = {
#                 'user':user,
#                 'booking': booking,
#                 'razorpay_order_id': razorpay_order.get("id"),
#                 'amount': amount,
#                 'status': 'Initated',
#                 'payment_method': payment_method,
#                 'raw_response_from_razorpay': razorpay_order
#             }

#             payment__created = Payment.objects.create(**body)
#             return Response({
#                 'status': status.HTTP_200_OK,
#                 'message': 'Payment Order Created Succeefully !',
#                 'payment_id': payment__created.id,
#                 'razorpay_order': razorpay_order,
#             })
#         except Exception as e:
#             raise ValidationError({
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": e
#             })

#     return Response({'error': 'Invalid payment method.'}, status=400)

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def razor_payment_confirm(request):
#     userId = request.data.get("user_id")
#     user = User.objects.filter(id=userId).first()
#     if not user:
#         return Response({'error': 'User does not exist.'}, status=400)
#     data = request.data
#     payment_id = data.get('payment_id')
#     razorpay_payment_id = data.get('razorpay_payment_id')
#     razorpay_signature = data.get('razorpay_signature')

#     if not all([userId, payment_id, razorpay_payment_id, razorpay_signature]):
#         return Response({"success": False, "message": "All feilds details are required."}, status=400)
    
#     try:
#         payment_instance = Payment.objects.filter(id=payment_id).first()
#         if payment_instance.status in ['success', 'failed']:
#             return Response({'error': 'Return cannot be initiated for current booking status.'}, status=400)
        
#         razorpay_order_id = payment_instance.razorpay_order_id
#         razorpay_order = confirm_razorpay_payment(razorpay_order_id=razorpay_order_id,razorpay_payment_id=razorpay_payment_id,razorpay_signature=razorpay_signature)

#         if razorpay_order.get("success") == True:

#             payment_instance.razorpay_payment_id = razorpay_payment_id
#             payment_instance.razorpay_signature = razorpay_signature
#             payment_instance.status = 'Success'
#             payment_instance.save()

#             return Response({
#                 'status': status.HTTP_200_OK,
#                 'message': 'Payment Verified Succeefully !',
#                 'payment_id': payment_instance.id,
#             })
        
#         else:
#             payment_instance.status = 'Failed'
#             payment_instance.save()

#             return Response({
#                 'status': status.HTTP_400_BAD_REQUEST,
#                 'message': 'Payment Verified Failed !',
#                 'payment_id': payment_instance.id,
#             })
#     except Exception as e:
#         raise ValidationError({
#             "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#             "message": e
#         })

import json
import hmac
import hashlib
from decimal import Decimal

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

import razorpay
import environ

from apps.users.models import User,UserDeviceToken , UserNotification
from apps.storage_bookings.models import StorageBooking , BookingStatusHistory
from apps.payment.models import Payment  # adjust import path if needed
from apps.wallet.models import UserWallet  # if you have this model, else remove wallet handling
env = environ.Env()
environ.Env.read_env()
from apps.payment.utils import generate_receipt_number
from django.views.decorators.csrf import csrf_exempt
from apps.storage_units.models import StorageUnit ,Addon
from apps.storage_bookings.models import BookingAddon
from django.utils import timezone
from utils.trigger_notiifcation import send_ayncpush_notification
from apps.users.models import UserDeviceToken
import asyncio


# Initialize Razorpay client
RZP_CLIENT = razorpay.Client(auth=(
    env("RAZORPAY_ID"),
    env("RAZORPAY_SECERT")  # fixed spelling from SECERT → SECRET
))

def _create_razorpay_order(amount_in_rupees, receipt=None, notes=None):
    """
    Create razorpay order and return dict. Amount must be Decimal/float in rupees.
    """
    if Decimal(amount_in_rupees) <= 0:
        raise ValidationError({"message": "Amount must be > 0", "status": status.HTTP_400_BAD_REQUEST})

    amount_paise = int(Decimal(amount_in_rupees) * 100)
    payload = {
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
    }
    if receipt:
        payload["receipt"] = receipt
    if notes:
        payload["notes"] = notes

    order = RZP_CLIENT.order.create(payload)
    if order.get("status") != "created":
        raise ValidationError({"message": "Failed to create razorpay order", "detail": order}, code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Normalize return
    return {
        "id": order.get("id"),
        "entity": order.get("entity"),
        "amount": Decimal(amount_in_rupees),
        "currency": order.get("currency"),
        "receipt": order.get("receipt"),
        "status": order.get("status"),
        "raw": order
    }


def _verify_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    HMAC SHA256 verification. Returns True/False.
    """
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return False
    msg = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
    expected = hmac.new(env("RAZORPAY_SECERT").encode(), msg, hashlib.sha256).hexdigest()
    return expected == razorpay_signature


@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_return_payment(request):
    """
    POST data expected:
    {
      "user_id": int,
      "booking_id": int,
      "payment_method": "wallet" | "razorpay" | "wallet+razorpay",
      "amount": decimal (total return amount),
      "wallet_amount": optional decimal (client-sent intended wallet use; server still validates balance)
    }
    Response on Razorpay: returns hosted_checkout_url and payment_id (db)
    """
    data = request.data
    user_id = data.get("user_id")
    booking_id = data.get("booking_id")
    payment_method = data.get("payment_method")
    total_amount = Decimal(str(data.get("amount", "0") or "0"))
    wallet_amount_requested = Decimal(str(data.get("wallet_amount", "0") or "0"))

    if not user_id or not booking_id or not payment_method:
        return Response({"error": "user_id, booking_id and payment_method are required"}, status=400)

    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User does not exist."}, status=400)

    booking = get_object_or_404(StorageBooking, id=booking_id, user_booked=user)

    if booking.status in ['completed', 'cancelled', 'return_payment_done']:
        return Response({'error': 'Return cannot be initiated for current booking status.'}, status=400)

    # Wallet handling
    used_wallet = Decimal("0")
    remaining_amount = total_amount
    try:
        wallet = UserWallet.objects.filter(user=user).first()
        wallet_balance = Decimal(str(wallet.balance)) if wallet else Decimal("0")
    except Exception:
        wallet = None
        wallet_balance = Decimal("0")

    if payment_method == 'wallet':
        if wallet_balance < total_amount:
            return Response({'error': 'Insufficient wallet balance.'}, status=400)
        # deduct wallet
        wallet.balance = wallet_balance - total_amount
        wallet.save()
        payment = Payment.objects.create(
            user=user,
            booking=booking,
            amount=total_amount,
            currency='INR',
            status='success',
            payment_method='wallet',
            raw_response_from_razorpay=f"paid_via_wallet:{total_amount}"
        )
        booking.status = 'payment_complete'
        booking.save()
        return Response({'status': 'paid_via_wallet', 'payment_id': payment.id})

    if payment_method == 'wallet+razorpay':
        # use as much wallet as possible up to requested wallet_amount
        if wallet_balance > 0 and wallet_amount_requested > 0:
            used_wallet = min(wallet_balance, wallet_amount_requested, total_amount)
            # deduct wallet now
            wallet.balance = wallet_balance - used_wallet
            wallet.save()
            remaining_amount = total_amount - used_wallet
        else:
            remaining_amount = total_amount

    if payment_method in ['razorpay', 'wallet+razorpay']:
        if remaining_amount <= 0:
            # everything covered by wallet
            payment = Payment.objects.create(
                user=user,
                booking=booking,
                amount=total_amount,
                currency='INR',
                status='success',
                payment_method=payment_method,
                raw_response_from_razorpay=f"paid_via_wallet:{used_wallet}"
            )
            booking.status = 'payment_complete'
            booking.save()
            return Response({'status': 'paid_via_wallet', 'payment_id': payment.id})

        # create razorpay order for remaining_amount
        try:
            receipt = generate_receipt_number()
            rzp_order = _create_razorpay_order(amount_in_rupees=remaining_amount, receipt=receipt, notes={"booking_id": str(booking.id), "user_id": str(user.id), "test": "return_payment"})
            payment = Payment.objects.create(
                user=user,
                booking=booking,
                amount=total_amount,
                currency='INR',
                status='initated',   # matches Payment.STATUS_CHOICES: 'initated'
                payment_method=payment_method,
                razorpay_order_id=rzp_order.get("id"),
                raw_response_from_razorpay=json.dumps(rzp_order.get("raw")),
            )
            # hosted_url = request.build_absolute_uri(reverse('payment:hosted_checkout', args=[payment.id]))
            frontend_payment_url = (
                f"https://api-dev.thestorezee.com/utils/pay.html?"
                f"payment_id={payment.id}"
                f"&order_id={payment.razorpay_order_id}"
                f"&amount={payment.amount}"
            )
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'Payment Order Created Successfully',
                'payment_id': payment.id,
                'razorpay_order': rzp_order,
                'frontend_payment_url': frontend_payment_url
            })
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'error': 'Invalid payment method.'}, status=400)


def hosted_checkout(request, payment_id):
    """
    GET endpoint that renders the Razorpay checkout page with server-injected order_id and key_id.
    React Native WebView should open this URL.
    """
    payment = get_object_or_404(Payment, id=payment_id)
    if not payment.razorpay_order_id:
        return HttpResponse("Missing razorpay order id for this payment", status=400)
    
    verify_url = request.build_absolute_uri(reverse('payment:verify_return_payment'))

    context = {
        "key_id": env("RAZORPAY_ID"),
        "order_id": payment.razorpay_order_id,
        "payment_db_id": payment.id,
        "amount": str(payment.amount),
        "verify_url": verify_url,
    }
    # render template 'payments/razorpay_hosted_checkout.html'
    return render(request, "payments/razorpay_hosted_checkout.html", context)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_return_payment(request):
    """
    Endpoint to be called by RN after checkout success or from hosted page.
    Body:
    {
      "razorpay_order_id": "order_xxx",
      "razorpay_payment_id": "pay_xxx",
      "razorpay_signature": "signature",
      "payment_db_id": <int>
    }
    """
    data = request.data
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")
    payment_db_id = data.get("payment_db_id")

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, payment_db_id]):
        return Response({'error': 'missing parameters'}, status=400)

    payment = get_object_or_404(Payment, id=payment_db_id)

    # idempotency: if already success
    if payment.status == 'success':
        return Response({'status': 'already_paid', 'payment_id': payment.id})

    # verify signature
    valid = _verify_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)
    if not valid:
        payment.status = 'failed'
        payment.raw_response_from_razorpay = (payment.raw_response_from_razorpay or "") + f"\nverification_failed:{json.dumps(data)}"
        payment.save()
        return Response({'status': 'invalid_signature'}, status=400)

    # optionally verify with Razorpay API that payment exists and is captured
    try:
        rzp_payment = RZP_CLIENT.payment.fetch(razorpay_payment_id)
        # ensure captured && link to order
        if rzp_payment.get("status") not in ("captured", "authorized", "captured_with_masked_card"):
            payment.status = 'failed'
            payment.raw_response_from_razorpay = (payment.raw_response_from_razorpay or "") + f"\nunexpected_payment_status:{rzp_payment}"
            payment.save()
            return Response({'status': 'payment_not_captured', 'detail': rzp_payment}, status=400)
    except Exception as e:
        # log but allow HMAC verification to be primary check
        payment.raw_response_from_razorpay = (payment.raw_response_from_razorpay or "") + f"\nfetch_error:{str(e)}"
        payment.status = 'failed'
        payment.save()
        return Response({'status': 'payment_failed', 'detail': rzp_payment}, status=500)

    # mark payment success
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.status = 'success'
    payment.save()

    # update booking status (idempotent)
    booking = payment.booking
    booking.status = 'return_payment_done'
    booking.save()

    booking_history = BookingStatusHistory.objects.filter(booking=booking).first()
    if booking_history:
        booking_history.payment_completed = True
        booking_history.payment_completed_at = timezone.now()
        booking_history.save()

    token = UserDeviceToken.objects.filter(user=payment.user).first()
    title = '💳 Payment Received'
    body = f"🙏 Thanks {payment.booking.user_booked.full_name}! Your payment has been successfully received. We appreciate your trust in us."
    asyncio.run(send_ayncpush_notification(token.token,title, body))

    data = {
            'user': payment.booking.user_booked,
            'title': 'Payment',
            'message': body,
            'type': 'Payment',
            'isRead': False,
            'priority': 'Medium',
            'actionRequired': False
        }

    dataInserted = UserNotification.objects.create(**data)

    return Response({'status': 'ok', 'payment_id': payment.id, 'booking_id': payment.booking.id, 'user': payment.user.id})

@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_return_payment(request):
    data = request.data
    booking_id = data.get("booking_id")

    if not booking_id:
        return Response({'error': 'booking_id is required'}, status=400)
    booking = StorageBooking.objects.filter(id=booking_id).first()
    if not booking:
        return Response({"success": False, "message": "Booking not found."}, status=404)    
    
    if booking.status in ['completed', 'cancelled']:
        return Response({'error': 'Return cannot be initiated for current booking status.'}, status=400)
    
    # storageInstance = booking.storage_unit

    start = booking.booking_created_time
    end = booking.booking_end_time

    diff = end - start
    total_hours = diff.total_seconds() / 3600

    # total_amount = Decimal(storageInstance.price_per_hour) * Decimal(total_hours)
    # total_amount = round(total_amount)

    addons = BookingAddon.objects.filter(booking=booking).select_related("addon")
    addon_total = Decimal(0)

    if not addons.exists():
        addon_total = Decimal(booking.storage_unit.price_per_hour) * Decimal(total_hours)
        addon_total = round(addon_total)
    for item in addons:
        addon_price = Decimal(item.addon.base_price)
        addon_amount = addon_price * Decimal(total_hours)
        addon_total += addon_amount

    booking.amount = addon_total
    booking.save(update_fields=['amount'])

    paymentInstance = Payment.objects.filter(booking=booking).first()
    if paymentInstance:
        paymentInstance.amount = addon_total
        paymentInstance.save(update_fields=['amount'])

    return Response({
            'amount': addon_total,
            'hours': total_hours
        })