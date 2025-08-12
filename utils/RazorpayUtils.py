import razorpay
import environ
from rest_framework.serializers import ValidationError
from rest_framework import status

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()  # Make sure it reads your .env file

# Initialize Razorpay client
client = razorpay.Client(auth=(
    env("RAZORPAY_ID"),
    env("RAZORPAY_SECERT")  # fixed spelling from SECERT → SECRET
))

class RazorpayClient:
    def create_order(amount, currency="INR", receipt=None, notes=None):
        """
        Creates a Razorpay order.

        :param amount: Amount in smallest currency unit (paise for INR)
        :param currency: Currency code (default INR)
        :param receipt: Optional receipt number
        :param notes: Optional dict of notes
        """
        data = {
            "amount": amount,  # e.g., ₹500 → 50000 paise
            "currency": currency,
            "payment_capture": 1  # auto-capture payments
        }

        if receipt:
            data["receipt"] = receipt
        if notes:
            data["notes"] = notes

        try:
            order_data =  client.order.create(data)
            return order_data
        except Exception as e:
            print(e)
            raise ValidationError({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": e
            })
        
    def verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verifies Razorpay payment using payment signature and confirms payment status.

        Returns:
            dict: Payment verification result.
        """
        try:
            # Step 1: Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)

            # Step 2: Fetch payment details to ensure status is 'captured'
            payment = client.payment.fetch(razorpay_payment_id)

            if payment.get("status") == "captured":
                return {
                    "status": status.HTTP_200_OK,
                    "success": True,
                    "message": "Payment verified successfully",
                    "payment_details": payment
                }
            else:
                return {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "success": False,
                    "message": f"Payment not successful. Current status: {payment.get('status')}",
                    "payment_details": payment
                }

        except razorpay.errors.SignatureVerificationError:
            raise ValidationError({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid payment signature."
            })
        except Exception as e:
            raise ValidationError({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            })