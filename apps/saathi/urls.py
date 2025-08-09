from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^saathi_booking_response', saathi_booking_response, name='saathi_booking_response'),


    *router.urls
]