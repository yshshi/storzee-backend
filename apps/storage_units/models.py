from django.db import models
from apps.meta_app.models import MyBaseModel
from apps.users.models import User
import uuid

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


class Addon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class StorageUnitAddon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storage_unit = models.ForeignKey(
        'StorageUnit',
        on_delete=models.CASCADE,
        related_name='storage_unit_addons'
    )
    addon = models.ForeignKey(
        Addon,
        on_delete=models.CASCADE,
        related_name='storage_unit_addons'
    )
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=False) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('storage_unit', 'addon')
        indexes = [
            models.Index(fields=['storage_unit']),
            models.Index(fields=['addon']),
        ]

    def __str__(self):
        return f"{self.addon.name} @ {self.storage_unit.id}"

    @property
    def effective_price(self):
        return self.price_override if self.price_override is not None else self.addon.base_price
    
class StoargeNearbyPlace(models.Model):
    city = models.CharField(max_length=100,blank=True,null=True)
    place_name = models.CharField(max_length=200,blank=True,null=True)
    place_description = models.TextField(blank=True,null=True)
    distance_km = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)