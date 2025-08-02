from django.db import models
from apps.meta_app.models import MyBaseModel
from apps.users.models import User

# Create your models here.

class StorageUnit(MyBaseModel):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='storage_units'
    )
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    capacity = models.IntegerField(help_text="Max bags", blank=True, null=True)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    price_per_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    rating = models.FloatField(default=0.0)

    benefits = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.owner.full_name}"
    
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    storage_unit = models.ForeignKey('StorageUnit', on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField()  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} by {self.user.full_name}"
    
class StorageImage(models.Model):
    storage_unit = models.ForeignKey(StorageUnit, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.storage_unit.title}"
