from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^saathi_booking_response', saathi_booking_response, name='saathi_booking_response'),
    re_path(r'^saathi_login', saathi_login, name='saathi_login'),
    re_path(r'^register_saathi', register_saathi, name='register_saathi'),
    re_path(r'^verify_saathi_otp', verify_saathi_otp, name='verify_saathi_otp'),
    re_path(r'^upload_saathi_documents', upload_saathi_documents, name='upload_saathi_documents'),
    re_path(r'^update_saathi_profile', update_saathi_profile, name='update_saathi_profile'),

    *router.urls
]