from django.db import models
from apps.meta_app.models import MyBaseModel
from apps.users.models import User

# Create your models here.
class Saathi(MyBaseModel):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="saathi_profile")
    pan_card_number = models.CharField(max_length=10, unique=True)
    aadhaar_card_number = models.CharField(max_length=12, unique=True)
    pan_card_upload_link = models.CharField(max_length=200, unique=True)
    aadhaar_card_upload_link = models.CharField(max_length=200, unique=True)
    vehicle_number = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Saathi"
        verbose_name_plural = "Saathis"

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"