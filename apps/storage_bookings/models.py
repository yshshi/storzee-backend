from django.db import models
from apps.meta_app.models import MyBaseModel
from apps.users.models import User
from apps.storage_units.models import StorageUnit

# Create your models here.
class StorageBooking(MyBaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('confirmed', 'Confirmed'),
        ('pickup', 'Pickup'),
        ('out_for_delivery', 'Out For Delivery'),
        ('luggage_Stored', 'Luggage Stored'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user_booked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    storage_unit = models.ForeignKey(StorageUnit, on_delete=models.CASCADE, related_name='bookings')
    booking_id = models.CharField(max_length=100, blank=True, null=True)
    booking_type = models.CharField(max_length=10, choices=[('hourly', 'Hourly'), ('daily', 'Daily'), ('others', 'Others')])
    booking_created_time = models.DateTimeField(blank=True, null=True)
    booking_end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    storage_image_url = models.URLField(blank=True, null=True)
    luggage_images = models.JSONField(default=list, blank=True, null=True)
    storage_weight = models.CharField(max_length=100, blank=True, null=True)
    assigned_saathi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saathi', null=True, blank=True)
    luggage_rakshak = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rakshak',null=True,blank=True)
    is_active = models.BooleanField(default=False)
    amount = models.CharField(max_length=10, blank=True, null=True)
    storage_latitude = models.FloatField(default=0.0)
    storage_longitude = models.FloatField(default=0.0)
    storage_booked_location = models.CharField(max_length=100, blank=True, null=True)
    pickup_confirmed_at = models.DateTimeField(blank=True, null=True)
    storage_location_updated_at = models.DateTimeField(blank=True, null=True)
    user_remark = models.CharField(max_length=200, blank=True, null=True)
    delivered_to_rakshak_at = models.DateTimeField(null=True, blank=True)
    return_requested_at = models.DateTimeField(null=True, blank=True)
    return_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    return_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    return_address = models.TextField(null=True, blank=True)
    return_preferred_time = models.DateTimeField(null=True, blank=True)
    return_estimated_amount = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.full_name} → {self.storage_unit.title} [{self.status}]"
    

class BookingFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(StorageBooking, on_delete=models.CASCADE, related_name='feedbacks')
    storage_unit = models.ForeignKey(StorageUnit, on_delete=models.CASCADE)
    
    rating = models.IntegerField()  # Range 1–5
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating}/5 by {self.user.full_name} for {self.storage_unit.title}"
