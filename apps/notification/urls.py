# urls.py
from django.urls import path
from .views import register_token,send_notification

urlpatterns = [
    path('register_token/', register_token, name='register_token'),
    path('send_notification/', send_notification, name='send_notification'),
]
