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

    full_name = models.CharField(max_length=255)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, default='saathi')
    profile_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_picture = models.CharField(max_length=150, null=True, blank=True)
    otp = models.CharField(null=True, blank=True, max_length=7)
    otp_generated_time = models.DateTimeField(auto_now_add=True)
    city_name = models.CharField(max_length=100, null=True, blank=True)
    pan_card_number = models.CharField(max_length=10, unique=True)
    aadhaar_card_number = models.CharField(max_length=12, unique=True)
    pan_card_upload_link = models.TextField(unique=True)
    aadhaar_card_upload_link = models.TextField(unique=True)
    vehicle_number = models.CharField(max_length=20)
    terms_and_condition_agreed = models.BooleanField(default=False)
    document_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Saathi"
        verbose_name_plural = "Saathis"

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"