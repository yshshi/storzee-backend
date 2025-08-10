from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import register,login,verify_otp,update_profile,update_profile_picture,user_details,user_notification
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^register', register, name='register'),
    re_path(r'^login', login, name='login'),
    re_path(r'^verify_otp', verify_otp, name='verify_otp'),
    re_path(r'^update_profile', update_profile, name='update_profile'),
    re_path(r'^change_profile_picture', update_profile_picture, name='update_profile_picture'),
    re_path(r'^user_details', user_details, name='user_details'),
    re_path(r'^user_notification', user_notification, name='user_notification'),


    *router.urls
]