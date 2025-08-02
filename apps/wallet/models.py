from django.db import models
from django.conf import settings
import uuid

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Wallet - ₹{self.balance}"


class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('topup', 'Top-up'),
        ('booking', 'Booking Payment'),
        ('refund', 'Refund'),
        ('referral_reward', 'Referral Reward'),
        ('cashback', 'Cashback'),
        ('adjustment', 'Manual Adjustment'),
        ('return_payment', 'Return Payment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_credit = models.BooleanField(default=False)  # True = credit, False = debit
    related_booking = models.ForeignKey("storage_bookings.StorageBooking", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        direction = "Credit" if self.is_credit else "Debit"
        return f"{direction} ₹{self.amount} to {self.wallet.user.email} for {self.transaction_type}"