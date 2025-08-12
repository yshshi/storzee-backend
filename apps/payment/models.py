from django.db import models
from apps.users.models import User
from apps.storage_bookings.models import StorageBooking

# Create your models here.
class Payment(models.Model):
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('initated', 'Initated'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    booking = models.ForeignKey(StorageBooking, on_delete=models.CASCADE, related_name="payments")
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # amount in INR
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Initated')

    payment_method = models.CharField(max_length=255, blank=True, null=True)

    raw_response_from_razorpay = models.TextField(null=True,blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency} ({self.status})"