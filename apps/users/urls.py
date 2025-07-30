from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import register,login,verify_otp
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^register', register, name='register'),
    re_path(r'^login', login, name='login'),
    re_path(r'^verify_otp', verify_otp, name='verify_otp'),


    *router.urls
]