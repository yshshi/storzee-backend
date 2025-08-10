from django.db import models  
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from apps.meta_app.models import MyBaseModel

USER_ROLES = (
    ('user', 'User'),
    ('shathi', 'Shathi'),
    ('locker_owner', 'Locker Owner'),
    ('admin', 'Admin'),
)

class UserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, role='user', **extra_fields):
        if not email and not phone:
            raise ValueError('User must have an email or phone number')

        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone=None, password=None):
        user = self.create_user(
            email=email,
            phone=phone,
            password=password,
            role='admin',
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(MyBaseModel, AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='user')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_picture = models.CharField(max_length=150, null=True, blank=True)
    otp = models.CharField(null=True, blank=True, max_length=7)
    otp_generated_time = models.DateTimeField(auto_now_add=True)
    city_name = models.CharField(max_length=100, null=True, blank=True)
    # wallet = models.OneToOneField('wallets.Wallet', null=True, blank=True, on_delete=models.SET_NULL, related_name='user_wallet')

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return f"{self.full_name} ({self.role})"

class UserNotification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_notification'
    )
    title = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"