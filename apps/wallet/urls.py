from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^get_user_wallet', get_user_wallet, name='get_user_wallet'),
    re_path(r'^get_saathi_wallet', get_saathi_wallet, name='get_saathi_wallet'),



    *router.urls
]